"""
Library Features:

Name:          hmc_apps_mapping
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20170907'
Version:       '1.0.0'
"""

# -------------------------------------------------------------------------------------
# Library
from PyQt4.QtGui import QColor
from qgis.core import *

from os.path import exists
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to check map layer
def checkMapLayer(sLayerName):
    oMapLayer = QgsMapLayerRegistry.instance().mapLayersByName(sLayerName)
    if not oMapLayer:
        bMapLayer = False
    else:
        bMapLayer = True
    return bMapLayer

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to add map layer
def addMapLayer(oLayerMap, sLayerName=None):
    if sLayerName is not None:
        oLayerMap.setLayerName(sLayerName)
    QgsMapLayerRegistry.instance().addMapLayer(oLayerMap)

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to get map layer (from registry)
def getMapLayer(sLayerName):
    # Cycle over layer(s) registry
    for oLyr in QgsMapLayerRegistry.instance().mapLayers().values():
        if oLyr.name() == sLayerName:
            oLayer = oLyr
            return oLayer

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to get map source filename
def getMapSource(oLayer):
    if oLayer:
        sFileSource = str(oLayer.source())

        # Delete extra information about data characteristic(s) --> delimited file ascii
        if '?' in sFileSource:
            sFileSource = sFileSource.split('?')[0]

        if exists(sFileSource):
            return sFileSource
        else:
            return None
    else:
        return None
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to remove map layer
def removeMapLayer(sLayerName):
    # Get all layers in qgis registry
    oLayers = QgsMapLayerRegistry.instance().mapLayers().values()
    for oLayer in oLayers:

        # Remove layer if algorithm will compute it during run
        if str(oLayer.name()) == sLayerName:
            QgsMapLayerRegistry.instance().removeMapLayers([oLayer.id()])
        else:
            pass

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to paint map layer
def paintMapLayer(layer):

    # Get layer feature(s)
    renderer = layer.renderer()
    provider = layer.dataProvider()
    extent = layer.extent()

    ver = provider.hasStatistics(1, QgsRasterBandStats.All)
    stats = provider.bandStatistics(1, QgsRasterBandStats.All, extent, 0)

    #if ver is not False:
    #    print "minimumValue = ", stats.minimumValue
    #    print "maximumValue = ", stats.maximumValue

    if (stats.minimumValue < 0):
        min = 0
    else:
        min = stats.minimumValue

    max = stats.maximumValue
    range = max - min
    add = range // 2
    interval = min + add

    colDic = {'red': '#ff0000', 'yellow': '#ffff00', 'blue': '#0000ff'}

    valueList = [min, interval, max]

    lst = [QgsColorRampShader.ColorRampItem(valueList[0], QColor(colDic['red'])),
           QgsColorRampShader.ColorRampItem(valueList[1], QColor(colDic['yellow'])),
           QgsColorRampShader.ColorRampItem(valueList[2], QColor(colDic['blue']))]

    myRasterShader = QgsRasterShader()
    myColorRamp = QgsColorRampShader()

    myColorRamp.setColorRampItemList(lst)
    myColorRamp.setColorRampType(QgsColorRampShader.INTERPOLATED)
    myRasterShader.setRasterShaderFunction(myColorRamp)

    myPseudoRenderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(),
                                                        layer.type(),
                                                        myRasterShader)

    layer.setRenderer(myPseudoRenderer)

    layer.triggerRepaint()

# -------------------------------------------------------------------------------------
