# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qgis_occurrences_dialog_base.ui'
#
# Created: Wed Dec  3 11:12:07 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_GBIFOccurrencesDialogBase(object):
    def setupUi(self, GBIFOccurrencesDialogBase):
        GBIFOccurrencesDialogBase.setObjectName(_fromUtf8("GBIFOccurrencesDialogBase"))
        GBIFOccurrencesDialogBase.resize(400, 194)
        self.scientific_name = QtGui.QLineEdit(GBIFOccurrencesDialogBase)
        self.scientific_name.setGeometry(QtCore.QRect(150, 20, 211, 21))
        self.scientific_name.setObjectName(_fromUtf8("scientific_name"))
        self.label = QtGui.QLabel(GBIFOccurrencesDialogBase)
        self.label.setGeometry(QtCore.QRect(20, 20, 111, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.progressBar = QtGui.QProgressBar(GBIFOccurrencesDialogBase)
        self.progressBar.setGeometry(QtCore.QRect(20, 160, 361, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.loadButton = QtGui.QPushButton(GBIFOccurrencesDialogBase)
        self.loadButton.setGeometry(QtCore.QRect(240, 120, 141, 40))
        self.loadButton.setFlat(False)
        self.loadButton.setObjectName(_fromUtf8("loadButton"))
        self.loadingLabel = QtGui.QLabel(GBIFOccurrencesDialogBase)
        self.loadingLabel.setGeometry(QtCore.QRect(20, 140, 361, 16))
        self.loadingLabel.setText(_fromUtf8(""))
        self.loadingLabel.setObjectName(_fromUtf8("loadingLabel"))
        self.basisComboBox = QtGui.QComboBox(GBIFOccurrencesDialogBase)
        self.basisComboBox.setGeometry(QtCore.QRect(150, 50, 211, 26))
        self.basisComboBox.setObjectName(_fromUtf8("basisComboBox"))
        self.label_2 = QtGui.QLabel(GBIFOccurrencesDialogBase)
        self.label_2.setGeometry(QtCore.QRect(20, 50, 111, 30))
        self.label_2.setObjectName(_fromUtf8("label_2"))

        self.retranslateUi(GBIFOccurrencesDialogBase)
        QtCore.QMetaObject.connectSlotsByName(GBIFOccurrencesDialogBase)

    def retranslateUi(self, GBIFOccurrencesDialogBase):
        GBIFOccurrencesDialogBase.setWindowTitle(_translate("GBIFOccurrencesDialogBase", "GBIF Occurrences", None))
        self.label.setText(_translate("GBIFOccurrencesDialogBase", "Scientific name:", None))
        self.loadButton.setText(_translate("GBIFOccurrencesDialogBase", "Load occurrences", None))
        self.loadButton.setShortcut(_translate("GBIFOccurrencesDialogBase", "Return", None))
        self.label_2.setText(_translate("GBIFOccurrencesDialogBase", "Basis of record:", None))

