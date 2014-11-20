# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qgis_occurrences_dialog_base.ui'
#
# Created: Thu Nov 20 14:29:21 2014
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
        GBIFOccurrencesDialogBase.resize(400, 118)
        self.button_box = QtGui.QDialogButtonBox(GBIFOccurrencesDialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 60, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))
        self.scientific_name = QtGui.QLineEdit(GBIFOccurrencesDialogBase)
        self.scientific_name.setGeometry(QtCore.QRect(150, 20, 211, 21))
        self.scientific_name.setObjectName(_fromUtf8("scientific_name"))
        self.label = QtGui.QLabel(GBIFOccurrencesDialogBase)
        self.label.setGeometry(QtCore.QRect(20, 20, 111, 16))
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(GBIFOccurrencesDialogBase)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), GBIFOccurrencesDialogBase.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), GBIFOccurrencesDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(GBIFOccurrencesDialogBase)

    def retranslateUi(self, GBIFOccurrencesDialogBase):
        GBIFOccurrencesDialogBase.setWindowTitle(_translate("GBIFOccurrencesDialogBase", "GBIF Occurrences", None))
        self.label.setText(_translate("GBIFOccurrencesDialogBase", "Scientific name:", None))

