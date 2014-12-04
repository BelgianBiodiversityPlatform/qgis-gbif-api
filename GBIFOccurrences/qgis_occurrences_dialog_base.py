# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qgis_occurrences_dialog_base.ui'
#
# Created: Thu Dec  4 11:18:19 2014
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
        GBIFOccurrencesDialogBase.resize(544, 270)
        self.scientific_name = QtGui.QLineEdit(GBIFOccurrencesDialogBase)
        self.scientific_name.setGeometry(QtCore.QRect(220, 60, 211, 21))
        self.scientific_name.setObjectName(_fromUtf8("scientific_name"))
        self.label = QtGui.QLabel(GBIFOccurrencesDialogBase)
        self.label.setGeometry(QtCore.QRect(90, 60, 111, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.progressBar = QtGui.QProgressBar(GBIFOccurrencesDialogBase)
        self.progressBar.setGeometry(QtCore.QRect(160, 230, 361, 31))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.loadButton = QtGui.QPushButton(GBIFOccurrencesDialogBase)
        self.loadButton.setGeometry(QtCore.QRect(10, 220, 141, 40))
        self.loadButton.setFlat(False)
        self.loadButton.setObjectName(_fromUtf8("loadButton"))
        self.loadingLabel = QtGui.QLabel(GBIFOccurrencesDialogBase)
        self.loadingLabel.setGeometry(QtCore.QRect(20, 200, 501, 20))
        self.loadingLabel.setText(_fromUtf8(""))
        self.loadingLabel.setObjectName(_fromUtf8("loadingLabel"))
        self.basisComboBox = QtGui.QComboBox(GBIFOccurrencesDialogBase)
        self.basisComboBox.setGeometry(QtCore.QRect(220, 90, 211, 26))
        self.basisComboBox.setObjectName(_fromUtf8("basisComboBox"))
        self.label_2 = QtGui.QLabel(GBIFOccurrencesDialogBase)
        self.label_2.setGeometry(QtCore.QRect(90, 90, 111, 30))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(GBIFOccurrencesDialogBase)
        self.label_3.setGeometry(QtCore.QRect(90, 130, 62, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.countryComboBox = QtGui.QComboBox(GBIFOccurrencesDialogBase)
        self.countryComboBox.setGeometry(QtCore.QRect(220, 130, 211, 26))
        self.countryComboBox.setObjectName(_fromUtf8("countryComboBox"))
        self.line = QtGui.QFrame(GBIFOccurrencesDialogBase)
        self.line.setGeometry(QtCore.QRect(10, 170, 511, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.label_4 = QtGui.QLabel(GBIFOccurrencesDialogBase)
        self.label_4.setGeometry(QtCore.QRect(40, 30, 62, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Lucida Grande"))
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName(_fromUtf8("label_4"))

        self.retranslateUi(GBIFOccurrencesDialogBase)
        QtCore.QMetaObject.connectSlotsByName(GBIFOccurrencesDialogBase)

    def retranslateUi(self, GBIFOccurrencesDialogBase):
        GBIFOccurrencesDialogBase.setWindowTitle(_translate("GBIFOccurrencesDialogBase", "GBIF Occurrences", None))
        self.label.setText(_translate("GBIFOccurrencesDialogBase", "Scientific name:", None))
        self.loadButton.setText(_translate("GBIFOccurrencesDialogBase", "Load occurrences", None))
        self.loadButton.setShortcut(_translate("GBIFOccurrencesDialogBase", "Return", None))
        self.label_2.setText(_translate("GBIFOccurrencesDialogBase", "Basis of record:", None))
        self.label_3.setText(_translate("GBIFOccurrencesDialogBase", "Country:", None))
        self.label_4.setText(_translate("GBIFOccurrencesDialogBase", "Filters:", None))

