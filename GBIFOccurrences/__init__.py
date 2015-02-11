# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GBIFOccurrences
                                 A QGIS plugin
 Retrieve data from GBIF webservices (occurences API) directly within QGIS.
                             -------------------
        begin                : 2014-11-18
        copyright            : (C) 2014 by Nicolas Noé - Belgian Biodiversity Platform
        email                : n.noe@biodiversity.be
        git sha              : $Format:%H$
 ***************************************************************************/

 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GBIFOccurrences class from file GBIFOccurrences.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .qgis_occurrences import GBIFOccurrences
    return GBIFOccurrences(iface)
