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
import json
from qgis.core import (
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
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterString,
    QgsProcessingParameterExtent,
    QgsProcessingParameterEnum,
)
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.PyQt.QtCore import QDateTime, QUrl, QCoreApplication

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


class OccurrencesExtractionQuick(QgsProcessingAlgorithm):
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
    SPECIES_NAME = "SPECIES_NAME"
    OPTIONS = "OPTIONS"

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
        return "quickfilters"

    def displayName(self) -> str:
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return " Occurrences extraction (Quick filters)"

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
        return self.tr("Extract GBIF's occurrences based on filters using GBIF's API.\nThis processing algorithm is based on GBIF Occurrences plugin, this is the quick filters version. Only 3 filters are requested:\n- An extent\n- A species name\n- A time period")

    def initAlgorithm(self, config: Optional[dict[str, Any]] = None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.ntwk_requester = QgsBlockingNetworkRequest()

        self.addParameter(
            QgsProcessingParameterExtent(
                self.EXTENT, self.tr("Extent"),
                defaultValue=None,
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.SPECIES_NAME,
                self.tr("Species name"),
                defaultValue=None,
                multiLine=False,
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.OPTIONS,
                self.tr("Date event"),
                options=[
                    self.tr("No date filter"),
                    self.tr("Last 10 years"),
                    self.tr("Last year"),
                    self.tr("Last 6 month"),
                    self.tr("Last month"),
                    self.tr("Last week"),
                ],
                allowMultiple=False,
                defaultValue=self.tr("No date filter"),
            )
        )

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

        start_time, end_time = self.get_date_range(parameters["OPTIONS"])

        if start_time != "" and end_time != "":
            if end_time >= start_time:
                event_date = "{min},{max}".format(
                    min=str(start_time.toString("yyyy-MM-dd")),
                    max=str(end_time.toString("yyyy-MM-dd")),
                )
            else:
                feedback.reportError(
                    self.tr("Start date is greater than end date"),  # noqa: E501
                    True,
                )
                return {}
        else:
            event_date = ""

        geometry = self.get_geometry(parameters["EXTENT"], output_crs)

        filters = {
            "scientificName": parameters["SPECIES_NAME"],
            "basisOfRecord": [
                "FOSSIL_SPECIMEN",
                "HUMAN_OBSERVATION",
                "LITERATURE",
                "LIVING_SPECIMEN",
                "MACHINE_OBSERVATION",
                "MATERIAL_CITATION",
                "MATERIAL_SAMPLE",
                "OCCURRENCE",
                "OBSERVATION",
                "PRESERVED_SPECIMEN",
                "UNKNOWN",
            ],
            "eventDate": event_date,
            "geometry": geometry,
            "hasCoordinate": "true",
            "limit": __api_per_page_records__,
        }
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
            scientific_name = parameters["SPECIES_NAME"]
            layer = create_and_add_layer(project=None, name=scientific_name)

            if int(occ_count / int(__api_per_page_records__)) == 1:
                total_pages = int(occ_count / int(__api_per_page_records__))
            else:
                total_pages = (
                    int(occ_count / int(__api_per_page_records__)) + 1
                )  # noqa: E501

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

    def get_date_range(self, selection):
        if selection == 0:
            return "", ""
        else:
            end_time = QDateTime.currentDateTime()

        if selection == 1:
            day_range = -3652
        elif selection == 2:
            day_range = -365
        elif selection == 3:
            day_range = -182
        elif selection == 4:
            day_range = -31
        elif selection == 5:
            day_range = -7
        start_time = QDateTime.currentDateTime().addDays(day_range)
        return start_time, end_time     

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
