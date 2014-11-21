from qgis.core import (QgsVectorLayer, QgsMapLayerRegistry, QgsFeature, QgsGeometry, QgsPoint)


def create_and_add_layer(name, attributes):
    mem_layer = QgsVectorLayer("Point?crs=epsg:4326&field=scientificname:string(255)&field=country:string(255)", name, "memory")

    QgsMapLayerRegistry.instance().addMapLayer(mem_layer)

    return mem_layer


def _get_field_or_empty(o, field_name):
    if field_name in o:
        return o[field_name]
    else:
        return ''


def add_gbif_occ_to_layer(occurrences, layer):
    features = []

    for o in occurrences:
        feat = QgsFeature()
        
        feat.setAttributes([_get_field_or_empty(o, 'scientificName'), _get_field_or_empty(o, 'country')])
        feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(o['decimalLongitude'], o['decimalLatitude'])))
        features.append(feat)

    (res, outFeats) = layer.dataProvider().addFeatures(features)
    layer.updateExtents()
    layer.triggerRepaint()
