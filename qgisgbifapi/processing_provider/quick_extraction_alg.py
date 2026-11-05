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
import datetime
from typing import Any, Optional

from qgis.core import (
    QgsBlockingNetworkRequest,
    QgsFeatureSink,
    Qgis,
    QgsProcessingException,
    QgsCoordinateReferenceSystem,
    QgsProcessingAlgorithm,
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsProcessingParameterCrs,
    QgsProcessingParameterEnum,
    QgsProcessingParameterExtent,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterString,
)
from qgis.PyQt.QtCore import QDateTime, QCoreApplication

from qgisgbifapi.tool import (
    blocking_occurrence_counting,
    get_geometry,
    manage_occurrences_counting,
    _finalize_filters,
)

from qgisgbifapi.__about__ import (
    __api_crs__,
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
    SCIENTIFIC_NAME = "SCIENTIFIC_NAME"
    DATE_RANGE = "DATE_RANGE"
    CRS = "CRS"

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
        return self.tr("Extract GBIF's occurrences based on filters using GBIF's API.\nThis processing algorithm is based on GBIF Occurrences plugin, this is the quick filters version. Only 3 filters are requested:\n- An extent\n- A species scientific name\n- A time period")  # noqa: E501

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

        date_range = QgsProcessingParameterEnum(
            self.DATE_RANGE,
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
        date_range.setHelp(self.tr(
            "Select one value from the list. Every value max date is the current date. For example 'last month' date range will fetch all occurrences collected since the last 31 days."  # noqa: E501
        ))
        self.addParameter(date_range)

        crs = QgsProcessingParameterCrs(
            self.CRS,
            self.tr("Coordinate Reference System"),
            defaultValue=QgsCoordinateReferenceSystem(
                "EPSG:" + str(__api_crs__)
            ),
            optional=False
        )
        self.addParameter(crs)

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        today = datetime.datetime.now()
        year = today.year
        month = today.strftime("%m")
        day = today.strftime("%d")
        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, (
                    str(year)
                    + str(month)
                    + str(day)
                    + "_GBIF_Occurrences"
                )
            )
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
        output_crs = QgsCoordinateReferenceSystem("EPSG:" + str(__api_crs__))

        # create date range list
        start_time, end_time = self.get_date_range(parameters["DATE_RANGE"])

        # translate date range in 2 dates
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

        geometry = get_geometry(parameters["EXTENT"], output_crs)

        # create filters list
        filters = {
            "scientificName": parameters["SCIENTIFIC_NAME"],
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

        feedback.pushInfo(str(filters))

        # check occurrence number
        occ_count = blocking_occurrence_counting(
            self.ntwk_requester,
            _finalize_filters(filters)
        )

        # depending on occurrence counting, switch log message
        # if there is too much records, delete doesn't start
        layer = manage_occurrences_counting(
            self.ntwk_requester,
            occ_count,
            parameters,
            filters,
            feedback,
            self.tr
        )
        if not layer:
            return {}
        else:
            (sink, dest_id) = self.parameterAsSink(
                parameters,
                self.OUTPUT,
                context,
                layer.fields(),
                Qgis.WkbType.Point,
                parameters["CRS"],
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
