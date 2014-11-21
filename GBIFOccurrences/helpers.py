from qgis.core import (QgsVectorLayer, QgsMapLayerRegistry, QgsFeature, QgsGeometry, QgsPoint, QgsField)
from PyQt4 import QtCore


def create_and_add_layer(name, epsg_id=4326):
    """Create a new memory layer, add it to the map and return it."""
    mem_layer = QgsVectorLayer("Point?crs=epsg:{id}".format(id=epsg_id), name, "memory")
    QgsMapLayerRegistry.instance().addMapLayer(mem_layer)

    return mem_layer


def add_features_to_layer(layer, features):
    layer.startEditing()
    layer.dataProvider().addFeatures(features)
    layer.commitChanges()
    layer.updateExtents()
    layer.triggerRepaint()


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
            # Add a layer attribute for each JSON fields(if not already encountered)
            if field_index == -1:
                dp.addAttributes([QgsField(k, QtCore.QVariant.String)])
            
            attrs.append({'attr': k, 'val': _get_field_or_empty(o, k)})

        feat = QgsFeature()

        # We should tell the feature which will be its fields
        # !! We need a variable !! Don't merge the next two lines !!
        myFields = dp.fields()
        feat.setFields(myFields)

        for d in attrs:
            feat.setAttribute(d['attr'], d['val'])

        feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(o['decimalLongitude'], o['decimalLatitude'])))
        
        features.append(feat)

    add_features_to_layer(layer, features)
    
