# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HMCTools
                                 A QGIS plugin
 Create geographical data to run Hydrological Model Continuum
                              -------------------
        begin                : 2017-08-21
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Fabio Delogu
        email                : fabio.delogu@cimafoundation.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# -------------------------------------------------------------------------------------
# Library
import os.path

from PyQt4.QtCore import QSettings, QTranslator, qVersion, Qt
from PyQt4.QtGui import QAction, QIcon, QWidget

from qgis.core import *

# Initialize Qt resources from file resources.py
import resources_rc

# Tool(s)
from hmc_tools_dockwidget import TemplateDock
from hmc_tools_sectionfinder import ToolSectionFinder

# Form(s)
from hmc_form_table import FormTable

# Application(s)
from hmc_apps_mapping import addMapLayer, removeMapLayer, checkMapLayer, paintMapLayer
from hmc_apps_io import openRasterFile, openVectorFile, openTableFile, \
    openMemoryFile, writeMemoryFile
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class HMC Tools
class HMCTools:

    # -------------------------------------------------------------------------------------
    # Variable(s) initialization
    iTabCurrent = 0
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # QGIS Plugin implementation
    def __init__(self, iface, callback=None):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        # Save reference to the QGIS interface
        self.iface = iface
        # Save reference to the QGIS canvas
        self.canvas = self.iface.mapCanvas()

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'HMCTools_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&HMC Tools')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'HMCTools')
        self.toolbar.setObjectName(u'HMCTools')

        # Initialize plugin, dock(s) and form(s)
        self.pluginIsActive = False
        self.dockwidget = None
        self.formTable = None

        # Initialize tool(s)
        self.oSectionFinder = None

        # Initialize variable(s)
        self.iTabCurrent = 0
        self.oDataSection = None
        self.oDataHistory = None

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to allow for language localisation (noinspection PyMethodMayBeStatic)
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('HMCTools', message)

    # -------------------------------------------------------------------------------------

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    # -------------------------------------------------------------------------------------
    # Method to create menu and toolbar in QGIS GUI
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # ADDED: we need to connect the signal in FeaturesTemplates class
        self.dock = TemplateDock()
        #self.dock.cancelingAlg.connect(self.cancelAlg)

        icon_path = ':/plugins/HMCTools/icon.png'
        #icon_path = ':/plugins/HMCTools/hmc_tools_logo.png'
        self.add_action(
            icon_path,
            text=self.tr(u'HMC Tools'),
            callback=self.run,
            parent=self.iface.mainWindow())

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to upload raster/vector layer(s)
    def uploadFile(self, sFileName, sLayerName, sLayerType, sLayerField):
        # Set layer epsg code
        iLayerEPSG = 4326

        # Check layer type
        if sLayerType == 'raster':
            # Open raster layer
            [oMapLayer, bMapLayer] = openRasterFile(sFileName, sLayerName, iLayerEPSG)
        elif sLayerType == 'vector':
            # Open vector layer
            [oMapLayer, bMapLayer] = openVectorFile(sFileName, sLayerName, iLayerEPSG, sLayerField)
        elif sLayerType == 'table':
            # Open delimited text layer
            [oMapLayer, bMapLayer] = openTableFile(sFileName, sLayerName)

        # Check layer validity
        if oMapLayer is not None:
            if (oMapLayer.isValid() is True) and (bMapLayer is False):

                QgsMessageLog.logMessage('HMCTools UPLOAD FILENAME: ' + str(sFileName), level=QgsMessageLog.INFO)
                QgsMessageLog.logMessage('HMCTools UPLOAD LAYERNAME: ' + str(sLayerName), level=QgsMessageLog.INFO)

                # Add raster/vector layer(s) to qgis interface (registry)
                if sLayerType == 'raster':
                    self.iface.addRasterLayer(sFileName, sLayerName)
                elif sLayerType == 'vector':
                    self.iface.addVectorLayer(sFileName, sLayerName, "ogr")
                elif sLayerType == 'table':
                    sFileUri = sFileName + '?useHeader=No&delimiter=%s' % ' '
                    self.iface.addVectorLayer(sFileUri, sLayerName, "delimitedtext")

                # Check map layer extent definition
                if oMapLayer.extent():
                    # Set canvas to layer extent
                    oExtent = oMapLayer.extent()
                    self.iface.mapCanvas().setExtent(oExtent)

                    # Finally refresh qgis interface
                    self.iface.mapCanvas().refresh()
                else:
                    pass

            else:
                # Exit code(s)
                if oMapLayer.isValid() is False:
                    QgsMessageLog.logMessage(' ===> ATTENTION: uploading ' + sFileName + ' ... FAILED!',
                                             level=QgsMessageLog.CRITICAL)
                if bMapLayer is True:
                    QgsMessageLog.logMessage(' ===> WARNING: uploading ' + sFileName + ' ... SKIPPED!',
                                             level=QgsMessageLog.WARNING)

            # Rename layer(s) using only first name (sometimes for shapefile qgis using filename too)
            for oMapLayer in QgsMapLayerRegistry.instance().mapLayers().values():
                sLayerName_Shorted = str(oMapLayer.name().split()[0])
                oMapLayer.setLayerName(sLayerName_Shorted)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to draw section(s) table to connect signal with functions
    def drawSectionTable(self):

        # Get layer data and name
        oLayerData = self.oSectionFinder.oSectionTable
        sLayerName = 'SECTION'

        # Add layer in QGIS canvas
        removeMapLayer(sLayerName)
        oLayer = openMemoryFile('Point?crs=epsg:4326', sLayerName)
        oLayer = writeMemoryFile(oLayer, oLayerData, sLayerName)
        addMapLayer(oLayer)

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to import section data
    def importSectionTable(self, oSectionTable):
        self.oDataHistory = oSectionTable
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to delete section table
    def deleteSectionTable(self):

        # Delete section(s) workspace(s)
        self.oDataHistory = []
        self.oSectionFinder.oSectionTable = []
        # Manage button(s)
        self.dockwidget.BtnStartAlg_T3.setEnabled(True)
        self.dockwidget.BtnStopAlg_T3.setEnabled(False)

        # Clean form table using section(s) data null
        self.formTable.setData(self.oSectionFinder.oSectionTable)

        # Remove layer from registry
        sLayerName = 'SECTION'
        removeMapLayer(sLayerName)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to store section(s) info
    def storeSectionTable(self):
        if self.oSectionFinder is not None:
            self.oDataHistory = self.oSectionFinder.oSectionTable
        else:
            self.oDataHistory = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to close section(s) table and reinitialize it
    def closeSectionTable(self):
        self.formTable = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get section(s) table
    def updateSectionTable(self):

        # Get section(s) table
        oSectionTable = self.oSectionFinder.oSectionTable

        # Run form table to store section(s)
        if self.formTable is None:
            self.formTable = FormTable()
        else:
            pass
        # Fill form table using section(s) data
        self.formTable.setData(oSectionTable)

        # Get signal of closing form (from class FormTable)
        self.formTable.deletingFormTable.connect(self.deleteSectionTable)
        self.formTable.closingFormTable.connect(self.closeSectionTable)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get tab index
    def getTabIndex(self, iTabIndex):

        # Get current tab index
        self.iTabCurrent = iTabIndex

        # Select case using tab index
        if self.iTabCurrent != 2:
            self.storeSectionTable()
            self.iface.actionPan().trigger()

            # Manage btn
            self.dockwidget.BtnStartAlg_T3.setEnabled(False)
            self.dockwidget.BtnStopAlg_T3.setEnabled(False)
        elif self.iTabCurrent == 2:
            pass

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to view raster data
    def viewRasterData(self, oVarsDict, iEpsgCode=4326):

        # Cycle(s) to save all variables
        for sVar_Key, oVar_Attributes in oVarsDict.iteritems():

            # Get information from common dictionary
            bVar_RasterView = oVar_Attributes['DataView']
            sVar_RasterName = oVar_Attributes['DataName']
            sVar_FileName = oVar_Attributes['DataFile']
            oVar_RasterValue = oVar_Attributes['DataValue']
            sVar_RasterWFlow = oVar_Attributes['DataWorkFlow']

            # Condition to view variable(s) in registry
            if bVar_RasterView and oVar_RasterValue is not None:

                QgsMessageLog.logMessage('HMCTools NAME: ' + sVar_RasterName, level=QgsMessageLog.INFO)
                QgsMessageLog.logMessage('HMCTools VIEW: ' + str(bVar_RasterView), level=QgsMessageLog.INFO)
                QgsMessageLog.logMessage('HMCTools FILE: ' + sVar_FileName, level=QgsMessageLog.INFO)

                # Open raster layer
                if sVar_RasterWFlow == 'IN/OUT':
                    bMapUpd = True
                else:
                    bMapUpd = False

                [oMapLayer, bMapLayer] = openRasterFile(sVar_FileName, sVar_RasterName, iEpsgCode, bMapUpd)

                # Check layer validity
                if (oMapLayer.isValid() is True) and (bMapLayer is False):
                    QgsMessageLog.logMessage('HMCTools LAYER VALID ===> ' + sVar_RasterName, level=QgsMessageLog.INFO)

                    # Add raster
                    addMapLayer(oMapLayer, sVar_RasterName)
                    # Paint raster
                    paintMapLayer(oMapLayer)

                    # Set canvas to layer extent
                    oExtent = oMapLayer.extent()
                    self.iface.mapCanvas().setExtent(oExtent)

                    # Finally refresh qgis interface
                    self.iface.mapCanvas().refresh()

            else:
                pass

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to start section finder tool
    def startSectionFinder(self):
        self.oSectionFinder = ToolSectionFinder(self.iface.mapCanvas(), self.dock, self.oDataHistory)
        self.oSectionFinder.updateTableSignal.connect(self.updateSectionTable)
        self.oSectionFinder.updateTableSignal.connect(self.drawSectionTable)
        self.iface.mapCanvas().setMapTool(self.oSectionFinder)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to stop section finder tool
    def stopSectionFinder(self):
        self.storeSectionTable()
        self.iface.actionPan().trigger()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # ADDED: test function
    def testAlg(self, sVarTest):
        QgsMessageLog.logMessage('HMCTools TESTFUNCTION AND TESTVAR: ' + sVarTest, level=QgsMessageLog.INFO)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to load base map(s)
    def loadBaseMap(self):

        # -------------------------------------------------------------------------------------
        # Get application current folder
        sPluginFolder = os.path.dirname(os.path.realpath(__file__))
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Add coastline shapefile layer
        sLayerName = 'LandCoast'
        if checkMapLayer(sLayerName) is False:
            sFileName = os.path.join(sPluginFolder, "base", "ne_10m_coastline", "ne_10m_coastline.shp")
            oLayer = QgsVectorLayer(sFileName, sLayerName, 'ogr')
            QgsMapLayerRegistry.instance().addMapLayer(oLayer)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Add boundaries shapefile layer
        sLayerName = 'LandBoundary'
        if checkMapLayer(sLayerName) is False:
            sFileName = os.path.join(sPluginFolder, "base", "ne_10m_land", "ne_10m_land.shp")
            oLayer = QgsVectorLayer(sFileName, sLayerName, 'ogr')
            QgsMapLayerRegistry.instance().addMapLayer(oLayer)
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to close plugin and all related item(s)
    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        # disconnects plugin and all related item(s)
        if self.formTable:
            self.formTable.close()
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to remove plugin from QGIS GUI
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD HMCTools"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&HMC Tools'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to run and start plugin
    def run(self):
        """Run method that loads and starts the plugin"""

        # Check plugin is active
        if not self.pluginIsActive:
            self.pluginIsActive = True

            # Load dockwidget
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = TemplateDock()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # ADDED: event action(s) specified in TemplateDock
            self.dockwidget.openingFile.connect(self.uploadFile)

            self.dockwidget.sharingPreProcessData.connect(self.viewRasterData)
            self.dockwidget.sharingLandData.connect(self.viewRasterData)
            self.dockwidget.sharingWMarkData.connect(self.viewRasterData)
            self.dockwidget.sharingParamData.connect(self.viewRasterData)

            self.dockwidget.startingSectionFinder.connect(self.startSectionFinder)
            self.dockwidget.stoppingSectionFinder.connect(self.stopSectionFinder)
            self.dockwidget.importingSectionTable.connect(self.importSectionTable)

            self.dockwidget.gettingTabIndex.connect(self.getTabIndex)

            self.dockwidget.testingAlg.connect(self.testAlg)

            # ADDED: pan tool set to default tool
            self.iface.actionPan().trigger()

            # ADDED: load base map(s)
            self.loadBaseMap()

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
