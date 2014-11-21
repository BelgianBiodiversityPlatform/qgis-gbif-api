from qgis.core import (QgsVectorLayer, QgsMapLayerRegistry, QgsFeature, QgsGeometry, QgsPoint, QgsField)
from PyQt4 import QtCore


def create_and_add_layer(name):
    #mem_layer = QgsVectorLayer("Point?crs=epsg:4326&field=scientificname:string(255)&field=country:string(255)", name, "memory")

    mem_layer = QgsVectorLayer("Point?crs=epsg:4326", name, "memory")
    QgsMapLayerRegistry.instance().addMapLayer(mem_layer)

    return mem_layer


def _get_field_or_empty(o, field_name):
    if field_name in o:
        return o[field_name]
    else:
        return ''


def add_gbif_occ_to_layer(occurrences, layer):
    features = []

    dp = layer.dataProvider()
    for o in occurrences:
        attrs = []
        for k in o.keys():
            field_index = dp.fieldNameIndex(k)
            if field_index == -1:
                dp.addAttributes([QgsField(k, QtCore.QVariant.String)])
                #layer.commitChanges()
            
            attrs.append({'attr': k, 'val': _get_field_or_empty(o, k)})

        feat = QgsFeature()
        myFields = dp.fields()
        feat.setFields(myFields)

        for d in attrs:
            feat.setAttribute(d['attr'], d['val'])

        feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(o['decimalLongitude'], o['decimalLatitude'])))
        features.append(feat)

    layer.startEditing()
    (res, outFeats) = layer.dataProvider().addFeatures(features)
    layer.commitChanges()
    layer.updateExtents()
    layer.triggerRepaint()
