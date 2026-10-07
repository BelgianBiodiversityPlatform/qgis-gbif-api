"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from typing import Any, Optional
from operator import itemgetter
import json
from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsCoordinateTransform,
    QgsReferencedGeometry,
    QgsBlockingNetworkRequest,
    QgsFeatureSink,
    QgsVectorLayer,
    QgsReferencedRectangle,
    QgsRectangle,
    Qgis,
    QgsProcessingException,
    QgsCoordinateReferenceSystem,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterDateTime,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterNumber,
    QgsProcessingParameterString,
    QgsProcessingParameterExtent,
    QgsProcessingParameterEnum,
)
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.PyQt.QtCore import (
    QDateTime,
    QUrl,
    QCoreApplication,
    QDir,
    QFile,
    QByteArray,
    QIODevice,
)

if Qgis.QGIS_VERSION_INT >= 40000:
    from qgis.PyQt.QtCore import QIODeviceBase

from qgisgbifapi.tool import (
    create_and_add_layer,
    _finalize_filters,
    add_gbif_occ_to_layer,
)

from qgisgbifapi.__about__ import (
    __api_endpoint__,
    __api_occurrences_search__,
    __api_max_total_records__,
    __api_warning_threshold__,
    __api_per_page_records__,
)

COMBOBOX_ALL_LABEL = "-- All --"


def get_countries():
    countries = []
    countries_dict = {}
    countries.append(COMBOBOX_ALL_LABEL)
    countries_dict[COMBOBOX_ALL_LABEL] = ""
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
        return countries, countries_dict

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
        countries.append(name.strip('"'))
        countries_dict[name.strip('"')] = alpha2
    file.close()
    return countries, countries_dict


countries, countries_dict = get_countries()
BOR = {
    "Fossilized specimen": "FOSSIL_SPECIMEN",
    "Human observation": "HUMAN_OBSERVATION",
    "Literature": "LITERATURE",
    "Living specimen": "LIVING_SPECIMEN",
    "Machine observation": "MACHINE_OBSERVATION",
    "Material citation": "MATERIAL_CITATION",
    "Material sample": "MATERIAL_SAMPLE",
    "Occurrence": "OCCURRENCE",
    "Observation": "OBSERVATION",
    "Preserved specimen": "PRESERVED_SPECIMEN",
    "Unknown": "UNKNOWN",
}
default_bor = []
n = 0
for elem in BOR:
    default_bor.append(n)
    n = n + 1


class OccurrencesExtractionComplete(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = "OUTPUT"
    EXTENT = "EXTENT"
    COUNTRY = "COUNTRY"
    GADM_CODE = "GADM_CODE"
    SCIENTIFIC_NAME = "SCIENTIFIC_NAME"
    SPECIES_KEY = "SPECIES_KEY"
    BASIS_OF_RECORD = "BASIS_OF_RECORD"
    CATALOG_NUMBER = "CATALOG_NUMBER"
    RECORDED_BY = "RECORDED_BY"
    PUBLISHING_COUNTRY = "PUBLISHING_COUNTRY"
    INSTITUTION_CODE = "INSTITUTION_CODE"
    COLLECTION_CODE = "COLLECTION_CODE"
    DATASET_KEY = "DATASET_KEY"
    START_DATE = "START_DATE"
    END_DATE = "END_DATE"

    def tr(self, message: str) -> str:
        """Get the translation for a string using Qt translation API.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: str
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GBIFOccurrences', message)

    def name(self) -> str:
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return "completefilters"

    def displayName(self) -> str:
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return " Occurrences extraction (Complete filters)"

    def group(self) -> str:
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return ""

    def groupId(self) -> str:
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ""

    def shortHelpString(self) -> str:
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and
        the parameters and outputs associated with it.
        """
        return self.tr("Extract GBIF's occurrences based on filters using GBIF's API.\nThis processing algorithm is based on GBIF Occurrences plugin, this is the complete filters version.  filters are requested:\n- An extent or a country with a possible GADM identifier, if both are completed, only the extent will be prioritized. \n- A species scientific name or a taxon key, if both are specified, taxon key is prioritized\n- A time period, with two date\n- A list of basis of record\n- A catalog number\n- A recorder name\n- A publishing country\n- An institution code\n- A collection code\n- A dataset key")  # noqa: E501

    def initAlgorithm(self, config: Optional[dict[str, Any]] = None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.ntwk_requester = QgsBlockingNetworkRequest()

        extent = QgsProcessingParameterExtent(
                self.EXTENT, self.tr("Extent"),
                defaultValue=None,
                optional=True,
        )
        extent.setHelp(self.tr(
            "Searches for occurrences inside an extent."
        ))
        self.addParameter(extent)

        country = QgsProcessingParameterEnum(
                self.COUNTRY, self.tr("Country"),
                defaultValue=COMBOBOX_ALL_LABEL,
                optional=True,
                options=countries,
            )

        country.setHelp(self.tr(
            "The country in which the occurrence was recorded."
        ))
        self.addParameter(country)

        gadm = QgsProcessingParameterString(
                self.GADM_CODE,
                self.tr("GADM.org Area Code"),
                defaultValue=None,
                multiLine=False,
                optional=True,
            )
        gadm.setHelp(self.tr(
            "A GADM geographic identifier at any level,<br>for example AGO, AGO.1_1, AGO.1.1_1 or AGO.1.1.1_1"  # noqa: E501
        ))
        self.addParameter(gadm)

        species = QgsProcessingParameterString(
                self.SCIENTIFIC_NAME,
                self.tr("Scientific name"),
                defaultValue=None,
                multiLine=False,
                optional=True,
            )
        species.setHelp(self.tr(
            "A scientific name from the GBIF backbone or the specified checklist (see checklistKey parameter). All included and synonym taxa are included in the search. Under the hood a call to the species match service is done first to retrieve a taxonKey. Only unique scientific names will return results, homonyms (many monomials) return nothing! Consider to use the taxonKey parameter instead and the species match service directly."  # noqa: E501
        ))
        self.addParameter(species)

        species_key = QgsProcessingParameterNumber(
                self.SPECIES_KEY,
                self.tr("Taxon key"),
                defaultValue=None,
                type=Qgis.ProcessingNumberParameterType.Integer,
                optional=True,
                minValue=0,
                maxValue=999999999,
            )
        species_key.setHelp(self.tr(
                'This is the primary id used to identify a taxon, "0" means this filter is not used.<br><b>Must be an integer</b>'  # noqa: E501
        ))
        self.addParameter(species_key)

        start_date = QgsProcessingParameterDateTime(
                self.START_DATE,
                self.tr("Start date"),
                type=Qgis.ProcessingDateTimeParameterDataType.Date,
                defaultValue=None,
                optional=True,
                maxValue=QDateTime.currentDateTime(),
                minValue=QDateTime.fromString('1500-01-01', "yyyy-MM-dd"),
            )
        start_date.setHelp(self.tr(
            "Minimum occurrence date. If not filled but End date is filled, Start date will be '1500-01-01'.<br><b>Must be smaller than End date</b>"  # noqa: E501
        ))
        self.addParameter(start_date)

        end_date = QgsProcessingParameterDateTime(
                self.END_DATE,
                self.tr("End date"),
                type=Qgis.ProcessingDateTimeParameterDataType.Date,
                defaultValue=None,
                optional=True,
                maxValue=QDateTime.currentDateTime(),
                minValue=QDateTime.fromString('1500-01-01', "yyyy-MM-dd"),
            )
        end_date.setHelp(self.tr(
            "Maximum occurrence date. If not filled but Start date is filled, End date will be current date.<br><b>Must be greater than Start date</b>"  # noqa: E501
        ))
        self.addParameter(end_date)

        bor = QgsProcessingParameterEnum(
                self.BASIS_OF_RECORD,
                self.tr("Basis of record"),
                defaultValue=default_bor,
                optional=True,
                allowMultiple=True,
                options=BOR,
            )

        bor.setHelp(self.tr(
            "Basis of record is a Darwin Core term that refers to the specific nature of the record."  # noqa: E501
        ))
        self.addParameter(bor)

        catalog_key = QgsProcessingParameterString(
                self.CATALOG_NUMBER,
                self.tr("Catalog number"),
                defaultValue=None,
                multiLine=False,
                optional=True,
            )
        catalog_key.setHelp(self.tr(
            "An identifier of any form assigned by the source within a physical collection or digital dataset for the record which may not be unique,<br>but should be fairly unique in combination with the institution and collection code."  # noqa: E501
        ))
        self.addParameter(catalog_key)

        recorder = QgsProcessingParameterString(
                self.RECORDED_BY,
                self.tr("Recorded by"),
                defaultValue=None,
                multiLine=False,
                optional=True,
            )
        recorder.setHelp(self.tr(
            "The person who recorded the occurrence."
        ))
        self.addParameter(recorder)

        pub_country = QgsProcessingParameterEnum(
                self.PUBLISHING_COUNTRY, self.tr("Publishing country"),
                defaultValue=COMBOBOX_ALL_LABEL,
                optional=True,
                options=countries,
            )

        pub_country.setHelp(self.tr(
            "The owning organization's country."
        ))
        self.addParameter(pub_country)

        institution = QgsProcessingParameterString(
                self.INSTITUTION_CODE,
                self.tr("Institution code"),
                defaultValue=None,
                multiLine=False,
                optional=True,
            )
        institution.setHelp(self.tr(
            "An identifier of any form assigned by the source to<br>identify the institution the record belongs to.<br>Not guaranteed to be unique."  # noqa: E501
        ))
        self.addParameter(institution)

        collection = QgsProcessingParameterString(
                self.COLLECTION_CODE,
                self.tr("Collection code"),
                defaultValue=None,
                multiLine=False,
                optional=True,
            )
        collection.setHelp(self.tr(
            "An identifier of any form assigned by the source to<br>identify the physical collection or digital dataset uniquely<br>within the context of an institution."  # noqa: E501
        ))
        self.addParameter(collection)

        dataset = QgsProcessingParameterString(
                self.DATASET_KEY,
                self.tr("Dataset key"),
                defaultValue=None,
                multiLine=False,
                optional=True,
            )
        dataset.setHelp(self.tr(
            "The occurrence dataset key (a UUID)."
        ))
        self.addParameter(dataset)

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, "GBIF Occurrences")
        )

    def processAlgorithm(
        self,
        parameters: dict[str, Any],
        context: QgsProcessingContext,
        feedback: QgsProcessingFeedback,
    ) -> dict[str, Any]:
        """
        Here is where the processing itself takes place.
        """
        output_crs = QgsCoordinateReferenceSystem("EPSG:4326")

        if parameters["START_DATE"] is not None and parameters["END_DATE"] is not None:  # noqa: E501
            if parameters["END_DATE"] >= parameters["START_DATE"]:
                event_date = "{min},{max}".format(
                    min=str(parameters["START_DATE"].toString("yyyy-MM-dd")),
                    max=str(parameters["END_DATE"].toString("yyyy-MM-dd")),
                )
            else:
                feedback.reportError(
                    self.tr("Start date is greater than End date"),  # noqa: E501
                    True,
                )
                return {}
        elif parameters["START_DATE"] is not None:
            event_date = "{min},{max}".format(
                min=str(parameters["START_DATE"].toString("yyyy-MM-dd")),
                max=str(QDateTime.currentDateTime().toString("yyyy-MM-dd")),
            )
        elif parameters["END_DATE"] is not None:
            event_date = "{min},{max}".format(
                min=str(QDateTime.fromString('1752-09-14', "yyyy-MM-dd").toString("yyyy-MM-dd")),  # noqa: E501
                max=str(parameters["END_DATE"].toString("yyyy-MM-dd")),
            )
        else:
            event_date = ""

        geometry = self.get_geometry(parameters["EXTENT"], output_crs)
        if geometry is not None:
            filters = {
                "scientificName": parameters["SCIENTIFIC_NAME"],
                "basisOfRecord": list(
                    itemgetter(*parameters["BASIS_OF_RECORD"])(
                        list(BOR.values())
                    )
                ),
                "catalogNumber": parameters["CATALOG_NUMBER"],
                "publishingCountry": list(
                    countries_dict.values()
                )[parameters["PUBLISHING_COUNTRY"]],
                "institutionCode": parameters["INSTITUTION_CODE"],
                "collectionCode": parameters["COLLECTION_CODE"],
                "eventDate": event_date,
                "taxonKey": parameters["SPECIES_KEY"],
                "datasetKey": parameters["DATASET_KEY"],
                "recordedBy": parameters["RECORDED_BY"],
                "geometry": geometry,
                "hasCoordinate": "true",
                "limit": __api_per_page_records__,
            }
        else:
            filters = {
                "scientificName": parameters["SCIENTIFIC_NAME"],
                "basisOfRecord": list(
                    itemgetter(*parameters["BASIS_OF_RECORD"])(
                        list(BOR.values())
                    )
                ),
                "catalogNumber": parameters["CATALOG_NUMBER"],
                "publishingCountry": list(
                    countries_dict.values()
                )[parameters["PUBLISHING_COUNTRY"]],
                "institutionCode": parameters["INSTITUTION_CODE"],
                "collectionCode": parameters["COLLECTION_CODE"],
                "eventDate": event_date,
                "taxonKey": parameters["SPECIES_KEY"],
                "datasetKey": parameters["DATASET_KEY"],
                "recordedBy": parameters["RECORDED_BY"],
                "country": list(
                    countries_dict.values()
                )[parameters["COUNTRY"]],
                "gadm_gid": parameters["GADM_CODE"],
                "hasCoordinate": "true",
                "limit": __api_per_page_records__,
            }

        feedback.pushInfo(str(filters))

        occ_count = self.occurrence_counting(_finalize_filters(filters))

        layer = QgsVectorLayer()
        if occ_count > int(__api_max_total_records__):
            feedback.reportError(
                self.tr("The query returned more than ")
                + str(__api_max_total_records__)
                + self.tr(" records. Due to limitations in the GBIF infrastructure, very large queries are currently not supported."),  # noqa: E501
                True,
            )
            return {}
        elif occ_count > 0:  # We have results
            feedback.pushInfo(
                self.tr("The query returned ")
                + str(occ_count)
                + self.tr(" records.")
            )
            if occ_count > int(__api_warning_threshold__):
                feedback.pushWarning(
                    self.tr("The number of records is very large (> ")
                    + str(__api_warning_threshold__)
                    + self.tr("). It may takes some times")
                )
            scientific_name = parameters["SCIENTIFIC_NAME"]
            layer = create_and_add_layer(project=None, name=scientific_name)

            if int(occ_count / int(__api_per_page_records__)) == 1:
                total_pages = int(occ_count / int(__api_per_page_records__))
            else:
                total_pages = (
                    int(occ_count / int(__api_per_page_records__)) + 1
                )

            for page in range(total_pages):
                filters["offset"] = int(page) * int(__api_per_page_records__)
                self.batch_request(layer, filters)
                # Update the progress bar
                feedback.setProgress(int(int(page) / total_pages))
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    break
        else:
            feedback.reportError(
                self.tr("The query didn't returned record."),
                True,
            )
            return {}

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            layer.fields(),
            Qgis.WkbType.Point,
            output_crs,
        )

        # If sink was not created, throw an exception to indicate that
        # the algorithm encountered a fatal error. The exception text
        # can be any string, but in this case we use the pre-built
        # invalidSinkError method to return a standard helper text
        # for when a sink cannot be evaluated
        if sink is None:
            raise QgsProcessingException(
                self.invalidSinkError(parameters, self.OUTPUT)
            )

        for f in layer.getFeatures():
            sink.addFeature(f, QgsFeatureSink.FastInsert)

        return {self.OUTPUT: dest_id}

    def createInstance(self):
        return self.__class__()

    def get_geometry(self, extent, output_crs):
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

    def create_url(self, params):
        request_url = __api_endpoint__ + __api_occurrences_search__ + "?"
        for param in params:
            if isinstance(params[param], list):
                for elem in params[param]:
                    request_url = (
                        request_url + str(param) + "=" + str(elem) + "&"
                    )  # noqa: E501
            elif params[param] == "":
                pass
            elif params[param] is None:
                pass
            else:
                request_url = (
                    request_url + str(param) + "=" + str(params[param]) + "&"
                )  # noqa: E501
        return request_url[:-1]

    def occurrence_counting(self, params):
        params["offset"] = 0
        request_url = self.create_url(params)
        request = QNetworkRequest(QUrl(request_url))
        request.setRawHeader(
            b"User-Agent",
            bytes("QGIS Plugin GBIF Occurrences", encoding="utf-8"),  # noqa: E501
        )
        request.setHeader(
            QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json"
        )  # noqa: E501
        self.ntwk_requester.get(
            request=request,
            forceRefresh=False,
        )
        req_reply = self.ntwk_requester.reply()
        # Decode data fetch from the get request and create a dictionnary.
        data_request = req_reply.content().data().decode()

        res = json.loads(data_request)
        # Get the observation number in the extent based on filters.
        nb_obs = res["count"]
        return nb_obs

    def batch_request(self, layer, params):
        request_url = self.create_url(params)
        request = QNetworkRequest(QUrl(request_url))
        request.setRawHeader(
            b"User-Agent",
            bytes("QGIS Plugin GBIF Occurrences", encoding="utf-8"),  # noqa: E501
        )
        request.setHeader(
            QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json"
        )  # noqa: E501
        self.ntwk_requester.get(
            request=request,
            forceRefresh=False,
        )
        req_reply = self.ntwk_requester.reply()
        # Decode data fetch from the get request and create a dictionnary.
        data_request = req_reply.content().data().decode()
        res = json.loads(data_request)
        try:
            add_gbif_occ_to_layer(res["results"], layer)
        except TypeError:
            print(res["results"])
