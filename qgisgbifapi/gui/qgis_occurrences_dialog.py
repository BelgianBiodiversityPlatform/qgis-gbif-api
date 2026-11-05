# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GBIFOccurrencesDialog
                                 A QGIS plugin
 Retrieve data from GBIF webservices (occurrences API) directly within QGIS.
                             -------------------
        begin                : 2014-11-18
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Nicolas Noé - Belgian Biodiversity Platform  # noqa: E501
        email                : n.noe@biodiversity.be
 ***************************************************************************/

"""
from builtins import str
import datetime
import os

from qgis.core import (
    QgsGeometry,
    QgsCoordinateReferenceSystem,
)
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QApplication, QMessageBox, QDialog
from qgis.PyQt.QtCore import QDate, Qt

from qgisgbifapi.tool import (
    calculate_pages,
    get_countries,
    GBIFApiError,
    RectangleDrawTool,
    create_and_add_layer,
    CountRequest,
    BatchRequest,
    _finalize_filters,
    _get_val_or_range,
    show_warning,
)

from qgisgbifapi.__about__ import (
    __api_crs__,
    __api_max_total_records__,
    __api_warning_threshold__,
    __api_per_page_records__,
)

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "qgis_occurrences_dialog_base.ui")
)


countries_dict = get_countries()


def _populate_country_field(combobox):
    for country in countries_dict:
        combobox.addItem(country)


def _get_selected_country_code(combobox):
    for country in countries_dict:
        if combobox.currentText() == country:
            return countries_dict[country]
    # Not found
    return None


class GBIFOccurrencesDialog(QDialog, FORM_CLASS):
    # Key: UI label
    # Value: GBIF filter constants, see
    # http://gbif.github.io/gbif-api/apidocs/org/gbif/api/vocabulary/BasisOfRecord.html
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

    def __init__(
        self,
        parent=None,
        project=None,
        iface=None,
        manager=None
    ):
        """Constructor."""
        super(GBIFOccurrencesDialog, self).__init__(parent)
        self.project = project
        self.iface = iface
        self.manager = manager
        self.canvas = self.iface.mapCanvas()

        self.count_request = CountRequest(dlg=self, manager=self.manager)
        self.batch_request = BatchRequest(
            manager=self.manager,
            dlg=self,
            project=self.project,
        )
        self.count_request.finished_dl.connect(self.count_results)
        self.batch_request.finished_dl.connect(self.occurrences_results)

        self.setupUi(self)
        self.setFixedSize(self.size())

        self._populate_bor()
        self._populate_countries()
        self._populate_publishing_countries()
        self.set_rectangle_tool()

        self.minDateEdit.setDate(QDate.currentDate())
        self.maxDateEdit.setDate(QDate.currentDate())

        # Widget tooltip
        self.taxonKeyField.setToolTip(
            self.tr(
                'This is the primary id used to identify a taxon, "0" means this filter is not used.<br><b>Must be an integer</b>. If both a species name and a taxon key are specified, taxon key will be prioritized.'  # noqa: E501
            )
        )
        self.basisComboBox.setToolTip(
            self.tr(
                "Basis of record is a Darwin Core term that refers to the specific nature of the record."  # noqa: E501
            )
        )
        self.catalogNumberField.setToolTip(
            self.tr(
                "An identifier of any form assigned by the source within a physical collection or digital dataset for the record which may not be unique,<br>but should be fairly unique in combination with the institution and collection code."  # noqa: E501
            )
        )
        self.recordedByField.setToolTip(
            self.tr(
                "The person who recorded the occurrence."
            )
        )
        self.gadmGidField.setToolTip(
            self.tr(
                "A GADM geographic identifier at any level,<br>for example AGO, AGO.1_1, AGO.1.1_1 or AGO.1.1.1_1"  # noqa: E501
            )
        )
        self.institutionCodeField.setToolTip(
            self.tr(
                "An identifier of any form assigned by the source to<br>identify the institution the record belongs to.<br>Not guaranteed to be unique."  # noqa: E501
            )
        )
        self.collectionCodeField.setToolTip(
            self.tr(
                "An identifier of any form assigned by the source to<br>identify the physical collection or digital dataset uniquely<br>within the context of an institution."  # noqa: E501
            )
        )
        self.datasetKeyField.setToolTip(
            self.tr("The occurrence dataset key (a UUID).")
        )

        # Crs selection widget
        self.crs_selection.setCrs(
            QgsCoordinateReferenceSystem("EPSG:" + str(__api_crs__))
        )

        # signal to adapt ui based on user selection
        self.bboxCheckBox.clicked.connect(self.localisation_selection_ui)
        self.boundariesCheckBox.clicked.connect(self.localisation_selection_ui)
        self.dateCheckBox.clicked.connect(self.date_selection_ui)

        # signal to use specific tool, extent pointer
        self.bboxButton.clicked.connect(self.pointer)

        # signal to launch and stop algorithm
        self.loadButton.clicked.connect(self.load_occurrences)
        self.stop = False
        self.stopButton.clicked.connect(self.clicked_stop_button)

    def showEvent(self, event):
        # recreate the previous extent rubber band when the dialog is re-open
        self.recreate_rubber_band()

    def closeEvent(self, event):
        # remove extent rubber band when the dialog is closed
        self.erase_rubber_band()
        self.canvas.unsetMapTool(self.rectangle_tool)

    def clicked_stop_button(self):
        self.stop = True

    def _populate_countries(self):
        _populate_country_field(self.countryComboBox)

    def _populate_publishing_countries(self):
        _populate_country_field(self.publishingCountryComboBox)

    def _populate_bor(self):
        for elem in self.BOR:
            self.basisComboBox.addItemWithCheckState(
                text=elem, state=Qt.CheckState.Checked, userData=self.BOR[elem]
            )

    def _disable_controls(self):
        self.toolBox.setDisabled(True)

    def _enable_controls(self):
        self.toolBox.setDisabled(False)

    def dialog_too_many_results(self):
        msg = self.tr("""The query returned more than {max} records.\n\
            Due to limitations in the GBIF infrastructure,\n\
            very large queries are currently not supported.""").format(
            max=__api_max_total_records__
        )
        QMessageBox.information(self, "Error", msg)

    def before_search_ui(self):
        self._disable_controls()
        self.stopButton.setDisabled(False)

    def after_search_ui(self):
        self.stopButton.setDisabled(True)
        self._enable_controls()

        self.localisation_selection_ui()

        # Theose have been affected during search
        self.progressBar.setValue(0)
        self.loadingLabel.setText("")

    def show_progress(self, already_loaded_records, total_records):
        self.loadingLabel.setText(
            self.tr("Adding ") + str(already_loaded_records) + "/" + str(total_records)  # noqa: E501
        )
        percent = (already_loaded_records / float(total_records)) * 100
        self.progressBar.setValue(int(percent))

    def connection_error_message(self):
        self.error_message(
            self.tr(
                "Cannot connect to GBIF. Please check your Internet connection."  # noqa: E501
            )
        )

    def error_message(self, msg):
        QMessageBox.critical(self, self.tr("Error"), msg)

    def _ui_to_filters(self):
        # switch ui widget selection to filter value to make the request
        # date calculation
        if self.dateCheckBox.isChecked():
            event_date = _get_val_or_range(
                self.minDateEdit.date(),
                self.maxDateEdit.date(),
                self.error_message,
            )
        else:
            event_date = ""
        # create dictionnary filters based on geometry or admin boundaries
        if not self.bboxCheckBox.isChecked():
            return {
                "scientificName": (
                    self.scientificNameField.text()
                    if self.taxonKeyField.value() == 0
                    else ""
                ),
                "basisOfRecord": self.basisComboBox.checkedItemsData(),
                "country": _get_selected_country_code(self.countryComboBox),
                "catalogNumber": self.catalogNumberField.text(),
                "publishingCountry": _get_selected_country_code(
                    self.publishingCountryComboBox
                ),
                "institutionCode": self.institutionCodeField.text(),
                "collectionCode": self.collectionCodeField.text(),
                "eventDate": event_date,
                "taxonKey": (
                    str(self.taxonKeyField.value())
                    if self.taxonKeyField.value() != 0
                    else ""
                ),
                "datasetKey": self.datasetKeyField.text(),
                "recordedBy": self.recordedByField.text(),
                "gadm_gid": self.gadmGidField.text(),
            }
        else:
            try:
                self.rectangle_tool.new_extent.asWktPolygon()
                return {
                    "scientificName": (
                        self.scientificNameField.text()
                        if self.taxonKeyField.value() == 0
                        else ""
                    ),
                    "basisOfRecord": self.basisComboBox.checkedItemsData(),
                    "catalogNumber": self.catalogNumberField.text(),
                    "publishingCountry": _get_selected_country_code(
                        self.publishingCountryComboBox
                    ),
                    "institutionCode": self.institutionCodeField.text(),
                    "collectionCode": self.collectionCodeField.text(),
                    "eventDate": event_date,
                    "taxonKey": (
                        str(self.taxonKeyField.value())
                        if self.taxonKeyField.value() != 0
                        else ""
                    ),
                    "datasetKey": self.datasetKeyField.text(),
                    "recordedBy": self.recordedByField.text(),
                    "geometry": self.rectangle_tool.new_extent.asWktPolygon(),
                }
            except AttributeError:
                return {
                    "scientificName": self.scientificNameField.text(),
                    "basisOfRecord": self.basisComboBox.checkedItemsData(),
                    "catalogNumber": self.catalogNumberField.text(),
                    "publishingCountry": _get_selected_country_code(
                        self.publishingCountryComboBox
                    ),
                    "institutionCode": self.institutionCodeField.text(),
                    "collectionCode": self.collectionCodeField.text(),
                    "eventDate": event_date,
                    "taxonKey": (
                        str(self.taxonKeyField.value())
                        if self.taxonKeyField.value() != 0
                        else ""
                    ),
                    "datasetKey": self.datasetKeyField.text(),
                    "recordedBy": self.recordedByField.text(),
                }

    def localisation_selection_ui(self):
        if self.boundariesCheckBox.isChecked():
            self.countryComboBox.setDisabled(False)
            self.gadmGidField.setDisabled(False)
            self.bboxButton.setDisabled(True)
            # Remove rectangle from map
            self.erase_rubber_band()
            # Remove the map tool to draw the rectangle
            self.canvas.unsetMapTool(self.rectangle_tool)
        else:
            self.countryComboBox.setDisabled(True)
            self.countryComboBox.setCurrentIndex(0)
            self.gadmGidField.setDisabled(True)
            self.gadmGidField.clear()
            self.bboxButton.setDisabled(False)
            self.recreate_rubber_band()

    def date_selection_ui(self):
        if self.dateCheckBox.isChecked():
            self.minDateEdit.setDisabled(False)
            self.maxDateEdit.setDisabled(False)
        else:
            self.minDateEdit.setDisabled(True)
            self.maxDateEdit.setDisabled(True)

    def erase_rubber_band(self):
        # Erase the drawn rectangle
        if self.rectangle_tool.rubber_band:
            self.rectangle_tool.rubber_band.reset()
        else:
            pass

    def recreate_rubber_band(self):
        # check if a rubber band already exists
        if (
            self.rectangle_tool.new_extent
            and self.rectangle_tool.rubber_band.numberOfVertices() == 0
        ):
            # we need to recreate it on the map in the right crs
            extent_api_crs = self.rectangle_tool.new_extent
            if str(self.project.instance().crs().postgisSrid()) != str(__api_crs__):  # noqa: E501
                geom = self.rectangle_tool.transform_geom(
                    QgsGeometry().fromRect(extent_api_crs),
                    QgsCoordinateReferenceSystem("EPSG:" + str(__api_crs__)),
                    self.project.instance().crs(),
                )
            else:
                geom = QgsGeometry().fromRect(extent_api_crs)
            self.rectangle_tool.rubber_band.setToGeometry(geom)
            self.rectangle_tool.rubber_band.show()
        else:
            pass

    def pointer(self):
        # Add the tool to draw a rectangle
        self.showMinimized()
        self.iface.mainWindow().activateWindow()
        self.canvas.setMapTool(self.rectangle_tool)

    def set_rectangle_tool(self):
        self.rectangle_tool = RectangleDrawTool(self.project, self.canvas)
        self.rectangle_tool.signal.connect(self.rectangle_drawned)

    def rectangle_drawned(self):
        # Launched every time a new extent is drawned.
        self.activate_window()

    def activate_window(self):
        # Put the dialog on top once the rectangle is drawn
        self.showNormal()
        self.activateWindow()
        self.canvas.unsetMapTool(self.rectangle_tool)

    def load_occurrences(self):
        # Remove the map tool to draw the rectangle
        self.canvas.unsetMapTool(self.rectangle_tool)
        filters = self._ui_to_filters()
        try:
            self.count_request.download(
                _finalize_filters(filters),
            )
        except GBIFApiError as e:
            self.error_message(self.tr("GBIF Error: ") + str(e))
        except AttributeError:
            pass

    def count_results(self):
        # check count of occurrence, stop algorithm if the number is to high
        # show a warning message if the number of occurrence is high
        # stop the algorithm if there is no occurrence.
        total_count = self.count_request.nb_obs
        if total_count > int(__api_max_total_records__):
            self.dialog_too_many_results()
        elif total_count > 0:  # We have results
            self.before_search_ui()
            if total_count > int(__api_warning_threshold__):
                if not show_warning():
                    return  # User chose not to continue
            self.show_progress(0, total_count)
            today = datetime.datetime.now()
            year = today.year
            month = today.strftime("%m")
            day = today.strftime("%d")

            # create output layer name
            if not self.count_request.taxon_key:
                if not self.count_request.scientific_name:
                    lyr_name = (
                        str(year)
                        + str(month)
                        + str(day)
                        + "_GBIF_Occurrences"
                    )
                else:
                    lyr_name = (
                        str(year)
                        + str(month)
                        + str(day)
                        + "_GBIF_Occurrences_"
                        + str(self.count_request.scientific_name)
                    )
            else:
                lyr_name = (
                    str(year)
                    + str(month)
                    + str(day)
                    + "_GBIF_Occurrences_"
                    + str(self.count_request.taxon_key)
                )
            layer = create_and_add_layer(
                project=self.project,
                name=lyr_name,
                epsg_id=self.crs_selection.crs().postgisSrid()
            )

            # launch batch download of occurrences
            total_pages = calculate_pages(
                int(total_count),
                int(__api_per_page_records__)
            )
            self.batch_request.total_pages = total_pages
            self.batch_request.download(
                self.count_request.params,
                layer,
                total_count
            )

            # We need this to make UI responsive
            QApplication.processEvents()
        else:
            QMessageBox.information(
                self,
                self.tr("Warning"),
                self.tr("No results returned.")
            )

    def occurrences_results(self):
        self.after_search_ui()
        self.close()
