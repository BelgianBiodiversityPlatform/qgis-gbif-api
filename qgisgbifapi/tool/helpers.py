import json

from qgis.core import (
    Qgis,
    QgsApplication,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsField,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsReferencedGeometry,
    QgsReferencedRectangle,
    QgsRectangle,
    QgsProject,
)

from qgis.PyQt.QtCore import QMetaType, QVariant, QDir, QFile, QByteArray, QUrl
if Qgis.QGIS_VERSION_INT >= 40000:
    from qgis.PyQt.QtCore import QIODeviceBase
else:
    from qgis.PyQt.QtCore import QIODevice
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.PyQt.QtWidgets import QMessageBox

from qgisgbifapi.__about__ import (
    __field_list__,
    __api_crs__,
    __api_endpoint__,
    __api_max_total_records__,
    __api_occurrences_search__,
    __api_per_page_records__,
    __api_warning_threshold__,
    __combobox_all_label__,
)


class GBIFApiError(Exception):
    pass


def _get_val_or_range(min_field, max_field, error_message):
    # check if max value is bigger than min value
    try:
        max_field >= min_field
        return "{min},{max}".format(
            min=str(min_field.toString("yyyy-MM-dd")),
            max=str(max_field.toString("yyyy-MM-dd")),
        )
    except GBIFApiError as e:
        error_message("GBIF Error: " + str(e))


def _finalize_filters(filters):
    # add specific parameters to user's parameters
    fixed_filters = {
        "hasCoordinate": "true",
        "limit": __api_per_page_records__
    }
    return dict(list(filters.items()) + list(fixed_filters.items()))


def show_warning():
    """Warning message if a request is very large,
    user can choose to stop or proceed"""
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setText(
        f"The number of results is very large (> {__api_warning_threshold__}). Do you want to continue?"  # noqa: E501
    )
    msg_box.setWindowTitle("Warning")
    msg_box.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    return msg_box.exec() == QMessageBox.StandardButton.Yes


def create_and_add_layer(project, name, epsg_id):
    """Create a new memory layer, add it to the map and return it."""
    mem_layer = QgsVectorLayer(
        "Point?crs=epsg:{id}&index=true".format(id=epsg_id), name, "memory"
    )
    if project is not None:
        project.addMapLayer(mem_layer)

    return mem_layer


def add_features_to_layer(layer, features):
    layer.startEditing()
    layer.dataProvider().addFeatures(features)
    layer.commitChanges()
    layer.updateExtents()
    layer.triggerRepaint()


# To distinguish sequences from strings
def is_sequence(arg):
    return (
        not hasattr(arg, "strip")
        and hasattr(arg, "__getitem__")
        or hasattr(arg, "__iter__")
    )


# Takes data and return a string suitable for a (feature) attribute
# It will be either a standard string, either a serialized JSON object
# in case of complex structure
def _get_field_value(o, field_name):
    value = o[field_name]

    if value:
        if is_sequence(value):  # Case 1: It's a list/dict
            return json.dumps(value, ensure_ascii=False)
        else:  # Case 2: It's a string
            return value
    else:  # Case 3: missing value
        return ""


def add_gbif_occ_to_layer(project, occurrences, layer, minimal_mode, export_crs):  # noqa: E501
    # create empty list of feature
    features = []
    dp = layer.dataProvider()
    # create attribute based on fetched data
    for o in occurrences:
        attrs = []
        if dp.fieldNameIndex("gbif_url") == -1:
            if Qgis.QGIS_VERSION_INT >= 33800:
                dp.addAttributes([QgsField("gbif_url", QMetaType.Type(10))])
            else:
                dp.addAttributes([QgsField("gbif_url", QVariant.String)])
        for k in list(o.keys()):
            if (minimal_mode is True and k in __field_list__) or not minimal_mode:  # noqa: E501
                field_index = dp.fieldNameIndex(k)
                # Add a layer attribute for each JSON fields
                # (if not already encountered)
                if field_index == -1:
                    if Qgis.QGIS_VERSION_INT >= 33800:
                        dp.addAttributes([QgsField(k, QMetaType.Type(10))])
                    else:
                        dp.addAttributes([QgsField(k, QVariant.String)])

                attrs.append({"attr": k, "val": _get_field_value(o, k)})
            else:
                continue

        feat = QgsFeature()

        # We should tell the feature which will be its fields
        # !! We need a variable !! Don't merge the next two lines !!
        myFields = dp.fields()
        feat.setFields(myFields)

        for d in attrs:
            try:
                feat.setAttribute(d["attr"], d["val"].strip('"'))
            except AttributeError:
                feat.setAttribute(d["attr"], d["val"])

        feat.setAttribute("gbif_url", "https://www.gbif.org/fr/occurrence/" + str(feat["key"]))  # noqa: E501
        geom = QgsGeometry.fromPointXY(
            QgsPointXY(o["decimalLongitude"], o["decimalLatitude"])
        )
        geom.transform(
            QgsCoordinateTransform(
                QgsCoordinateReferenceSystem("EPSG:" + str(__api_crs__)),
                export_crs,
                project,
            )
        )
        feat.setGeometry(geom)

        features.append(feat)
    add_features_to_layer(layer, features)


def create_url(params):
    # create base url for request
    request_url = __api_endpoint__ + __api_occurrences_search__ + "?"
    # add every parameters to base url
    for param in params:
        if isinstance(params[param], list):
            for elem in params[param]:
                request_url = request_url + str(param) + "=" + str(elem) + "&"  # noqa: E501
        elif params[param] == "":
            pass
        elif params[param] is None:
            pass
        else:
            request_url = request_url + str(param) + "=" + str(params[param]) + "&"  # noqa: E501
    # remove last character of url, either ? or &
    return request_url[:-1]


def calculate_pages(occ_count, record_per_page):
    # calculate number of pages needed to download all records
    if int(occ_count / int(record_per_page)) == 1:
        total_pages = int(occ_count / int(record_per_page))
    else:
        total_pages = (
            int(occ_count / int(record_per_page)) + 1
        )
    return total_pages


def get_countries():
    # find country list in QGIS metadata file to build a dictionnary
    # country name as key and alpha code 2 as value, a list is also built
    # with only the countries name
    countries_dict = {}
    countries_dict[__combobox_all_label__] = ""
    path = QDir(QgsApplication.metadataPath()).absoluteFilePath(
        "country_code_ISO_3166.csv"
    )
    file = QFile(path)
    if Qgis.QGIS_VERSION_INT >= 40000:
        open_mode = QIODeviceBase.OpenModeFlag.ReadOnly
    else:
        open_mode = open_mode = QIODevice.ReadOnly
    if not file.open(open_mode):
        print(
            "Error while opening the CSV file: {}, {} ".format(
                path,
                file.errorString()
            )
        )
        return countries_dict

    file.readLine()
    while not file.atEnd():
        line = file.readLine()
        items = line.split(QByteArray(",".encode()))
        if len(items) > 9:
            name = (
                items[0].trimmed().data().decode()
                + " "
                + items[1].trimmed().data().decode()
            )
            alpha2 = items[2].trimmed().data().decode()
        else:
            name = items[0].trimmed().data().decode()
            alpha2 = items[1].trimmed().data().decode()
        countries_dict[name.strip('"')] = alpha2
    file.close()
    return countries_dict


def get_geometry(extent, output_crs):
    if extent is not None:
        point_list = extent.split(" ")[0]
        crs = extent.split(" ")[1][1:-1]
        xmin = point_list.split(",")[0]
        xmax = point_list.split(",")[1]
        ymin = point_list.split(",")[2]
        ymax = point_list.split(",")[3]
        rect = QgsRectangle()
        rect.setXMaximum(float(xmax))
        rect.setXMinimum(float(xmin))
        rect.setYMaximum(float(ymax))
        rect.setYMinimum(float(ymin))
        extent = QgsReferencedGeometry().fromReferencedRect(
            QgsReferencedRectangle(rect, QgsCoordinateReferenceSystem(crs))
        )
        extent.transform(
            QgsCoordinateTransform(
                QgsCoordinateReferenceSystem(str(crs)),
                output_crs,
                QgsProject.instance(),
            )
        )
        return extent.boundingBox().asWktPolygon()
    else:
        return ""


def blocking_occurrence_counting(ntwk_requester, params):
    params["offset"] = 0
    request_url = create_url(params)
    request = QNetworkRequest(QUrl(request_url))
    request.setRawHeader(
        b"User-Agent",
        bytes("QGIS Plugin GBIF Occurrences", encoding="utf-8"),  # noqa: E501
    )
    request.setHeader(
        QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json"
    )  # noqa: E501
    ntwk_requester.get(
        request=request,
        forceRefresh=False,
    )
    req_reply = ntwk_requester.reply()
    # Decode data fetch from the get request and create a dictionnary.
    data_request = req_reply.content().data().decode()
    res = json.loads(data_request)
    # Get the observation number in the extent based on filters.
    nb_obs = res["count"]
    return nb_obs


def blocking_batch_request(ntwk_requester, layer, params, parameters):
    request_url = create_url(params)
    request = QNetworkRequest(QUrl(request_url))
    request.setRawHeader(
        b"User-Agent",
        bytes("QGIS Plugin GBIF Occurrences", encoding="utf-8"),  # noqa: E501
    )
    request.setHeader(
        QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json"
    )  # noqa: E501
    ntwk_requester.get(
        request=request,
        forceRefresh=False,
    )
    req_reply = ntwk_requester.reply()
    # Decode data fetch from the get request and create a dictionnary.
    data_request = req_reply.content().data().decode()
    res = json.loads(data_request)
    try:
        add_gbif_occ_to_layer(
            QgsProject.instance(),
            res["results"],
            layer,
            False,
            parameters["CRS"]
        )
    except TypeError:
        print(res["results"])


def manage_occurrences_counting(ntwk_requester, occ_count, parameters, filters, feedback, translation):  # noqa: E501
    # depending on occurrence number, we continue the process or not
    # Too much result
    if occ_count > int(__api_max_total_records__):
        feedback.reportError(
            translation("The query returned more than ")
            + str(__api_max_total_records__)
            + translation(" records. Due to limitations in the GBIF infrastructure, very large queries are currently not supported."),  # noqa: E501
            True,
        )
        return None
    # Not too much but more than 0 result
    elif occ_count > 0:
        feedback.pushInfo(
            translation("The query returned ")
            + str(occ_count)
            + translation(" records.")
        )
        # Warning if there is a lot of records
        if occ_count > int(__api_warning_threshold__):
            feedback.pushWarning(
                translation("The number of records is very large (> ")
                + str(__api_warning_threshold__)
                + translation("). It may takes some times")
            )
        scientific_name = parameters["SCIENTIFIC_NAME"]
        layer = create_and_add_layer(
            project=None,
            name=scientific_name,
            epsg_id=parameters["CRS"].postgisSrid()
        )

        total_pages = calculate_pages(
            int(occ_count),
            int(__api_per_page_records__)
        )

        for page in range(total_pages):
            filters["offset"] = int(page) * int(__api_per_page_records__)
            blocking_batch_request(
                ntwk_requester,
                layer,
                filters,
                parameters
            )
            # Update the progress bar
            feedback.setProgress(int(int(page) / total_pages))
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
        return layer
    # No result
    else:
        feedback.reportError(
            translation("The query didn't returned record."),
            True,
        )
        return None
