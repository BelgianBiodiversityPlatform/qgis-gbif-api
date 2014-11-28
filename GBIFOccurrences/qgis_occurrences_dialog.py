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

from PyQt4 import QtGui, uic, QtCore, Qt

from qgis.utils import iface
from .helpers import create_and_add_layer, add_gbif_occ_to_layer
from .gbif_webservices import get_occurrences_in_baches

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'qgis_occurrences_dialog_base.ui'))


# threads
class WorkerThread(QtCore.QThread):
    def __init__(self, parentThread):
        QtCore.QThread.__init__(self, parentThread)
    
    def run(self, args):
        self.running = True
        success = self.doWork(args)
        self.emit(QtCore.SIGNAL("jobFinished( PyQt_PyObject )"), success)
    
    def stop(self):
        self.running = False
        pass
    
    def doWork(self):
        return True

    def cleanUp(self):
        pass


class LoadOccurrencesThread(WorkerThread):
    def __init__(self, parentThread):
        WorkerThread.__init__(self, parentThread)
    
    def doWork(self, filters):
        already_loaded_records = 0
        for occ, total_records, percent in get_occurrences_in_baches(filters):
            already_loaded_records += len(occ)
            self.emit(QtCore.SIGNAL("occurrences( PyQt_PyObject )"), [occ, percent, total_records])

        return True


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

        self.to_disable_during_load = (self.loadButton, self.scientific_name)

        self.loadButton.clicked.connect(self.load_occurrences)
        self.workerThread = LoadOccurrencesThread(iface.mainWindow())

    def runThread(self, filters):
        QtCore.QObject.connect(self.workerThread, QtCore.SIGNAL("occurrences( PyQt_PyObject )"), self.occurrencesFromThread)
        QtCore.QObject.connect(self.workerThread, QtCore.SIGNAL("jobFinished( PyQt_PyObject )"), self.ui_workerFinished)
        self.workerThread.run(filters)

    def ui_beforeWorker(self):
        self.already_loaded_records = 0
        self.disable_controls()

    def ui_workerFinished(self):
        self.enable_controls()
        self.close()

    def occurrencesFromThread(self, args):
        occ = args[0]
        percent = args[1]
        total_records = args[2]
        self.already_loaded_records += len(occ)

        add_gbif_occ_to_layer(occ, self.current_layer)
        self.progressBar.setValue(percent)
        self.loadingLabel.setText("Adding " + str(self.already_loaded_records) + "/" + str(total_records))
        Qt.QApplication.processEvents()

    def reset_after_search_bar(self):
        self.progressBar.setValue(0)
        self.loadingLabel.setText("")

    def disable_controls(self):
        for widget in self.to_disable_during_load:
            widget.setDisabled(True)

    def enable_controls(self):
        for widget in self.to_disable_during_load:
            widget.setDisabled(False)

    def load_occurrences(self):
        scientific_name = self.scientific_name.text()
        filters = {'scientificName': scientific_name}

        self.current_layer = create_and_add_layer(scientific_name)
        
        self.ui_beforeWorker()
        self.runThread(filters)

