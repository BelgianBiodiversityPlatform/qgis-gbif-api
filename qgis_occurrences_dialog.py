# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GBIFOccurrencesDialog
                                 A QGIS plugin
 Retrieve data from GBIF webservices (occurrences API) directly within QGIS.
                             -------------------
        begin                : 2014-11-18
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Nicolas Noé - Belgian Biodiversity Platform
        email                : n.noe@biodiversity.be
 ***************************************************************************/

"""
import os
from builtins import str

from qgis.core import (
    Qgis,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsApplication,
)
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QApplication, QMessageBox, QDialog
from qgis.PyQt.QtCore import QDate, Qt, QIODevice, QDir, QFile, QByteArray

if Qgis.QGIS_VERSION_INT >= 40000:
    from qgis.PyQt.QtCore import QIODeviceBase

from .helpers import create_and_add_layer, add_gbif_occ_to_layer
from .gbif_webservices import (
    get_occurrences_in_batches,
    count_occurrences,
    ConnectionIssue,
    GBIFApiError,
    MAX_TOTAL_RECORDS_GBIF,
)
from .rectangle_tool import RectangleDrawTool


FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "qgis_occurrences_dialog_base.ui")
)


COMBOBOX_ALL_LABEL = "-- All --"


def get_countries():
    countries = []

    path = QDir(QgsApplication.metadataPath()).absoluteFilePath(u"country_code_ISO_3166.csv")
    file = QFile(path)
    if Qgis.QGIS_VERSION_INT >= 40000:
        open_mode = QIODeviceBase.OpenModeFlag.ReadOnly
    else:
        open_mode = open_mode = QIODevice.ReadOnly
    if not file.open(open_mode):
        print(u"Error while opening the CSV file: {}, {} ".format(path, file.errorString()))
        return countries

    file.readLine()
    while not file.atEnd():
        country_attr = {}
        line = file.readLine()
        items = line.split(QByteArray(','.encode()))
        country_attr["name"] = items[0].trimmed().data().decode()
        country_attr["alpha2"] = items[1].trimmed().data().decode()
        country_attr["alpha3"] = items[2].trimmed().data().decode()
        countries.append(country_attr)
    file.close()
    return countries


countries = get_countries()


def _populate_country_field(combobox):
    combobox.addItem(COMBOBOX_ALL_LABEL)
    for c in countries:
        combobox.addItem(c["name"])


def _get_selected_country_code(combobox):
    for c in countries:
        if combobox.currentText() == c["name"]:
            return c["alpha2"]
    # Not found
    return None


def _get_val_or_range(min_field, max_field, error_message):
    try:
        max_field.date() >= min_field.date()
        return "{min},{max}".format(min=str(min_field.date().toString('yyyy-MM-dd')), max=str(max_field.date().toString('yyyy-MM-dd')))
    except GBIFApiError as e:
        error_message("GBIF Error: " + str(e))


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

    def __init__(self, parent=None, project=None, iface=None):
        """Constructor."""
        super(GBIFOccurrencesDialog, self).__init__(parent)
        self.project = project
        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        self.setupUi(self)
        self.setFixedSize(self.size())

        self._populate_bor()
        self._populate_countries()
        self._populate_publishing_countries()
        self.set_rectangle_tool()
        # self.to_disable_during_load = ()  # Hinzugefügt

        self.minDateEdit.setDate(QDate.currentDate())
        self.maxDateEdit.setDate(QDate.currentDate())

        self.taxonKeyField.setToolTip('This is the primary id used to identify a taxon, "0" means this filter is not used.<br><b>Must be an integer</b>')
        self.basisComboBox.setToolTip('Basis of record is a Darwin Core term that refers to the specific nature of the record.')
        self.catalogNumberField.setToolTip('An identifier of any form assigned by the source within a physical collection or digital dataset for the record which may not be unique,<br>but should be fairly unique in combination with the institution and collection code.')
        self.recordedByField.setToolTip('The person who recorded the occurrence.')
        self.gadmGidField.setToolTip('A GADM geographic identifier at any level,<br>for example AGO, AGO.1_1, AGO.1.1_1 or AGO.1.1.1_1')
        self.institutionCodeField.setToolTip('An identifier of any form assigned by the source to<br>identifythe institution the record belongs to.<br>Not guaranteed to be unique.')
        self.collectionCodeField.setToolTip('An identifier of any form assigned by the source to<br>identify the physical collection or digital dataset uniquely<br>within the context of an institution.')
        self.datasetKeyField.setToolTip('The occurrence dataset key (a UUID).')

        self.loadButton.clicked.connect(self.load_occurrences)
        self.bboxCheckBox.clicked.connect(self.localisation_selection_ui)
        self.boundariesCheckBox.clicked.connect(self.localisation_selection_ui)
        self.bboxButton.clicked.connect(self.pointer)

        self.dateCheckBox.clicked.connect(self.date_selection_ui)

        self.stop = False
        self.stopButton.clicked.connect(self.clicked_stop_button)

    def showEvent(self, event):
        self.recreate_rubber_band()

    def closeEvent(self, event):
        # Remove rectangle from map
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
            self.basisComboBox.addItemWithCheckState(text=elem,state=Qt.CheckState.Checked,userData=self.BOR[elem])

    def _disable_controls(self):
        self.tabWidget.setDisabled(True)

    def _enable_controls(self):
        self.tabWidget.setDisabled(False)

    def dialog_too_many_results(self):
        msg = """The query returned more than {max} records.\
            Due to limitations in the GBIF infrastructure, very large queries are currently not \
            supported.""".format(
                        max=MAX_TOTAL_RECORDS_GBIF
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
            "Adding " + str(already_loaded_records) + "/" + str(total_records)
        )
        percent = (already_loaded_records / float(total_records)) * 100
        self.progressBar.setValue(int(percent))

    def connection_error_message(self):
        self.error_message(
            "Cannot connect to GBIF. Please check your Internet connection."
        )

    def error_message(self, msg):
        QMessageBox.critical(self, "Error", msg)

    def _ui_to_filters(self):
        if self.dateCheckBox.isChecked():
            event_date = _get_val_or_range(
                self.minDateEdit, self.maxDateEdit, self.error_message
                )
        else:
            event_date = ""
        if not self.bboxCheckBox.isChecked():
            return {
                "scientificName": self.scientificNameField.text(),
                "basisOfRecord": self.basisComboBox.checkedItemsData(),
                "country": _get_selected_country_code(self.countryComboBox),
                "catalogNumber": self.catalogNumberField.text(),
                "publishingCountry": _get_selected_country_code(
                    self.publishingCountryComboBox
                ),
                "institutionCode": self.institutionCodeField.text(),
                "collectionCode": self.collectionCodeField.text(),
                "eventDate": event_date,
                "taxonKey": str(self.taxonKeyField.value()) if self.taxonKeyField.value() != 0 else '',
                "datasetKey": self.datasetKeyField.text(),
                "recordedBy": self.recordedByField.text(),
                "gadm_gid": self.gadmGidField.text(),
            }
        else:
            try:
                self.rectangle_tool.new_extent.asWktPolygon()
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
                    "taxonKey": str(self.taxonKeyField.value()) if self.taxonKeyField.value() != 0 else '',
                    "datasetKey": self.datasetKeyField.text(),
                    "recordedBy": self.recordedByField.text(),
                    "geometry": self.rectangle_tool.new_extent.asWktPolygon(),
                }
            except AttributeError:
                self.error_message("GBIF Error: No bounding box drawned on map canvas, press the dedicated button.")

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
        if self.rectangle_tool.new_extent and self.rectangle_tool.rubber_band.numberOfVertices() == 0:
            extent4326 = self.rectangle_tool.new_extent
            if str(self.project.instance().crs().postgisSrid()) != str(4326):
                geom = self.rectangle_tool.transform_geom(
                    QgsGeometry().fromRect(extent4326),
                    QgsCoordinateReferenceSystem("EPSG:" + str(4326)),
                    self.project.instance().crs(),
                )
            else:
                geom = QgsGeometry().fromRect(extent4326)
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
            count = count_occurrences(filters)
        except ConnectionIssue:
            self.connection_error_message()
        except GBIFApiError as e:
            self.error_message("GBIF Error: " + str(e))
        except AttributeError:
            pass
        else:
            if count > MAX_TOTAL_RECORDS_GBIF:
                self.dialog_too_many_results()
            elif count > 0:  # We have results
                self.before_search_ui()
                scientific_name = filters["scientificName"]
                if not scientific_name:
                    scientific_name = "GBIF_O Taxon {}".format(filters["taxonKey"])
                layer = create_and_add_layer(project=self.project, name=scientific_name)

                already_loaded_records = 0

                for occ in get_occurrences_in_batches(filters):
                    if self.stop:  # Interrupt process if the stop button was pressed
                        self.stop = False
                        break

                    already_loaded_records += len(occ)
                    self.show_progress(already_loaded_records, count)
                    add_gbif_occ_to_layer(occ, layer)

                    # We need this to make UI responsive (progress bar advance, ...)
                    QApplication.processEvents()

                self.after_search_ui()

                self.close()
            else:
                QMessageBox.information(self, "Warning", "No results returned.")
