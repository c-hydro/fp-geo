"""
Library Features:

Name:          hmc_tools_sectionfinder
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20170907'
Version:       '1.0.0'
"""

# -------------------------------------------------------------------------------------
# Library
from PyQt4.QtCore import pyqtSignal
from qgis.gui import QgsMapTool
from qgis.core import QgsRaster, QgsMessageLog, QgsMapLayerRegistry

from hmc_form_section import FormSection
from hmc_form_table import FormTable
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class Tool SectionFinder
class ToolSectionFinder(QgsMapTool):

    # -------------------------------------------------------------------------------------
    # Signal trigger with no arguments
    endFormSignal = pyqtSignal()
    updateTableSignal = pyqtSignal(list)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Init method
    def __init__(self, canvas, dock, data=None, callback=None):
        QgsMapTool.__init__(self, canvas)

        # -------------------------------------------------------------------------------------
        # Initialize variable(s) and object(s)
        self.canvas = canvas
        self.dock = dock
        self.form = None

        self.oSectionHistory = data

        self.oSectionForm = None
        self.oSectionMap = None
        self.oSectionTable = []

        self.callback = callback
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get and manage sections info
    def saveSectionInfo(self, oSectionForm):

        oSectionInfo = None
        if oSectionForm is not None:

            sSecDomain = oSectionForm[0]
            sSecName = oSectionForm[1]
            sSecCode = oSectionForm[2]
            sSecArea = oSectionForm[3]
            sSecThrAlert = oSectionForm[4]
            sSecThrAlarm = oSectionForm[5]

            sSecGeoX = str(self.oSectionMap[0])
            sSecGeoY = str(self.oSectionMap[1])
            sSecRow = str(self.oSectionMap[2])
            sSecCol = str(self.oSectionMap[3])
            sSecValue = str(self.oSectionMap[4])

            oSectionInfo = [sSecRow, sSecCol,
                            sSecDomain, sSecName,
                            sSecCode, sSecArea, sSecThrAlert, sSecThrAlarm,
                            sSecGeoX, sSecGeoY, sSecValue]

        else:
            pass

        # Restore section data from previous tool session
        if self.oSectionHistory is not None:
            self.oSectionTable = self.oSectionHistory

        # Check section info data
        if oSectionInfo is not None:
            # Append info section to sections workspace
            self.oSectionTable.append(oSectionInfo)

        # Info section
        # QgsMessageLog.logMessage(' ---> Point info: ' + str(self.oSectionTable), level=QgsMessageLog.INFO)

        if self.callback:
            self.callback()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to openForm using a callback
    def openSectionForm(self):

        # Call section form to edit information
        self.form = FormSection(callback=self.saveSectionInfo)
        # Get signal(s) from SectionForm
        self.form.pressButtonYes.connect(self.emitSignal)
        # Show SectionForm
        self.form.show()

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to emit signal
    def emitSignal(self):
        # Emit the signal
        self.endFormSignal.emit()
        self.updateTableSignal.emit(self.oSectionTable)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to test
    def testFunc(self):
        QgsMessageLog.logMessage(' ==== TEST FUNCTION ', level=QgsMessageLog.INFO)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get point information (based on canvasReleaseEvent implicit function)
    def canvasReleaseEvent(self, oEvent):

        # Select layer(s)
        for oLayer in QgsMapLayerRegistry.instance().mapLayers().values():

            if 'CHANNELS_NETWORK' == oLayer.name():
                oLayer_CNET = oLayer
            if 'POINT' == oLayer.name():
                oLayer_SEC = oLayer

        # Use flow directions layer
        dRasterXSize = oLayer_CNET.rasterUnitsPerPixelX()
        dRasterYSize = oLayer_CNET.rasterUnitsPerPixelY()

        oDP = oLayer_CNET.dataProvider()
        oRasterExtent = oDP.extent()
        iRasterWidth = oDP.xSize()
        iRasterHeight = oDP.ySize()
        iRasterWidth = oDP.xSize()
        iRasterHeight = oDP.ySize()

        # Get the click
        iPixelIndX = oEvent.pos().x()
        iPixelIndY = oEvent.pos().y()

        iRasterYMax = oRasterExtent.yMaximum()
        iRasterXMin = oRasterExtent.xMinimum()

        oPixelCoord = oEvent.originalMapPoint()
        dPixelGeoX = oPixelCoord.x()
        dPixelGeoY = oPixelCoord.y()
        dPixelValue = oDP.identify(oPixelCoord, QgsRaster.IdentifyFormatValue).results().values()[0]

        oPoint = self.canvas.getCoordinateTransform().toMapCoordinates(iPixelIndX, iPixelIndY)

        # Row in pixel coordinates
        iRasterRow = int(((iRasterYMax - dPixelGeoY) / dRasterYSize) + 1)
        # Column in pixel coordinates
        iRasterCol = int(((dPixelGeoX - iRasterXMin) / dRasterXSize) + 1)
        # Check indexes with domain extent
        if iRasterRow <= 0 or iRasterCol <= 0 or iRasterRow > iRasterHeight or iRasterCol > iRasterWidth:
            iRasterRow = None
            iRasterCol = None
        # View point selection
        QgsMessageLog.logMessage(str(iPixelIndX) + ' - ' + str(iPixelIndY))
        QgsMessageLog.logMessage(str(dPixelGeoX) + ' - ' + str(dPixelGeoY) + ' - ' + str(dPixelValue))

        # Use sections layer
        oSectionMap = []
        if (iRasterRow is not None) and (iRasterCol is not None) and (dPixelValue is not None):

            # Info point over domain
            QgsMessageLog.logMessage(' ---> Point over domain', level=QgsMessageLog.INFO)

            # Define section form information
            self.openSectionForm()

            # Define section map information
            oSectionMap = [dPixelGeoX, dPixelGeoY, iRasterRow, iRasterCol, dPixelValue]
            self.oSectionMap = oSectionMap

        else:
            # Info point out of domain
            QgsMessageLog.logMessage(' ---> Point out of domain', level=QgsMessageLog.WARNING)

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
