import json

from qgis.core import (QgsVectorLayer, QgsMapLayerRegistry, QgsFeature, QgsGeometry, QgsPoint, QgsField)
from PyQt4 import QtCore


def create_and_add_layer(name, epsg_id=4326):
    """Create a new memory layer, add it to the map and return it."""
    mem_layer = QgsVectorLayer("Point?crs=epsg:{id}&index=true".format(id=epsg_id), name, "memory")
    QgsMapLayerRegistry.instance().addMapLayer(mem_layer)

    return mem_layer


def add_features_to_layer(layer, features):
    layer.startEditing()
    layer.dataProvider().addFeatures(features)
    layer.commitChanges()
    layer.updateExtents()
    layer.triggerRepaint()


# To distinguish sequences from strings
def is_sequence(arg):
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))


# Takes data and return a string suitable for a (feature) attribute
# It will be either a standard string, either a serialized JSON object in cas of complex structure
def _get_field_value(o, field_name):
    value = o[field_name]

    if value:
        if is_sequence(value):  # Case 1: It's a list/dict
            return json.dumps(value, ensure_ascii=False)
        else:  # Case 2: It's a string
            return value
    else:  # Case 3: missing value
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
            
            attrs.append({'attr': k, 'val': _get_field_value(o, k)})

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
    
