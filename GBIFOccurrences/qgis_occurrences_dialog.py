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

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic

from .helpers import create_and_add_layer, add_gbif_occ_to_layer
from .gbif_webservices import get_occurrences_in_baches

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'qgis_occurrences_dialog_base.ui'))


class GBIFOccurrencesDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(GBIFOccurrencesDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.loadButton.clicked.connect(self.load_occurrences)

    def load_occurrences(self):
        scientific_name = self.scientific_name.text()
        filters = {'scientificName': scientific_name}

        layer = create_and_add_layer(scientific_name)
            
        for occ, percent in get_occurrences_in_baches(filters):
            # FIXME: print statement NEEDED, otherwise unresponsive UI/progressBar
            print "Will add " + str(len(occ)) + " records, " + str(percent) + " %"
            self.progressBar.setValue(percent)
            add_gbif_occ_to_layer(occ, layer)

        self.close()

