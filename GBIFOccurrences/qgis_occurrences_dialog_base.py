# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qgis_occurrences_dialog_base.ui'
#
# Created: Tue Jan 20 14:26:42 2015
#      by: PyQt4 UI code generator 4.11.2
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
        GBIFOccurrencesDialogBase.resize(544, 315)
        self.progressBar = QtGui.QProgressBar(GBIFOccurrencesDialogBase)
        self.progressBar.setGeometry(QtCore.QRect(160, 270, 361, 31))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.loadButton = QtGui.QPushButton(GBIFOccurrencesDialogBase)
        self.loadButton.setGeometry(QtCore.QRect(10, 260, 141, 40))
        self.loadButton.setCheckable(False)
        self.loadButton.setDefault(False)
        self.loadButton.setFlat(False)
        self.loadButton.setObjectName(_fromUtf8("loadButton"))
        self.loadingLabel = QtGui.QLabel(GBIFOccurrencesDialogBase)
        self.loadingLabel.setGeometry(QtCore.QRect(20, 240, 501, 20))
        self.loadingLabel.setText(_fromUtf8(""))
        self.loadingLabel.setObjectName(_fromUtf8("loadingLabel"))
        self.line = QtGui.QFrame(GBIFOccurrencesDialogBase)
        self.line.setGeometry(QtCore.QRect(10, 210, 511, 16))
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
        self.widget = QtGui.QWidget(GBIFOccurrencesDialogBase)
        self.widget.setGeometry(QtCore.QRect(90, 60, 361, 120))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout = QtGui.QGridLayout(self.widget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.scientificNameField = QtGui.QLineEdit(self.widget)
        self.scientificNameField.setObjectName(_fromUtf8("scientificNameField"))
        self.gridLayout.addWidget(self.scientificNameField, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.basisComboBox = QtGui.QComboBox(self.widget)
        self.basisComboBox.setObjectName(_fromUtf8("basisComboBox"))
        self.gridLayout.addWidget(self.basisComboBox, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.widget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.countryComboBox = QtGui.QComboBox(self.widget)
        self.countryComboBox.setObjectName(_fromUtf8("countryComboBox"))
        self.gridLayout.addWidget(self.countryComboBox, 2, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.widget)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)
        self.catalogNumberField = QtGui.QLineEdit(self.widget)
        self.catalogNumberField.setObjectName(_fromUtf8("catalogNumberField"))
        self.gridLayout.addWidget(self.catalogNumberField, 3, 1, 1, 1)

        self.retranslateUi(GBIFOccurrencesDialogBase)
        QtCore.QMetaObject.connectSlotsByName(GBIFOccurrencesDialogBase)

    def retranslateUi(self, GBIFOccurrencesDialogBase):
        GBIFOccurrencesDialogBase.setWindowTitle(_translate("GBIFOccurrencesDialogBase", "GBIF Occurrences", None))
        self.loadButton.setText(_translate("GBIFOccurrencesDialogBase", "Load occurrences", None))
        self.loadButton.setShortcut(_translate("GBIFOccurrencesDialogBase", "Return", None))
        self.label_4.setText(_translate("GBIFOccurrencesDialogBase", "Filters:", None))
        self.label.setText(_translate("GBIFOccurrencesDialogBase", "Scientific name:", None))
        self.label_2.setText(_translate("GBIFOccurrencesDialogBase", "Basis of record:", None))
        self.label_3.setText(_translate("GBIFOccurrencesDialogBase", "Country:", None))
        self.label_5.setText(_translate("GBIFOccurrencesDialogBase", "Catalog Number:", None))

