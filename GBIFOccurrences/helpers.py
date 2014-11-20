from qgis.core import (QgsVectorLayer, QgsMapLayerRegistry, QgsFeature, QgsGeometry, QgsPoint)


def create_and_add_layer(name, attributes):
    mem_layer = QgsVectorLayer("Point?crs=epsg:4326", name, "memory")

    pr = mem_layer.dataProvider()
    # for a in attributes:
    #     pr.addAttributes([QgsField(a)])

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
        #feat.setAttribute(0, 'hello')
        print o
        feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(o['decimalLongitude'], o['decimalLatitude'])))
        features.append(feat)

    (res, outFeats) = layer.dataProvider().addFeatures(features)
    layer.updateExtents()
    layer.triggerRepaint()
