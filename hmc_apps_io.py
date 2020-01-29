"""
Library Features:

Name:          hmc_apps_io
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20170907'
Version:       '1.0.0'
"""

# -------------------------------------------------------------------------------------
# Library
from os.path import join, split, exists
from numpy import zeros
from re import match

from PyQt4.QtCore import QFileInfo, QVariant
from PyQt4.QtGui import QColor, QFont
from qgis.core import *

from hmc_apps_generic import createFolder, defineString
from hmc_apps_mapping import checkMapLayer, getMapLayer
from hmc_apps_io_ascii import openFile, closeFile, readArcGrid, writeArcGrid, readTable, writeTable
from hmc_apps_io_object import parserTable, importTable
from hmc_apps_geo import readGeoHeader, defineGeoCorner, defineGeoGrid
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to set output folder
def setOutFolder(sFileName, sOutPath):

    # Get path and filename
    [sFilePath, sFileBase] = split(sFileName)
    # Set output path
    if not sOutPath:
        sOutPath = join(sFilePath, 'TEMP')
        createFolder(sOutPath)
    else:
        createFolder(sOutPath)

    return sOutPath
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to set variable(s) information
def setVarsInfo(oDictVars, sOutPath, sDomainName):
    # Cycle(s) over variable(s)
    for sVar_Key, oVar_Attributes in oDictVars.iteritems():

        # Match string expression for string extra tags
        if match(r"([aA-zZ$]+\.[aA-zZ$]+)", sVar_Key):
            sVar_KeyExtra = sVar_Key.split('.')[1]
        else:
            sVar_KeyExtra = ''

        # Update output filename
        sVar_FileName_UPD = defineString(join(sOutPath, sVar_KeyExtra, oVar_Attributes['DataFile']),
                                         {'$domain': sDomainName})
        oDictVars[sVar_Key]['DataFile'] = sVar_FileName_UPD

    return oDictVars
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to update variable(s) information in a given field
def updateVarsInfo(oDictVars, oDictVarName, oDictVarValue, sDictVarField):

    # Cycle over variable dictionaries and store in a common workspace
    for (sVarName, a2dVarData) in zip(oDictVarName.values(), oDictVarValue.values()):
        oDictVars[sVarName][sDictVarField] = a2dVarData
    return oDictVars

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to open vector file
def openVectorFile(sFileName, sLayerName, iLayerEPSG, sLayerField):

    # Check layer in registry
    bMapLayer = checkMapLayer(sLayerName)

    # Upload or reload layer
    if bMapLayer is False:

        # Get layer information and data
        oFileInfo = QFileInfo(sFileName)
        oFilePath = oFileInfo.filePath()
        oFileBase = oFileInfo.baseName()

        # Define layer object
        oMapLayer = QgsVectorLayer(sFileName, sLayerName, "ogr")

        # Set layer crs
        oCrs = oMapLayer.crs()
        oCrs.createFromId(iLayerEPSG)
        oMapLayer.setCrs(oCrs)

        # Label point(s)
        oPoint = QgsPalLayerSettings()
        oPoint.readFromLayer(oMapLayer)
        oPoint.enabled = True
        oPoint.fieldName = sLayerField
        oPoint.placement = QgsPalLayerSettings.AroundPoint
        oPoint.textColor = QColor('yellow')
        oPoint.textTransp = 0
        oPoint.setDataDefinedProperty(QgsPalLayerSettings.Size, True, True, '8', '')
        oPoint.writeToLayer(oMapLayer)

        # Redefine name (sometimes qgis upload shapefile including filename
        sLayerName_Shorted = str(oMapLayer.name().split()[0])
        oMapLayer.setLayerName(sLayerName_Shorted)

    else:
        # Layer available in registry
        oMapLayer = getMapLayer(sLayerName)

    return oMapLayer, bMapLayer

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to open raster file
def openRasterFile(sFileName, sLayerName, iLayerEPSG=4326, bMapUpd=False):

    # Check layer in registry
    if bMapUpd is False:
        bMapLayer = checkMapLayer(sLayerName)
    else:
        bMapLayer = False

    # Upload or reload layer
    if bMapLayer is False:

        # Get layer information and data
        oFileInfo = QFileInfo(sFileName)
        oFilePath = oFileInfo.filePath()
        oFileBase = oFileInfo.baseName()

        # Define layer object
        oMapLayer = QgsRasterLayer(oFilePath, oFileBase)

        # Set layer crs
        oCrs = oMapLayer.crs()
        oCrs.createFromId(iLayerEPSG)
        oMapLayer.setCrs(oCrs)

    else:
        # Layer available in registry
        oMapLayer = getMapLayer(sLayerName)

    return oMapLayer, bMapLayer

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to open table file (ascii delimeted file)
def openTableFile(sLayerFile, sLayerName):

    # Check layer in registry
    bMapLayer = checkMapLayer(sLayerName)

    if bMapLayer is False:
        sLayerUri = sLayerFile + '?useHeader=No&delimiter=%s' % ' '
        oMapLayer = QgsVectorLayer(sLayerUri, sLayerName, 'delimitedtext')
        # "?useHeader=No&delimiter=%s' % (' ')"
    else:
        # Layer available in registry
        oMapLayer = getMapLayer(sLayerName)

    return oMapLayer, bMapLayer

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to import table file
def importTableObj(sFileName, oTableObj):
    # Open file handle
    oFileHandle = openFile(sFileName, 'r')
    oTableObj = importTable(oFileHandle, oTableObj)
    closeFile(oFileHandle)
    return oTableObj

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to write table
def writeTableObj(sFileName, oTableObj):

    # Check filename selection is not empty
    if sFileName:

        # Open file handle
        oFileHandle = openFile(sFileName, 'w')

        # Parser table object
        oTableData = parserTable(oTableObj)
        # Write table data to file handle
        oFileHandle = writeTable(oFileHandle, oTableData)

        # Close file to dump data
        closeFile(oFileHandle)

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
#  Method to read table file
def readTableFile(sFileName, iSkipRows=0):
    oFileHandle = openFile(sFileName, 'r')
    a2oVarData = readTable(oFileHandle, iSkipRows)
    return a2oVarData
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to read raster file in ascii format
def readRasterFile(sFileName):

    # Open file handle
    oFileHandle = openFile(sFileName, 'r')
    # Read file
    [a2dData, a1oHeader] = readArcGrid(oFileHandle)

    # Define ancillary data information
    [iRows, iCols, dGeoXMin, dGeoYMin, dGeoXStep, dGeoYStep, dNoData] = readGeoHeader(a1oHeader)
    [dGeoXMin, dGeoXMax, dGeoYMin, dGeoYMax] = defineGeoCorner(dGeoXMin, dGeoYMin, dGeoXStep, dGeoYStep, iCols, iRows)
    [a2dGeoX, a2dGeoY, a1dGeoBox] = defineGeoGrid(dGeoYMin, dGeoXMin, dGeoYMax, dGeoXMax, dGeoYStep, dGeoXStep)

    return a2dData, a1oHeader, a2dGeoX, a2dGeoY, dGeoXStep, dGeoYStep, dNoData
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to save raster in ascii format
def saveRasterFile(sFileName, a2dVarData, a1oVarHeader, sVarFormat, dVarNoData):

    # Open file handle
    #oFileHandle = openFile(sFileName, 'w')
    # Write file
    writeArcGrid(sFileName,
                 a2dVarData, a1oVarHeader, sDataFormat=sVarFormat, dNoData=dVarNoData)

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to get raster layer (from registry or using filename)
def getRasterLayer(sFileName, sRasterName):

    if sFileName is not None:

        # Read data using filename set in processing GUI
        if exists(sFileName):
            oFile = openFile(sFileName, 'r')
            a2dVarData = readArcGrid(oFile)[0]
        else:
            # Read data using filename get from layers source
            a1oRasterName = [layer.name() for layer in QgsMapLayerRegistry.instance().mapLayers().values()]
            if sRasterName in a1oRasterName:
                for oLayer in QgsMapLayerRegistry.instance().mapLayers().values():
                    if oLayer.name() == sRasterName:
                        # Verify layer validity
                        if oLayer.isValid():
                            try:
                                # Get data reading source filename of raster
                                sFileSource = str(oLayer.source())
                                if exists(sFileSource):
                                    oFile = openFile(sFileSource, 'r')
                                    a2dVarData = readArcGrid(oFile)[0]
                                else:
                                    a2dVarData = None
                                break

                            except:

                                # Get data reading all pixels in registry raster
                                oDP = oLayer.dataProvider()
                                oRasterExtent = oDP.extent()
                                iRasterWidth = oDP.xSize()
                                iRasterHeight = oDP.ySize()
                                oRasterBlock = oDP.block(1, oRasterExtent, iRasterWidth, iRasterHeight)

                                a2dVarData = zeros([iRasterWidth, iRasterHeight])
                                for iX in range(iRasterWidth):
                                    for iY in range(iRasterHeight):
                                        dVal = oRasterBlock.value(iX, iY)
                                        a2dVarData[iX, iY] = dVal
                                break
                        else:
                            pass
                    else:
                        pass
            else:
                a2dVarData = None
    else:
        a2dVarData = None

    return a2dVarData
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to open memory file
def openMemoryFile(sTypeFile, sLayerName='UNDEF'):
    oLayer = QgsVectorLayer(sTypeFile, sLayerName, 'memory')

    oMapRenderer = QgsMapRenderer()
    oMapRenderer.setLayerSet(sLayerName)
    oMapComp = QgsComposition(oMapRenderer)
    oLabelComp = QgsComposerLabel(oMapComp)
    oLabelComp.adjustSizeToText()
    oLabelComp.setFont(QFont("Arial", 8))
    oLabelComp.setBackgroundEnabled(True)
    oLabelComp.setBackgroundColor(QColor('blue'))
    oMapComp.addItem(oLabelComp)

    oLayerSymbol = QgsMarkerSymbolV2.createSimple(
        {'color': 'red', 'name': 'square', 'size': '4', 'color_border': '#008000'})

    oLayer.rendererV2().setSymbol(oLayerSymbol)

    return oLayer

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to write memory file
def writeMemoryFile(oLayer, oData, sName):

    # Get layer data provider
    oLayerProvider = oLayer.dataProvider()
    oLayerCaps = oLayer.dataProvider().capabilities()

    QgsMessageLog.logMessage(' DATA DICTIONARY: ' + str(oData), level=QgsMessageLog.INFO)

    # Check data (section provided by section finder)
    if oData:

        # Set layer field(s)
        if oLayerCaps & QgsVectorDataProvider.AddAttributes:
            oRes = oLayer.dataProvider().addAttributes(
                [QgsField(sName, QVariant.String),
                 QgsField("index_x", QVariant.Int),
                 QgsField("index_y", QVariant.Int),
                 QgsField("geo_x", QVariant.Double),
                 QgsField("geo_y", QVariant.Double)])

        for iDataID, oDataValue in enumerate(oData):
            iDataRow = int(oDataValue[0])
            iDataCol = int(oDataValue[1])
            sDataDomain = str(oDataValue[2])
            sDataName = str(oDataValue[3])
            dDataGeoX = float(oDataValue[8])
            dDataGeoY = float(oDataValue[9])

            sDataLabel = sDataDomain + '_' + sDataName

            # Create new features
            oDataFeature = QgsFeature()
            oPoint = QgsPoint(dDataGeoX, dDataGeoY)
            oDataFeature.setGeometry(QgsGeometry.fromPoint(oPoint))
            # Set values to attributes table
            oDataFeature.setAttributes([sDataLabel, iDataRow, iDataCol, dDataGeoX, dDataGeoY])

            oPointLabel = QgsPalLayerSettings()
            oPointLabel.readFromLayer(oLayer)
            oPointLabel.enabled = True
            oPointLabel.fieldName = sName
            oPointLabel.placement = QgsPalLayerSettings.AroundPoint  # OverPoint
            oPointLabel.textColor = QColor('yellow')
            oPointLabel.textTransp = 0
            oPointLabel.setDataDefinedProperty(QgsPalLayerSettings.Size, True, True, '12', '')
            oPointLabel.writeToLayer(oLayer)

            oLayer.startEditing()
            oLayer.addFeatures([oDataFeature], True)
            oLayer.commitChanges()

            oLayer.rendererV2().symbol().symbolLayers()[0].properties()

        else:
            pass

    return oLayer

# -------------------------------------------------------------------------------------
