from qgis.core import (QgsVectorLayer, QgsMapLayerRegistry, QgsFeature, QgsGeometry, QgsPoint)


def create_and_add_layer(name, attributes):
    mem_layer = QgsVectorLayer("Point?crs=epsg:4326&field=scientificname:string(255)&field=country:string(255)", name, "memory")

    QgsMapLayerRegistry.instance().addMapLayer(mem_layer)

    return mem_layer


def add_gbif_occ_to_layer(occurrences, layer):
    features = []
    # fields = layer.dataProvider().fields()
    # for f in fields:
    #     print f

    for o in occurrences:
        feat = QgsFeature()
        
        #feat.setFields(fields)

        #Todo: correspondance between id and field name
        feat.setAttributes([o['scientificName'], o['country']])
        feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(o['decimalLongitude'], o['decimalLatitude'])))
        features.append(feat)

    (res, outFeats) = layer.dataProvider().addFeatures(features)
    layer.updateExtents()
    layer.triggerRepaint()
