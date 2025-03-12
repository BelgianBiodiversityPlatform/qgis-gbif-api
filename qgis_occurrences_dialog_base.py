# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'qgis_occurrences_dialog_baseQNVHTK.ui'
##
## Created by: Qt User Interface Compiler version 5.15.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_GBIFOccurrencesDialogBase(object):
    def setupUi(self, GBIFOccurrencesDialogBase):
        if not GBIFOccurrencesDialogBase.objectName():
            GBIFOccurrencesDialogBase.setObjectName(u"GBIFOccurrencesDialogBase")
        GBIFOccurrencesDialogBase.resize(418, 624)
        self.progressBar = QProgressBar(GBIFOccurrencesDialogBase)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(10, 580, 391, 31))
        self.progressBar.setValue(0)
        self.loadButton = QPushButton(GBIFOccurrencesDialogBase)
        self.loadButton.setObjectName(u"loadButton")
        self.loadButton.setGeometry(QRect(10, 540, 141, 31))
        self.loadButton.setCheckable(False)
        self.loadButton.setFlat(False)
        self.loadingLabel = QLabel(GBIFOccurrencesDialogBase)
        self.loadingLabel.setObjectName(u"loadingLabel")
        self.loadingLabel.setGeometry(QRect(10, 520, 391, 20))
        self.line = QFrame(GBIFOccurrencesDialogBase)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(10, 499, 391, 16))
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.label_4 = QLabel(GBIFOccurrencesDialogBase)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 20, 62, 20))
        font = QFont()
        font.setFamily(u"Lucida Grande")
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.layoutWidget = QWidget(GBIFOccurrencesDialogBase)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 60, 391, 420))
        self.gridLayout = QGridLayout(self.layoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.recordedByField = QLineEdit(self.layoutWidget)
        self.recordedByField.setObjectName(u"recordedByField")

        self.gridLayout.addWidget(self.recordedByField, 7, 1, 1, 1)

        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)

        self.label_10 = QLabel(self.layoutWidget)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout.addWidget(self.label_10, 2, 0, 1, 1)

        self.basisComboBox = QComboBox(self.layoutWidget)
        self.basisComboBox.setObjectName(u"basisComboBox")

        self.gridLayout.addWidget(self.basisComboBox, 3, 1, 1, 1)

        self.label_6 = QLabel(self.layoutWidget)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 10, 0, 1, 1)

        self.taxonKeyField = QLineEdit(self.layoutWidget)
        self.taxonKeyField.setObjectName(u"taxonKeyField")

        self.gridLayout.addWidget(self.taxonKeyField, 2, 1, 1, 1)

        self.label_5 = QLabel(self.layoutWidget)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 5, 0, 1, 1)

        self.label_8 = QLabel(self.layoutWidget)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 13, 0, 1, 1)

        self.countryComboBox = QComboBox(self.layoutWidget)
        self.countryComboBox.setObjectName(u"countryComboBox")

        self.gridLayout.addWidget(self.countryComboBox, 4, 1, 1, 1)

        self.label_12 = QLabel(self.layoutWidget)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout.addWidget(self.label_12, 7, 0, 1, 1)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.yearRangeBox = QCheckBox(self.layoutWidget)
        self.yearRangeBox.setObjectName(u"yearRangeBox")

        self.gridLayout_2.addWidget(self.yearRangeBox, 0, 0, 1, 1)

        self.minYearEdit = QLineEdit(self.layoutWidget)
        self.minYearEdit.setObjectName(u"minYearEdit")

        self.gridLayout_2.addWidget(self.minYearEdit, 1, 0, 1, 1)

        self.maxYearEdit = QLineEdit(self.layoutWidget)
        self.maxYearEdit.setObjectName(u"maxYearEdit")
        self.maxYearEdit.setEnabled(False)

        self.gridLayout_2.addWidget(self.maxYearEdit, 1, 1, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_2, 8, 1, 1, 1)

        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.scientificNameField = QLineEdit(self.layoutWidget)
        self.scientificNameField.setObjectName(u"scientificNameField")

        self.gridLayout.addWidget(self.scientificNameField, 1, 1, 1, 1)

        self.label_9 = QLabel(self.layoutWidget)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout.addWidget(self.label_9, 8, 0, 1, 1)

        self.datasetKeyField = QLineEdit(self.layoutWidget)
        self.datasetKeyField.setObjectName(u"datasetKeyField")

        self.gridLayout.addWidget(self.datasetKeyField, 16, 1, 1, 1)

        self.label_15 = QLabel(self.layoutWidget)
        self.label_15.setObjectName(u"label_15")
        font1 = QFont()
        font1.setBold(True)
        font1.setWeight(75)
        self.label_15.setFont(font1)

        self.gridLayout.addWidget(self.label_15, 9, 0, 1, 2)

        self.collectionCodeField = QLineEdit(self.layoutWidget)
        self.collectionCodeField.setObjectName(u"collectionCodeField")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.collectionCodeField.sizePolicy().hasHeightForWidth())
        self.collectionCodeField.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.collectionCodeField, 13, 1, 1, 1)

        self.catalogNumberField = QLineEdit(self.layoutWidget)
        self.catalogNumberField.setObjectName(u"catalogNumberField")

        self.gridLayout.addWidget(self.catalogNumberField, 5, 1, 1, 1)

        self.label_7 = QLabel(self.layoutWidget)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 12, 0, 1, 1)

        self.label_11 = QLabel(self.layoutWidget)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout.addWidget(self.label_11, 16, 0, 1, 1)

        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)

        self.label_13 = QLabel(self.layoutWidget)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setFont(font1)

        self.gridLayout.addWidget(self.label_13, 0, 0, 1, 2)

        self.institutionCodeField = QLineEdit(self.layoutWidget)
        self.institutionCodeField.setObjectName(u"institutionCodeField")
        sizePolicy.setHeightForWidth(self.institutionCodeField.sizePolicy().hasHeightForWidth())
        self.institutionCodeField.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.institutionCodeField, 12, 1, 1, 1)

        self.publishingCountryComboBox = QComboBox(self.layoutWidget)
        self.publishingCountryComboBox.setObjectName(u"publishingCountryComboBox")

        self.gridLayout.addWidget(self.publishingCountryComboBox, 10, 1, 1, 1)

        self.label_gadm_gid = QLabel(self.layoutWidget)
        self.label_gadm_gid.setObjectName(u"label_gadm_gid")

        self.gridLayout.addWidget(self.label_gadm_gid, 6, 0, 1, 1)

        self.gadmGidField = QLineEdit(self.layoutWidget)
        self.gadmGidField.setObjectName(u"gadmGidField")

        self.gridLayout.addWidget(self.gadmGidField, 6, 1, 1, 1)

        self.stopButton = QPushButton(GBIFOccurrencesDialogBase)
        self.stopButton.setObjectName(u"stopButton")
        self.stopButton.setEnabled(False)
        self.stopButton.setGeometry(QRect(150, 540, 111, 31))
        self.layoutWidget.raise_()
        self.progressBar.raise_()
        self.loadButton.raise_()
        self.loadingLabel.raise_()
        self.line.raise_()
        self.label_4.raise_()
        self.stopButton.raise_()

        self.retranslateUi(GBIFOccurrencesDialogBase)

        self.loadButton.setDefault(False)


        QMetaObject.connectSlotsByName(GBIFOccurrencesDialogBase)
    # setupUi

    def retranslateUi(self, GBIFOccurrencesDialogBase):
        GBIFOccurrencesDialogBase.setWindowTitle(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"GBIF Occurrences", None))
        self.loadButton.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"Load occurrences", None))
#if QT_CONFIG(shortcut)
        self.loadButton.setShortcut(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"Return", None))
#endif // QT_CONFIG(shortcut)
        self.loadingLabel.setText("")
        self.label_4.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"Filters:", None))
        self.label_2.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"Basis of record:", None))
        self.label_10.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"Taxon key:", None))
        self.label_6.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"Publishing Country:", None))
        self.label_5.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"Catalog Number:", None))
        self.label_8.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"Collection Code:", None))
        self.label_12.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"Recorded by:", None))
        self.yearRangeBox.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"Use a year range", None))
        self.label.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"Scientific name:", None))
        self.label_9.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"Year:", None))
        self.label_15.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"About data source:", None))
        self.label_7.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"Institution Code:", None))
        self.label_11.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"Dataset key:", None))
        self.label_3.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"Country:", None))
        self.label_13.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"About occurrence:", None))
        self.label_gadm_gid.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"GADM.org Area Code:", None))
        self.stopButton.setText(QCoreApplication.translate("GBIFOccurrencesDialogBase", u"Stop", None))
    # retranslateUi

