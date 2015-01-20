# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'n.noe@biodiversity.be'
__date__ = '2014-11-18'
__copyright__ = 'Copyright 2014, Nicolas Noé - Belgian Biodiversity Platform'

import unittest


from PyQt4 import QtCore, QtTest, QtGui

from qgis.core import QgsMapLayerRegistry

from qgis_occurrences_dialog import GBIFOccurrencesDialog

from utilities import get_qgis_app

from httmock import HTTMock
from gbif_mock import gbif_v1_response

QGIS_APP = get_qgis_app()


def close_all_messagebox():
        for widget in QtGui.qApp.topLevelWidgets():
            if isinstance(widget, QtGui.QMessageBox):
                QtTest.QTest.keyClick(widget, QtCore.Qt.Key_Enter)


class GBIFOccurrencesDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.dialog = GBIFOccurrencesDialog(None)
        self.dialog.show()

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def launch_search_and_wait(self, waitfor=2):
        QtTest.QTest.mouseClick(self.dialog.loadButton, QtCore.Qt.LeftButton)
        # As long as we have a mock object for GBIF webservice, this should be fast
        QtTest.QTest.qWait(waitfor * 1000)

    def test_basic_tetraodon(self):
        """ Ensure we have a new layer with 51 features when searching for T. fluviatilis."""

        with HTTMock(gbif_v1_response):
            existing_layers = QgsMapLayerRegistry().instance().mapLayers().values()

            self.dialog.scientificNameField.setText("Tetraodon fluviatilis")
            
            self.launch_search_and_wait(len(existing_layers))
            # everything went OK, get the new layer
            current_layers = QgsMapLayerRegistry().instance().mapLayers().values()
            new_layer = list(set(current_layers).difference(set(existing_layers)))[0]
            
            # We should have 51 feature on this layer
            self.assertEqual(new_layer.featureCount(), 51)

            # The plugin window should be closed
            self.assertFalse(self.dialog.isVisible())

    def test_no_results(self):
        with HTTMock(gbif_v1_response):
            existing_layers = QgsMapLayerRegistry().instance().mapLayers().values()

            self.dialog.scientificNameField.setText("inexisting")
            
            QtCore.QTimer.singleShot(1000, close_all_messagebox)

            self.launch_search_and_wait(len(existing_layers))
            # everything went OK, get the new layer
            current_layers = QgsMapLayerRegistry().instance().mapLayers().values()

            # Ensure no new layer created
            self.assertEqual(current_layers, existing_layers)
            
            # TODO: Ensure a message box has been shown!
            
            #from nose.tools import set_trace; set_trace()
            # Ensure the main dialog stays open
            self.assertTrue(self.dialog.isVisible())

    def test_return_shortcut(self):
        """Ensure the return key also work to launch search."""
        with HTTMock(gbif_v1_response):
            existing_layers = QgsMapLayerRegistry().instance().mapLayers().values()

            self.dialog.scientific_name.setText("Tetraodon fluviatilis")
            
            QtTest.QTest.keyPress(self.dialog, QtCore.Qt.Key_Enter)
            QtTest.QTest.qWait(1000)

            # everything went OK, get the new layer
            current_layers = QgsMapLayerRegistry().instance().mapLayers().values()
            new_layer = list(set(current_layers).difference(set(existing_layers)))[0]
            
            # We should have 51 feature on this layer
            self.assertEqual(new_layer.featureCount(), 51)

    def test_tetraodon_basisofrecord_filter(self):
        with HTTMock(gbif_v1_response):
            existing_layers = QgsMapLayerRegistry().instance().mapLayers().values()

            # 2 filters: scientific name and basis of record
            self.dialog.scientificNameField.setText("Tetraodon fluviatilis")
            self.dialog.basisComboBox.setCurrentIndex(self.dialog.basisComboBox.findText("Unknown"))

            self.launch_search_and_wait(len(existing_layers))
            # everything went OK, get the new layer
            current_layers = QgsMapLayerRegistry().instance().mapLayers().values()
            new_layer = list(set(current_layers).difference(set(existing_layers)))[0]
            
            # We should have 4 feature on this layer
            self.assertEqual(new_layer.featureCount(), 4)

    def test_ui_during_after_load(self):
        """ Ensure the UI is disabled during load, and re-enabled later."""
        with HTTMock(gbif_v1_response):
            self.dialog.scientific_name.setText("Tetraodon fluviatilis")
            QtTest.QTest.mouseClick(self.dialog.loadButton, QtCore.Qt.LeftButton)

            # TODO: fix this test... we should try we a long response (several pages) so yield is called...
            # self.assertFalse(self.dialog.scientific_name.isEnabled())


    # TODO: test list of dicts are supported and serialized as JSON
    # TODO: test unicode is supported in attributes (string and list/dicts)


    def test_layer_projection(self):
        """ Ensure the created layer use EPSG:4326. """

    def test_country_filter(self):
        pass

    def test_layer_name(self):
        pass

    def test_always_have_coordinates(self):
        """Ensure we only ask GBIF records with coordinates."""
        pass

    def test_coordinates(self):
        """Ensure the POINTS are respecting lat/long from returned data"""
        pass

    # TODO: merge with test_attributes (or the opposite: split more)
    def test_attributes_listofdicts(self):
        with HTTMock(gbif_v1_response):
            existing_layers = QgsMapLayerRegistry().instance().mapLayers().values()
            self.dialog.scientific_name.setText("canis lupus")
            self.dialog.countryComboBox.setCurrentIndex(self.dialog.countryComboBox.findText("Germany"))

            self.launch_search_and_wait(len(existing_layers))
            current_layers = QgsMapLayerRegistry().instance().mapLayers().values()
            new_layer = list(set(current_layers).difference(set(existing_layers)))[0]

            new_layer.selectAll()
            all_features = new_layer.selectedFeatures()

            record_id_920936125 = next(f for f in all_features if f.attribute('gbifID') == "920936125")
            
            # Here, we ensure it looks like JSON
            expected_media = '[{"references": "http://www.enjoynature.net/?bild=-1579880650", "format": "text/html"}]'
            self.assertEqual(expected_media, record_id_920936125.attribute('media'))

    # TODO: Also test when value is NULL
    def test_attributes(self):
        """Test the (features) attributes creation is working. """
        with HTTMock(gbif_v1_response):
            # 0. Run a search with 2 filters
            existing_layers = QgsMapLayerRegistry().instance().mapLayers().values()
            self.dialog.scientific_name.setText("Tetraodon fluviatilis")
            self.dialog.basisComboBox.setCurrentIndex(self.dialog.basisComboBox.findText("Unknown"))

            self.launch_search_and_wait(len(existing_layers))
            current_layers = QgsMapLayerRegistry().instance().mapLayers().values()
            new_layer = list(set(current_layers).difference(set(existing_layers)))[0]
        
            # 1. Ensure the righ attributes are the layer
            expected_attributes = ('protocol', 'taxonKey', 'family', 'institutionCode',
                                   'lastInterpreted', 'speciesKey', 'gbifID', 'genericName',
                                   'phylum', 'orderKey', 'facts', 'species', 'issues',
                                   'countryCode', 'basisOfRecord', 'relations', 'classKey',
                                   'catalogNumber', 'scientificName', 'taxonRank', 'familyKey',
                                   'kingdom', 'decimalLatitude', 'publishingOrgKey', 'geodeticDatum',
                                   'collectionCode', 'kingdomKey', 'genusKey', 'locality', 'key',
                                   'phylumKey', 'class', 'publishingCountry', 'lastCrawled',
                                   'datasetKey', 'specificEpithet', 'identifiers',
                                   'decimalLongitude', 'extensions', 'country', 'genus', 'order',
                                   'identifiedBy', 'lastParsed', 'continent', 'nomenclaturalCode',
                                   'higherClassification', 'identifier')
            real_attributes = [new_layer.attributeDisplayName(a) for a in new_layer.pendingAllAttributesList()]

            # 1a. Check that all the expected attributes are found
            # It should make the union of all fields returned from all records (returned fields vary)
            for a in expected_attributes:
                self.assertIn(a, real_attributes)

            # 1b. Also ensure that there are not "unexpected" attributes
            self.assertEqual(len(real_attributes), len(expected_attributes))

            # 2. Ensure the correct values/content is set
            new_layer.selectAll()
            all_features = new_layer.selectedFeatures()

            record_id_864652968 = next(f for f in all_features if f.attribute('gbifID') == "864652698")
            record_id_90129834 = next(f for f in all_features if f.attribute('gbifID') == "90129834")

            self.assertEqual(record_id_864652968.attribute('institutionCode'), 'FishBase')
            self.assertEqual(record_id_90129834.attribute('institutionCode'), 'NCL')

            self.assertEqual(record_id_864652968.attribute('basisOfRecord'), 'UNKNOWN')
            self.assertEqual(record_id_90129834.attribute('basisOfRecord'), 'UNKNOWN')

            self.assertIn("COORDINATE_ROUNDED", record_id_864652968.attribute('issues'))
            self.assertIn("GEODETIC_DATUM_ASSUMED_WGS84", record_id_864652968.attribute('issues'))
            self.assertNotIn("COUNTRY_DERIVED_FROM_COORDINATES", record_id_864652968.attribute('issues'))

            self.assertNotIn("COORDINATE_ROUNDED", record_id_90129834.attribute('issues'))
            self.assertIn("GEODETIC_DATUM_ASSUMED_WGS84", record_id_90129834.attribute('issues'))
            self.assertIn("COUNTRY_DERIVED_FROM_COORDINATES", record_id_90129834.attribute('issues'))
            

if __name__ == "__main__":
    suite = unittest.makeSuite(GBIFOccurrencesDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
