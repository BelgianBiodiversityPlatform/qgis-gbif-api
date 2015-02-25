# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GBIFOccurrencesDialog
                                 A QGIS plugin
 Retrieve data from GBIF webservices (occurences API) directly within QGIS.
                             -------------------
        begin                : 2014-11-18
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Nicolas Noé - Belgian Biodiversity Platform
        email                : n.noe@biodiversity.be
 ***************************************************************************/

"""

import os
import sys

from PyQt4 import QtGui, uic, Qt

from helpers import create_and_add_layer, add_gbif_occ_to_layer
from gbif_webservices import get_occurrences_in_baches, count_occurrences, ConnectionIssue

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')
sys.path.append(vendor_dir)
from iso3166 import countries

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'qgis_occurrences_dialog_base.ui'))


COMBOBOX_ALL_LABEL = "-- All --"


def _populate_country_field(combobox):
    combobox.addItem(COMBOBOX_ALL_LABEL)
    for c in countries:
        combobox.addItem(c.name)


def _get_selected_country_code(combobox):
    for c in countries:
            if combobox.currentText() == c.name:
                return c.alpha2
    # Not found
    return None


def _get_val_or_range(checkbox, min_field, max_field):
    if checkbox.isChecked():
        return "{min},{max}".format(min=min_field.text(), max=max_field.text())
    else:
        return min_field.text()


class GBIFOccurrencesDialog(QtGui.QDialog, FORM_CLASS):
    # Key: UI label
    # Value: GBIF filter constants, see
    # http://gbif.github.io/gbif-api/apidocs/org/gbif/api/vocabulary/BasisOfRecord.html
    BOR = {
        COMBOBOX_ALL_LABEL: None,
        "Fossilized specimen": "FOSSIL_SPECIMEN",
        "Human observation": "HUMAN_OBSERVATION",
        "Literature": "LITERATURE",
        "Living specimen": "LIVING_SPECIMEN",
        "Machine observation": "MACHINE_OBSERVATION",
        "Material sample": "MATERIAL_SAMPLE",
        "Observation": "OBSERVATION",
        "Preserved specimen": "PRESERVED_SPECIMEN",
        "Unknown": "UNKNOWN"
    }

    def __init__(self, parent=None):
        """Constructor."""
        super(GBIFOccurrencesDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self._populate_bor()
        self._populate_countries()
        self._populate_publishing_countries()
        self.to_disable_during_load = (self.loadButton, self.scientificNameField,
                                       self.basisComboBox, self.countryComboBox,
                                       self.catalogNumberField, self.publishingCountryComboBox,
                                       self.institutionCodeField, self.collectionCodeField,
                                       self.yearRangeBox, self.maxYearEdit, self.minYearEdit,
                                       self.taxonKeyField, self.datasetKeyField, self.recordedByField)

        self.loadButton.clicked.connect(self.load_occurrences)
        self.yearRangeBox.clicked.connect(self.year_range_ui)

    def _populate_countries(self):
        _populate_country_field(self.countryComboBox)

    def _populate_publishing_countries(self):
        _populate_country_field(self.publishingCountryComboBox)

    def _populate_bor(self):
        vals = self.BOR.keys()
        self.basisComboBox.addItems(sorted(vals))

    def _disable_controls(self):
        for widget in self.to_disable_during_load:
            widget.setDisabled(True)

    def _enable_controls(self):
        for widget in self.to_disable_during_load:
            widget.setDisabled(False)

    def before_search_ui(self):
        self._disable_controls()

    def after_search_ui(self):
        self._enable_controls()

        self.year_range_ui()  # We may have messed up with enabled status of year fields...

        # Theose have been affected during search
        self.progressBar.setValue(0)
        self.loadingLabel.setText("")

    def show_progress(self, already_loaded_records, total_records):
        self.loadingLabel.setText("Adding " + str(already_loaded_records) +
                                  "/" + str(total_records))
        percent = ((already_loaded_records / float(total_records)) * 100)
        self.progressBar.setValue(percent)

    def connection_error_message(self):
        msg = "Cannot connect to GBIF. Please check your Internet connection."
        QtGui.QMessageBox.critical(self, "Error", msg)

    def _ui_to_filters(self):
        return {'scientificName': self.scientificNameField.text(),
                'basisOfRecord': self.BOR[self.basisComboBox.currentText()],
                'country': _get_selected_country_code(self.countryComboBox),
                'catalogNumber': self.catalogNumberField.text(),
                'publishingCountry': _get_selected_country_code(self.publishingCountryComboBox),
                'institutionCode': self.institutionCodeField.text(),
                'collectionCode': self.collectionCodeField.text(),
                'year': _get_val_or_range(self.yearRangeBox, self.minYearEdit, self.maxYearEdit),
                'taxonKey': self.taxonKeyField.text(),
                'datasetKey': self.datasetKeyField.text(),
                'recordedBy': self.recordedByField.text()}

    def year_range_ui(self):
        if self.yearRangeBox.isChecked():
            self.maxYearEdit.setDisabled(False)
        else:
            self.maxYearEdit.setDisabled(True)

    def load_occurrences(self):
        filters = self._ui_to_filters()

        try:
            count = count_occurrences(filters)
        except ConnectionIssue:
            self.connection_error_message()
        else:
            if count > 0:  # We have results
                self.before_search_ui()
                layer = create_and_add_layer(filters['scientificName'])

                already_loaded_records = 0

                for occ in get_occurrences_in_baches(filters):
                    already_loaded_records += len(occ)
                    self.show_progress(already_loaded_records, count)
                    add_gbif_occ_to_layer(occ, layer)

                    # We need this to make UI responsive (progress bar advance, ...)
                    Qt.QApplication.processEvents()

                self.after_search_ui()

                self.close()
            else:
                QtGui.QMessageBox.information(self, "Warning", "No results returned.")
