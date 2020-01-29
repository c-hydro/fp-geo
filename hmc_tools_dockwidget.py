# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HMCToolsDockWidget
                                 A QGIS plugin
 Create sdata to run Hydrological Model Continuum
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
import os
from numpy import full, all

from PyQt4 import QtGui, uic
from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import pyqtSignal, pyqtSlot, QThread, QObject

from qgis.core import *

from hmc_tools_settings import oDictVars_Alg_PreProcess, oDictVars_Alg_Land, oDictVars_Alg_WaterMark, \
    oDictVars_Alg_Parameter, oDictVars_Alg_SectionFinder

from hmc_apps_mapping import getMapLayer, getMapSource, checkMapLayer, removeMapLayer
from hmc_tools_preprocess import ToolPreProcess
from hmc_tools_land import ToolLand
from hmc_tools_watermark import ToolWaterMark
from hmc_tools_parameters import ToolParameters

from hmc_apps_io import readTableFile

# Add UI to plugin
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'hmc_tools_dockwidget.ui'))
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class Template Dock
class TemplateDock(QtGui.QDockWidget, FORM_CLASS):

    # -------------------------------------------------------------------------------------
    # Class variable(s) initialization
    iTabSelect = None
    # -------------------------------------------------------------------------------------

    # ---- GLOBAL: Plugin Signal(s) -------------------------------------------------------
    # Signal to search and open file
    openingFile = pyqtSignal(str, str, str, str)
    # Signal to get tab index
    gettingTabIndex = pyqtSignal(int)
    # Signal to close plugin
    closingPlugin = pyqtSignal()
    # Signal to test
    testingAlg = pyqtSignal(str)
    # -------------------------------------------------------------------------------------

    # ---- TAB1: Land Data Signal(s) ------------------------------------------------------
    # Signal to share source
    sharingPreProcessData = pyqtSignal(object)
    # Signal to share data
    sharingLandData = pyqtSignal(object)
    # Signal to update progress bar
    changingLandStatus = pyqtSignal(int)
    # -------------------------------------------------------------------------------------

    # ---- TAB2: WaterMark Data Signal(s) -------------------------------------------------
    # Signal to share data
    sharingWMarkData = pyqtSignal(object)
    # Signal to update progress bar
    changingWMarkStatus = pyqtSignal(int)
    # -------------------------------------------------------------------------------------

    # ---- TAB3: Section Finder Signal(s) -------------------------------------------------
    # Signal to start section finder
    startingSectionFinder = pyqtSignal()
    # Signal to stop section finder
    stoppingSectionFinder = pyqtSignal()
    # Signal to import section table
    importingSectionTable = pyqtSignal(list)
    # -------------------------------------------------------------------------------------

    # ---- TAB4: Parameter(s) Data Signal(s) ----------------------------------------------
    # Signal to share data
    sharingParamData = pyqtSignal(object)
    # Signal to update progress bar
    changingParamStatus = pyqtSignal(int)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Init method
    def __init__(self, parent=None):

        # -------------------------------------------------------------------------------------
        # Constructor
        super(TemplateDock, self).__init__(parent)

        # Set up the user interface from Designer.
        self.setupUi(self)

        # TabWidget action(s)
        self.TabMain.setCurrentIndex(0)
        # -------------------------------------------------------------------------------------

        # ---- TAB1: Land Data Tool -----------------------------------------------------------
        # Get DEM File
        self.BtnSearchDEMFile_T1.clicked.connect(lambda: self.getFile(
            self.LnSearchDEMFile_T1, 'ASCII Grid(*.txt)'))
        self.BtnUploadFile_T1.clicked.connect(lambda: self.openFile(
            self.LnSearchDEMFile_T1, 'DEM', 'raster', ''))

        # Get CURVE NUMBER File
        self.BtnSearchCNFile_T1.clicked.connect(lambda: self.getFile(
            self.LnSearchCNFile_T1, 'ASCII Grid(*.txt)'))
        self.BtnUploadFile_T1.clicked.connect(lambda: self.openFile(
            self.LnSearchCNFile_T1, 'CN', 'raster', ''))

        # Check data algorithm
        self.BtnUploadFile_T1.clicked.connect(lambda: self.checkRegistryData(
            oDictVars_Alg_Land, self.oVarFile_T1, self.BtnStartAlg_T1))

        # Remove all layer(s) related with tool
        self.BtnRemoveFile_T1.clicked.connect(lambda: self.removeRegistryData(oDictVars_Alg_Land))

        # Source file pre-processing operations
        self.CBoxMask_T1.stateChanged.connect(self.setPreProcessOptL1)
        self.CBoxWarp_T1.stateChanged.connect(self.setPreProcessOptL1)
        self.CBoxRescale_T1.stateChanged.connect(self.setPreProcessOptL1)
        self.RBtnMaskOverDEM_T1.setEnabled(False)
        self.RBtnMaskOverDEM_T1.setText('Mask --> OverDEM')
        self.RBtnMaskOverDEM_T1.clicked.connect(lambda: self.setPreProcessOptL2(self.RBtnMaskOverDEM_T1))
        self.RBtnMaskOverCN_T1.setEnabled(False)
        self.RBtnMaskOverCN_T1.setText('Mask --> OverCN')
        self.RBtnMaskOverCN_T1.clicked.connect(lambda: self.setPreProcessOptL2(self.RBtnMaskOverCN_T1))

        self.RBtnWarpOverDEM_T1.setEnabled(False)
        self.RBtnWarpOverDEM_T1.setText('Warp --> OverDEM')
        self.RBtnWarpOverDEM_T1.clicked.connect(lambda: self.setPreProcessOptL2(self.RBtnWarpOverDEM_T1))
        self.RBtnWarpOverCN_T1.setEnabled(False)
        self.RBtnWarpOverCN_T1.setText('Warp --> OverCN')
        self.RBtnWarpOverCN_T1.clicked.connect(lambda: self.setPreProcessOptL2(self.RBtnWarpOverCN_T1))

        self.LnDefineRescaleM_T1.setText('90')

        self.BtnStartAlg_PreProcess_T1.setEnabled(False)
        self.BtnStartAlg_PreProcess_T1.clicked.connect(self.startPreProcessThread)
        self.BtnStopAlg_PreProcess_T1.setEnabled(False)
        self.BtnStopAlg_PreProcess_T1.clicked.connect(self.stopPreProcessThread)

        # Set land data parameter(s)
        self.LnDefineEPSG_T1.setText('4326')
        self.LnDefineThrASk.setText('150000')
        self.LnDefineThrCRes.setText('0.5')
        self.LnDefineThrWts.setText('50')
        self.LnDefineDomainName_T1.setText('data')
        # Set output folder
        self.BtnOutputFolder_T1.clicked.connect(lambda: self.openFolder(
            self.LnDefineOutputFolder_T1))

        # Start/Stop land data algorithm
        self.BtnStartAlg_T1.setEnabled(False)
        self.BtnStopAlg_T1.setEnabled(False)
        self.BtnStartAlg_T1.clicked.connect(self.startLandThread)
        self.BtnStopAlg_T1.clicked.connect(self.stopLandThread)

        # Set progress bar
        self.PrBar_T1.setValue(0)
        self.PrBar_T1.setMinimum(0)
        self.PrBar_T1.setMaximum(10)

        # Connect algorithm step to update progress bar object
        self.changingLandStatus.connect(self.changeLandStatus)

        # Initialize variable(s) and tab index
        self.oVarFile_T1 = {}
        self.getTabIndex()
        # -------------------------------------------------------------------------------------

        # ---- TAB2: WaterMark Data Tool ------------------------------------------------------
        # Get DEM File
        self.BtnSearchDEMFile_T2.clicked.connect(lambda: self.getFile(
            self.LnSearchDEMFile_T2, 'ASCII Grid(*.txt)'))
        self.BtnUploadFile_T2.clicked.connect(lambda: self.openFile(
            self.LnSearchDEMFile_T2, 'DEM', 'raster', ''))
        # Get Flow Directions File
        self.BtnSearchPNTFile_T2.clicked.connect(lambda: self.getFile(
            self.LnSearchPNTFile_T2, 'ASCII Grid(*.txt)'))
        self.BtnUploadFile_T2.clicked.connect(lambda: self.openFile(
            self.LnSearchPNTFile_T2, 'FLOW_DIRECTIONS', 'raster', ''))
        # Get Partial Distance File
        self.BtnSearchPDISTFile_T2.clicked.connect(lambda: self.getFile(
            self.LnSearchPDISTFile_T2, 'ASCII Grid(*.txt)'))
        self.BtnUploadFile_T2.clicked.connect(lambda: self.openFile(
            self.LnSearchPDISTFile_T2, 'PARTIAL_DISTANCE', 'raster', ''))
        # Get Channels Network File
        self.BtnSearchCHOICEFile_T2.clicked.connect(lambda: self.getFile(
            self.LnSearchCHOICEFile_T2, 'ASCII Grid(*.txt)'))
        self.BtnUploadFile_T2.clicked.connect(lambda: self.openFile(
            self.LnSearchCHOICEFile_T2, 'CHANNELS_NETWORK', 'raster', ''))
        # Get Uc Parameter File
        self.BtnSearchUCFile_T2.clicked.connect(lambda: self.getFile(
            self.LnSearchUCFile_T2, 'ASCII Grid(*.txt)'))
        self.BtnUploadFile_T2.clicked.connect(lambda: self.openFile(
            self.LnSearchUCFile_T2, 'UC', 'raster', ''))
        # Get Uh Parameter File
        self.BtnSearchUHFile_T2.clicked.connect(lambda: self.getFile(
            self.LnSearchUHFile_T2, 'ASCII Grid(*.txt)'))
        self.BtnUploadFile_T2.clicked.connect(lambda: self.openFile(
            self.LnSearchUHFile_T2, 'UH', 'raster', ''))
        # Get Sections File
        self.BtnSearchSECTIONFile_T2.clicked.connect(lambda: self.getFile(
            self.LnSearchSECTIONFile_T2, 'ASCII(*.txt)'))
        self.BtnUploadFile_T2.clicked.connect(lambda: self.openFile(
            self.LnSearchSECTIONFile_T2, 'SECTIONS', 'table', ''))

        # Check data algorithm
        self.BtnUploadFile_T2.clicked.connect(lambda: self.checkRegistryData(
            oDictVars_Alg_WaterMark, self.oVarFile_T2, self.BtnStartAlg_T2))

        # Remove all layer(s) related with tool
        self.BtnRemoveFile_T2.clicked.connect(lambda: self.removeRegistryData(oDictVars_Alg_WaterMark))

        # Set watermark data parameter(s)
        self.LnDefineEPSG_T2.setText('4326')
        self.LnDefineParUHConst_T2.setText('1.5')
        self.LnDefineParUCConst_T2.setText('20')
        self.LnDefineDomainName_T2.setText('data')

        # Set output folder
        self.BtnOutputFolder_T2.clicked.connect(lambda: self.openFolder(
            self.LnDefineOutputFolder_T2))

        # Start/Stop watermark data algorithm
        self.BtnStartAlg_T2.setEnabled(False)
        self.BtnStopAlg_T2.setEnabled(False)
        self.BtnStartAlg_T2.pressed.connect(self.startWMarkThread)
        self.BtnStopAlg_T2.pressed.connect(self.stopWMarkThread)

        # Set progress bar
        self.PrBar_T2.setValue(0)
        self.PrBar_T2.setMinimum(0)
        self.PrBar_T2.setMaximum(11)

        # Connect algorithm step to update progress bar object
        self.changingWMarkStatus.connect(self.changeWMarkStatus)

        # Initialize variable(s)
        self.oVarFile_T2 = {}
        # -------------------------------------------------------------------------------------

        # ---- TAB3: Sections Data Tool -------------------------------------------------------
        # Get ChannelsNetwork File
        self.BtnSearchCNetFile_T3.clicked.connect(lambda: self.getFile(
            self.LnSearchCNetFile_T3, 'ASCII Grid(*.txt)'))
        self.BtnUploadFile_T3.clicked.connect(lambda: self.openFile(
            self.LnSearchCNetFile_T3, 'CHANNELS_NETWORK', 'raster', ''))
        # Get Point(s) File
        self.BtnSearchPointFile_T3.clicked.connect(lambda: self.getFile(
            self.LnSearchPointFile_T3, 'Shapefile(*.shp)'))
        self.BtnUploadFile_T3.clicked.connect(lambda: self.openFile(
            self.LnSearchPointFile_T3, 'POINT', 'vector', 'NAME'))

        # Get Section(s) Table
        self.BtnSearchSectionFile_T3.clicked.connect(lambda: self.getFile(
            self.LnSearchSectionFile_T3, 'ASCII(*.txt)'))
        self.BtnImportTable_T3.clicked.connect(lambda: self.openFile(
            self.LnSearchSectionFile_T3, 'SECTION_IMPORTED_TABLE', 'table', 'NAME'))
        self.BtnImportTable_T3.clicked.connect(self.importSectionTable)

        # Check data algorithm
        self.BtnUploadFile_T3.clicked.connect(lambda: self.checkRegistryData(
            oDictVars_Alg_SectionFinder, self.oVarFile_T3, self.BtnStartAlg_T3))

        # Remove all layer(s) related with tool
        self.BtnRemoveFile_T3.clicked.connect(lambda: self.removeRegistryData(oDictVars_Alg_SectionFinder))

        # Start/Stop section finder tool
        self.BtnStartAlg_T3.setEnabled(False)
        self.BtnStopAlg_T3.setEnabled(False)
        self.BtnStartAlg_T3.pressed.connect(self.startSectionFinder)
        self.BtnStopAlg_T3.pressed.connect(self.stopSectionFinder)

        # Initialize variable(s)
        self.oVarFile_T3 = {}
        # -------------------------------------------------------------------------------------

        # ---- TAB4: Parameters Data Tool -----------------------------------------------------
        # Get DEM File
        self.BtnSearchDEMFile_T4.clicked.connect(lambda: self.getFile(
            self.LnSearchDEMFile_T4, 'ASCII Grid(*.txt)'))
        self.BtnUploadFile_T4.clicked.connect(lambda: self.openFile(
            self.LnSearchDEMFile_T4, 'DEM', 'raster', ''))
        # Get WaterMark File
        self.BtnSearchWMFile_T4.clicked.connect(lambda: self.getFile(
            self.LnSearchWMFile_T4, 'ASCII Grid(*.txt)'))
        self.BtnUploadFile_T4.clicked.connect(lambda: self.openFile(
            self.LnSearchWMFile_T4, 'WATERMARK', 'raster', ''))
        # Get Parameters File
        self.BtnSearchPARFile_T4.clicked.connect(lambda: self.getFile(
            self.LnSearchPARFile_T4, 'ASCII(*.txt)'))
        self.BtnUploadFile_T4.clicked.connect(lambda: self.openFile(
            self.LnSearchPARFile_T4, 'PARAMETERS', 'table', ''))

        # Check data algorithm
        self.BtnUploadFile_T4.clicked.connect(lambda: self.checkRegistryData(
            oDictVars_Alg_Parameter, self.oVarFile_T4, self.BtnStartAlg_T4))

        # Remove all layer(s) related with tool
        self.BtnRemoveFile_T4.clicked.connect(lambda: self.removeRegistryData(oDictVars_Alg_Parameter))

        # Set model data parameter(s)
        self.LnDefineEPSG_T4.setText('4326')
        self.LnDefineParCTConst_T4.setText('0.5')
        self.LnDefineParCFConst_T4.setText('0.02')
        self.LnDefineParUHConst_T4.setText('1.5')
        self.LnDefineParUCConst_T4.setText('20')
        self.LnDefineDomainName_T4.setText('data')

        # Set output folder
        self.BtnOutputFolder_T4.clicked.connect(lambda: self.openFolder(
            self.LnDefineOutputFolder_T4))

        # Start/Stop watermark data algorithm
        self.BtnStartAlg_T4.setEnabled(False)
        self.BtnStopAlg_T4.setEnabled(False)
        self.BtnStartAlg_T4.pressed.connect(self.startParamThread)
        self.BtnStopAlg_T4.pressed.connect(self.stopParamThread)

        # Set progress bar
        self.PrBar_T4.setValue(0)
        self.PrBar_T4.setMinimum(0)
        self.PrBar_T4.setMaximum(9)

        # Connect algorithm step to update progress bar object
        self.changingParamStatus.connect(self.changeParamStatus)

        # Initialize variable(s)
        self.oVarFile_T4 = {}
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Signal to get current tab index
        # self.TabMain.connect(self.TabMain, SIGNAL("currentChanged(int)"), self.getTabIndex) # OLD STYLE
        self.TabMain.currentChanged[int].connect(self.getTabIndex)  # NEW STYLE

        # Initialize worker(s) and thread(s)
        self.oPreProcessTool = None
        self.oPreProcessWorker = None
        self.oLandTool = None
        self.oLandWorker = None
        self.oWMarkTool = None
        self.oWMarkWorker = None
        self.oParamTool = None
        self.oParamWorker = None

        # Initialize variable(s)
        self.iPrBarValue = None

        # Initialize preprocess setting(s)
        self.bMaskDEM = None
        self.bMaskCN = None
        self.bWarpDEM = None
        self.bWarpCN = None
        self.dResValue = None
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to run preprocess algorithm
    def startPreProcessThread(self):

        # Manage btn object(s)
        self.BtnStartAlg_PreProcess_T1.setEnabled(False)
        self.BtnStopAlg_PreProcess_T1.setEnabled(True)

        # Instantiate worker
        self.oPreProcessWorker = Worker(self.runPreProcessAlg)
        self.oPreProcessWorker.signals.sendingWorkerResult.connect(self.sharePreProcessData)
        self.oPreProcessWorker.signals.closingWorkerExc.connect(self.closePreProcessThread)
        self.oPreProcessWorker.signals.stoppingWorkerExc.connect(self.stopPreProcessThread)

        # Execute worker
        self.oPreProcessWorker.start()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to apply option to preprocess land data
    def runPreProcessAlg(self):

        # Get DEM and CN filenames
        if str(self.LnSearchDEMFile_T1.text()) and str(self.LnSearchCNFile_T1.text()):
            sFileName_DEM = str(self.LnSearchDEMFile_T1.text())
            sFileName_CN = str(self.LnSearchCNFile_T1.text())
        elif 'DEM' in self.oVarFile_T1 and 'CN' in self.oVarFile_T1:
            sFileName_DEM = self.oVarFile_T1['DEM']
            sFileName_CN = self.oVarFile_T1['CN']

        # Get output data path
        if self.LnDefineOutputFolder_T1.text():
            sOutPath = self.LnDefineOutputFolder_T1.text()
        else:
            sOutPath = ''

        iEpsgCode = int(self.LnDefineEPSG_T1.text())
        sDomainName = str(self.LnDefineDomainName_T1.text())

        # Instantiate tool preprocess
        self.oPreProcessTool = ToolPreProcess(sFileName_DEM, sFileName_CN,
                                              self.bMaskDEM, self.bMaskCN, self.bWarpDEM, self.bWarpCN, self.dResValue,
                                              sOutPath,
                                              iEpsgCode, sDomainName, oDictVars_Alg_PreProcess)
        # Compute preprocess data
        self.oPreProcessTool.run()
        # Save preprocess data
        self.oPreProcessTool.save()

        # Get data from preprocess class
        oVarsDict = self.oPreProcessTool.oVarsDict

        # Return object(s)
        return oVarsDict

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to stop preprocess thread and algorithm
    def stopPreProcessThread(self):
        # Manage preprocess thread and algorithm (if exists)
        #self.oPreProcessTool.stop()
        self.oPreProcessWorker.stop()

        # Manage btn object(s)
        self.BtnStartAlg_PreProcess_T1.setEnabled(True)
        self.BtnStopAlg_PreProcess_T1.setEnabled(False)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to close preprocess thread
    def closePreProcessThread(self):
        # Manage btn object(s)
        self.BtnStartAlg_PreProcess_T1.setEnabled(True)
        self.BtnStopAlg_PreProcess_T1.setEnabled(False)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to share preprocess result(s) between thread and gui
    def sharePreProcessData(self, oVarsDict):
        self.sharingPreProcessData.emit(oVarsDict)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set level 1 option(s) in preprocess algorithm
    def setPreProcessOptL1(self):

        # Apply option
        if self.CBoxMask_T1.isChecked() or self.CBoxWarp_T1.isChecked() or self.CBoxRescale_T1.isChecked():
            self.BtnStartAlg_PreProcess_T1.setEnabled(True)
            self.BtnStopAlg_PreProcess_T1.setEnabled(False)
        else:
            self.BtnStartAlg_PreProcess_T1.setEnabled(False)
            self.BtnStopAlg_PreProcess_T1.setEnabled(False)

        # Mask option
        if self.CBoxMask_T1.isChecked():
            # Manage radio btn object(s)
            self.RBtnMaskOverDEM_T1.setEnabled(True)
            self.RBtnMaskOverCN_T1.setEnabled(True)
            if self.RBtnMaskOverDEM_T1.isChecked():
                self.setPreProcessOptL2(self.RBtnMaskOverDEM_T1)
            elif self.RBtnMaskOverCN_T1.isChecked():
                self.setPreProcessOptL2(self.RBtnMaskOverCN_T1)
        else:
            # Manage radio btn object(s)
            self.RBtnMaskOverDEM_T1.setEnabled(False)
            self.setPreProcessOptL2(self.RBtnMaskOverDEM_T1)
            self.RBtnMaskOverCN_T1.setEnabled(False)
            self.setPreProcessOptL2(self.RBtnMaskOverCN_T1)

        # Warp option
        if self.CBoxWarp_T1.isChecked():
            # Manage radio btn object(s)
            self.RBtnWarpOverDEM_T1.setEnabled(True)
            self.RBtnWarpOverCN_T1.setEnabled(True)
            if self.RBtnWarpOverDEM_T1.isChecked():
                self.setPreProcessOptL2(self.RBtnWarpOverDEM_T1)
            elif self.RBtnWarpOverCN_T1.isChecked():
                self.setPreProcessOptL2(self.RBtnWarpOverCN_T1)
        else:
            # Manage radio btn object(s)
            self.RBtnWarpOverDEM_T1.setEnabled(False)
            self.setPreProcessOptL2(self.RBtnWarpOverDEM_T1)
            self.RBtnWarpOverCN_T1.setEnabled(False)
            self.setPreProcessOptL2(self.RBtnWarpOverCN_T1)

        # Rescale option
        if self.CBoxRescale_T1.isChecked():
            self.dResValue = float(self.LnDefineRescaleM_T1.text())
        else:
            self.dResValue = None

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set level 2 option(s) in preprocess algorithm
    def setPreProcessOptL2(self, oRBtn):

        if self.CBoxMask_T1.isChecked():
            if oRBtn.text() == 'Mask --> OverDEM':
                QgsMessageLog.logMessage(' --> MASK: OVER DEM', level=QgsMessageLog.INFO)
                self.bMaskDEM = True
                self.bMaskCN = False
            elif oRBtn.text() == 'Mask --> OverCN':
                QgsMessageLog.logMessage(' --> MASK: OVER CN', level=QgsMessageLog.INFO)
                self.bMaskDEM = False
                self.bMaskCN = True
        else:
            self.bMaskDEM = None
            self.bMaskCN = None
            QgsMessageLog.logMessage(' --> MASK NONE', level=QgsMessageLog.INFO)

        if self.CBoxWarp_T1.isChecked():
            if oRBtn.text() == 'Warp --> OverDEM':
                QgsMessageLog.logMessage(' --> WARP: OVER DEM', level=QgsMessageLog.INFO)
                self.bWarpDEM = True
                self.bWarpCN = False
            elif oRBtn.text() == 'Warp --> OverCN':
                QgsMessageLog.logMessage(' --> WARP: OVER CN', level=QgsMessageLog.INFO)
                self.bWarpDEM = False
                self.bWarpCN = True
        else:
            self.bWarpDEM = None
            self.bWarpCN = None
            QgsMessageLog.logMessage(' --> WARP: NONE', level=QgsMessageLog.INFO)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to import data in section table
    def importSectionTable(self):

        sFileName_SEC = str(self.LnSearchSectionFile_T3.text())
        a2oSectionTable = readTableFile(sFileName_SEC)
        a2oSectionTable_T = map(list, zip(*a2oSectionTable))

        self.importingSectionTable.emit(a2oSectionTable_T)

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to start thread for parameter(s) algorithm
    def startParamThread(self):

        # Manage btn object(s)
        self.BtnStartAlg_T4.setEnabled(False)
        self.BtnStopAlg_T4.setEnabled(True)

        # Instantiate worker
        self.oParamWorker = Worker(self.runParamAlg)
        self.oParamWorker.signals.sendingWorkerResult.connect(self.shareParamData)
        self.oParamWorker.signals.closingWorkerExc.connect(self.closeParamThread)
        self.oParamWorker.signals.stoppingWorkerExc.connect(self.stopParamThread)

        # Execute worker
        self.oParamWorker.start()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to run parameter(s) algorithm
    def runParamAlg(self):

        # Get DEM filename
        if str(self.LnSearchDEMFile_T4.text()):
            sFileName_DEM = str(self.LnSearchDEMFile_T4.text())
        elif 'DEM' in self.oVarFile_T4:
            sFileName_DEM = self.oVarFile_T4['DEM']
        QgsMessageLog.logMessage(' FILE DEM: ' + str(sFileName_DEM), level=QgsMessageLog.INFO)

        # Get WATERMARK filename
        if str(self.LnSearchWMFile_T4.text()):
            sFileName_WATERMARK = str(self.LnSearchWMFile_T4.text())
        elif 'WATERMARK' in self.oVarFile_T4:
            sFileName_WATERMARK = self.oVarFile_T4['WATERMARK']
        QgsMessageLog.logMessage(' FILE WATERMARK: ' + str(sFileName_WATERMARK), level=QgsMessageLog.INFO)

        # Get SECTIONS filename
        if str(self.LnSearchPARFile_T4.text()):
            sFileName_PARAM = str(self.LnSearchPARFile_T4.text())
        elif 'PARAMETERS' in self.oVarFile_T4:
            sFileName_PARAM = self.oVarFile_T4['PARAMETERS']
        QgsMessageLog.logMessage(' FILE PARAMETERS: ' + str(sFileName_PARAM), level=QgsMessageLog.INFO)

        # Get output data path
        if self.LnDefineOutputFolder_T4.text():
            sOutPath = self.LnDefineOutputFolder_T4.text()
        else:
            sOutPath = ''

        # Get parameter(s)
        dParConst_CT = float(self.LnDefineParCTConst_T4.text())
        dParConst_CF = float(self.LnDefineParCFConst_T4.text())
        dParConst_UC = float(self.LnDefineParUCConst_T4.text())
        dParConst_UH = float(self.LnDefineParUHConst_T4.text())
        iEpsgCode = int(self.LnDefineEPSG_T4.text())
        sDomainName = str(self.LnDefineDomainName_T4.text())

        # Instantiate tool parameters
        self.oParamTool = ToolParameters(sFileName_DEM, sFileName_WATERMARK, sFileName_PARAM, sOutPath,
                                         dParConst_CT, dParConst_CF, dParConst_UC, dParConst_UH,
                                         iEpsgCode, sDomainName, oDictVars_Alg_Parameter,
                                         callback=self.updateParamThread)

        # Compute land data
        self.oParamTool.run()
        # Save land data
        self.oParamTool.save()
        # Get data from land class
        oVarsDict = self.oParamTool.oVarsDict

        # Return object(s)
        return oVarsDict

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to stop parameter(s) thread and algorithm
    def stopParamThread(self):
        # Manage land thread and algorithm
        self.oParamTool.stop()
        self.oParamWorker.stop()

        # Manage information line and bar
        self.PrBar_T4.reset()
        self.PrBar_T4.setValue(0)

        # Manage btn object(s)
        self.BtnStartAlg_T4.setEnabled(True)
        self.BtnStopAlg_T4.setEnabled(False)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to close parameter(s) thread
    def closeParamThread(self):
        # Manage information line and bar
        self.PrBar_T4.reset()
        self.PrBar_T4.setValue(0)
        # Manage btn object(s)
        self.BtnStartAlg_T4.setEnabled(True)
        self.BtnStopAlg_T4.setEnabled(False)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to share parameter(s) result(s) between thread and gui
    def shareParamData(self, oVarsDict):
        self.sharingParamData.emit(oVarsDict)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get signal(s) form algorithm line and bar progress
    def changeParamStatus(self, iValue):
        self.iPrBarValue = self.PrBar_T4.value() + 1
        self.PrBar_T4.setValue(self.iPrBarValue)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to update parameter(s) thread
    def updateParamThread(self, sValue):
        iValue = int(sValue)
        self.changingParamStatus.emit(iValue)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to start thread for land algorithm
    def startLandThread(self):

        # Manage btn object(s)
        self.BtnStartAlg_T1.setEnabled(False)
        self.BtnStopAlg_T1.setEnabled(True)

        # Instantiate worker
        self.oLandWorker = Worker(self.runLandAlg)
        self.oLandWorker.signals.sendingWorkerResult.connect(self.shareLandData)
        self.oLandWorker.signals.closingWorkerExc.connect(self.closeLandThread)
        self.oLandWorker.signals.stoppingWorkerExc.connect(self.stopLandThread)

        # Execute worker
        self.oLandWorker.start()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to run land algorithm
    def runLandAlg(self):

        # Get DEM filename
        if str(self.LnSearchDEMFile_T1.text()):
            sFileName_DEM = str(self.LnSearchDEMFile_T1.text())
        elif 'DEM' in self.oVarFile_T1:
            sFileName_DEM = self.oVarFile_T1['DEM']
        QgsMessageLog.logMessage(' FILE DEM: ' + str(sFileName_DEM), level=QgsMessageLog.INFO)

        # Get output data path
        if self.LnDefineOutputFolder_T1.text():
            sOutPath = self.LnDefineOutputFolder_T1.text()
        else:
            sOutPath = ''

        # Get parameter(s)
        dThrAsk = float(self.LnDefineThrASk.text())
        dThrCRes = float(self.LnDefineThrCRes.text())
        dThrWts = float(self.LnDefineThrWts.text())
        iEpsgCode = int(self.LnDefineEPSG_T1.text())
        sDomainName = str(self.LnDefineDomainName_T1.text())

        # Instantiate tool land
        self.oLandTool = ToolLand(sFileName_DEM, sOutPath,
                                dThrAsk, dThrCRes, dThrWts,
                                iEpsgCode, sDomainName, oDictVars_Alg_Land, callback=self.updateLandThread)

        # Compute land data
        self.oLandTool.run()
        # Save land data
        self.oLandTool.save()
        # Get data from land class
        oVarsDict = self.oLandTool.oVarsDict

        # Return object(s)
        return oVarsDict

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to stop land thread and algorithm
    def stopLandThread(self):
        # Manage land thread and algorithm
        self.oLandTool.stop()
        self.oLandWorker.stop()

        # Manage information line and bar
        self.PrBar_T1.reset()
        self.PrBar_T1.setValue(0)

        # Manage btn object(s)
        self.BtnStartAlg_T1.setEnabled(True)
        self.BtnStopAlg_T1.setEnabled(False)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to close land thread
    def closeLandThread(self):
        # Manage information line and bar
        self.PrBar_T1.reset()
        self.PrBar_T1.setValue(0)
        # Manage btn object(s)
        self.BtnStartAlg_T1.setEnabled(True)
        self.BtnStopAlg_T1.setEnabled(False)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to share land result(s) between thread and gui
    def shareLandData(self, oVarsDict):
        self.sharingLandData.emit(oVarsDict)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get signal(s) form algorithm line and bar progress
    def changeLandStatus(self, iValue):
        self.iPrBarValue = self.PrBar_T1.value() + 1
        self.PrBar_T1.setValue(self.iPrBarValue)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to update land thread
    def updateLandThread(self, sValue):
        iValue = int(sValue)
        self.changingLandStatus.emit(iValue)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to start thread for watermark algorithm
    def startWMarkThread(self):

        # Manage btn object(s)
        self.BtnStartAlg_T2.setEnabled(False)
        self.BtnStopAlg_T2.setEnabled(True)

        # Instantiate worker
        self.oWMarkWorker = Worker(self.runWMarkAlg)
        self.oWMarkWorker.signals.sendingWorkerResult.connect(self.shareWMarkData)
        self.oWMarkWorker.signals.closingWorkerExc.connect(self.closeWMarkThread)
        self.oWMarkWorker.signals.stoppingWorkerExc.connect(self.stopWMarkThread)

        # Execute worker
        self.oWMarkWorker.start()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to run watermark algorithm
    def runWMarkAlg(self):

        # Get DEM filename
        if str(self.LnSearchDEMFile_T2.text()):
            sFileName_DEM = str(self.LnSearchDEMFile_T2.text())
        elif 'DEM' in self.oVarFile_T2:
            sFileName_DEM = self.oVarFile_T2['DEM']
        QgsMessageLog.logMessage(' FILE DEM: ' + str(sFileName_DEM), level=QgsMessageLog.INFO)

        # Get FLOW_DIRECTIONS filename
        if str(self.LnSearchPNTFile_T2.text()):
            sFileName_PNT = str(self.LnSearchPNTFile_T2.text())
        elif 'FLOW_DIRECTIONS' in self.oVarFile_T2:
            sFileName_PNT = self.oVarFile_T2['FLOW_DIRECTIONS']
        QgsMessageLog.logMessage(' FILE PNT: ' + str(sFileName_PNT), level=QgsMessageLog.INFO)

        # Get PARTIAL_DISTANCE filename
        if str(self.LnSearchPDISTFile_T2.text()):
            sFileName_PDIST = str(self.LnSearchPDISTFile_T2.text())
        elif 'PARTIAL_DISTANCE' in self.oVarFile_T2:
            sFileName_PDIST = self.oVarFile_T2['PARTIAL_DISTANCE']
        QgsMessageLog.logMessage(' FILE PDIST: ' + str(sFileName_PDIST), level=QgsMessageLog.INFO)

        # Get CHANNELS_NETWORK filename
        if str(self.LnSearchCHOICEFile_T2.text()):
            sFileName_CHOICE = str(self.LnSearchCHOICEFile_T2.text())
        elif 'CHANNELS_NETWORK' in self.oVarFile_T2:
            sFileName_CHOICE = self.oVarFile_T2['CHANNELS_NETWORK']
        QgsMessageLog.logMessage(' FILE CHOICE: ' + str(sFileName_CHOICE), level=QgsMessageLog.INFO)

        # Get UC filename
        if str(self.LnSearchUCFile_T2.text()):
            sFileName_UC = str(self.LnSearchUCFile_T2.text())
        elif 'UC' in self.oVarFile_T2:
            sFileName_UC = self.oVarFile_T2['UC']
        else:
            sFileName_UC = None
        QgsMessageLog.logMessage(' FILE UC: ' + str(sFileName_UC), level=QgsMessageLog.INFO)

        # Get UH filename
        if str(self.LnSearchUHFile_T2.text()):
            sFileName_UH = str(self.LnSearchUHFile_T2.text())
        elif 'UH' in self.oVarFile_T2:
            sFileName_UH = self.oVarFile_T2['UH']
        else:
            sFileName_UH = None
        QgsMessageLog.logMessage(' FILE UH: ' + str(sFileName_UH), level=QgsMessageLog.INFO)

        # Get SECTIONS filename
        if str(self.LnSearchSECTIONFile_T2.text()):
            sFileName_SECTION = str(self.LnSearchSECTIONFile_T2.text())
        elif 'SECTIONS' in self.oVarFile_T2:
            sFileName_SECTION = self.oVarFile_T2['SECTIONS']
        QgsMessageLog.logMessage(' FILE SECTIONS: ' + str(sFileName_SECTION), level=QgsMessageLog.INFO)

        # Get output data path
        if self.LnDefineOutputFolder_T2.text():
            sOutPath = self.LnDefineOutputFolder_T2.text()
        else:
            sOutPath = ''

        # Get parameter(s)
        dParConst_UC = float(self.LnDefineParUCConst_T2.text())
        dParConst_UH = float(self.LnDefineParUHConst_T2.text())
        sDomainName = str(self.LnDefineDomainName_T2.text())

        # Instantiate tool watermark
        self.oWMarkTool = ToolWaterMark(sFileName_DEM, sFileName_PNT, sFileName_PDIST, sFileName_CHOICE,
                                      sFileName_UC, sFileName_UH, sFileName_SECTION,
                                      sOutPath,
                                      dParConst_UC, dParConst_UH, sDomainName,
                                      oDictVars_Alg_WaterMark, callback=self.updateWMarkThread)

        # Compute land data
        self.oWMarkTool.run()
        # Save land data
        self.oWMarkTool.save()
        # Get data from land class
        oVarsDict = self.oWMarkTool.oVarsDict

        # Return object(s)
        return oVarsDict

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to close watermark thread
    def closeWMarkThread(self):
        # Manage information line and bar
        self.PrBar_T2.reset()
        self.PrBar_T2.setValue(0)
        # Manage btn object(s)
        self.BtnStartAlg_T2.setEnabled(True)
        self.BtnStopAlg_T2.setEnabled(False)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to share watermark result(s) between thread and gui
    def shareWMarkData(self, oVarsDict):
        self.sharingWMarkData.emit(oVarsDict)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to stop watermark thread and algorithm
    def stopWMarkThread(self):
        # Manage land thread and algorithm
        self.oWMarkTool.stop()
        self.oWMarkWorker.stop()

        # Manage information line and bar
        self.PrBar_T2.reset()
        self.PrBar_T2.setValue(0)

        # Manage btn object(s)
        self.BtnStartAlg_T2.setEnabled(True)
        self.BtnStopAlg_T2.setEnabled(False)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get signal(s) form algorithm line and bar progress
    def changeWMarkStatus(self, iValue):
        self.iPrBarValue = self.PrBar_T2.value() + 1
        self.PrBar_T2.setValue(self.iPrBarValue)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to update land thread
    def updateWMarkThread(self, sValue):
        iValue = int(sValue)
        self.changingWMarkStatus.emit(iValue)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to start selection finder tool
    def startSectionFinder(self):
        self.startingSectionFinder.emit()
        self.BtnStartAlg_T3.setDisabled(True)
        self.BtnImportTable_T3.setDisabled(True)
        self.BtnStopAlg_T3.setDisabled(False)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to close selection finder tool
    def stopSectionFinder(self):
        self.stoppingSectionFinder.emit()
        self.BtnStopAlg_T3.setDisabled(True)
        self.BtnStartAlg_T3.setDisabled(False)
        self.BtnImportTable_T3.setDisabled(False)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get tab index
    def getTabIndex(self, iTabIndex=None):

        # Get tab index if is not defined by previous action(s)
        if iTabIndex is None:
            iTabIndex = self.TabMain.currentIndex()

        # Deactivate/activate section tool (if tab2 is not selected)
        if iTabIndex != 2:
            self.BtnStopAlg_T3.setDisabled(False)
            self.BtnStartAlg_T3.setDisabled(False)

        # Check data algorithm using tab index
        if iTabIndex == 0:
            self.oVarFile_T1 = self.checkRegistryData(
                oDictVars_Alg_Land, self.oVarFile_T1, self.BtnStartAlg_T1)
        if iTabIndex == 1:
            self.oVarFile_T2 = self.checkRegistryData(
                oDictVars_Alg_WaterMark, self.oVarFile_T2, self.BtnStartAlg_T2)
        if iTabIndex == 2:
            self.oVarFile_T3 = self.checkRegistryData(
                oDictVars_Alg_SectionFinder, self.oVarFile_T3, self.BtnStartAlg_T3)
        if iTabIndex == 3:
            self.oVarFile_T4 = self.checkRegistryData(
                oDictVars_Alg_Parameter, self.oVarFile_T4, self.BtnStartAlg_T4)

        # Emit tab value
        self.gettingTabIndex.emit(iTabIndex)

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to open folder
    def openFolder(self, oFolderLine):
        # Select folder using a dialog
        oFolderLine.setText(QtGui.QFileDialog.getExistingDirectory(self, 'Select Folder'))
        return oFolderLine

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to get file
    def getFile(self, oFileLine, sFileType):
        # Select file using a dialog
        oFileLine.setText(QtGui.QFileDialog.getOpenFileName(self, 'Search File', '.', sFileType))
        return oFileLine

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to open file
    def openFile(self, oFileLine, sLayerName, sLayerType, sFieldName):
        sFileName = oFileLine.text()
        QgsMessageLog.logMessage(' ===> OpenFile: ' + sFileName + ' - LayerName: ' + sLayerName,
                                 level=QgsMessageLog.INFO)
        self.openingFile.emit(sFileName, sLayerName, sLayerType, sFieldName)

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to remove all data related with tool from registry
    @staticmethod
    def removeRegistryData(oAlgVarDict):

        for iVarID, sVarKey in enumerate(oAlgVarDict):
            oVarWorkSpace = oAlgVarDict[sVarKey]

            sVarName = oVarWorkSpace['DataName']
            bMapLayer = checkMapLayer(sVarName)

            if bMapLayer is True:
                removeMapLayer(sVarName)
            else:
                pass

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to check registry data available on memory
    @staticmethod
    def checkRegistryData(oAlgVarDict, oAlgVarFile, oAlgBtnStart):

        a1bVarCheck = full(oAlgVarDict.keys().__len__(), False, dtype=bool)
        for iVarID, sVarKey in enumerate(oAlgVarDict):

            oVarWorkSpace = oAlgVarDict[sVarKey]

            sVarWF = oVarWorkSpace['DataWorkFlow']
            sVarLevel = oVarWorkSpace['DataLevel']
            sVarName = oVarWorkSpace['DataName']
            sVarType = oVarWorkSpace['DataType']

            if sVarWF == 'IN' and sVarLevel == 'Mandatory':
                oVarLayer = getMapLayer(sVarName)

                if oVarLayer is not None:
                    sVarFile = getMapSource(oVarLayer)
                    a1bVarCheck[iVarID] = True
                    oAlgVarFile[sVarName] = sVarFile
                else:
                    a1bVarCheck[iVarID] = False

            elif sVarWF == 'IN' and sVarLevel == 'Optional':

                oVarLayer = getMapLayer(sVarName)
                if oVarLayer is not None:
                    sVarFile = getMapSource(oVarLayer)
                    a1bVarCheck[iVarID] = True
                    oAlgVarFile[sVarName] = sVarFile
                else:
                    a1bVarCheck[iVarID] = True
            else:
                a1bVarCheck[iVarID] = True

        if all(a1bVarCheck):
            oAlgBtnStart.setEnabled(True)
        else:
            oAlgBtnStart.setEnabled(False)

        return oAlgVarFile
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to test algorithm
    def testAlg(self):
        sVarTest = 'VARTEST_TEMPLATEDOCK'
        QgsMessageLog.logMessage(' #### TEST FUNCTION #### VAR: ' + sVarTest, level=QgsMessageLog.INFO)
        self.testingAlg.emit(sVarTest)

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to close event (destroy dockwidget)
    def closeEvent(self, oEvent):
        oReply = QMessageBox.question(self, 'Message', "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)
        if oReply == QMessageBox.Yes:
            oEvent.accept()
            self.closingPlugin.emit()
        else:
            oEvent.ignore()
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class to define signals for threads
class WorkerSignals(QObject):

    # Define signals
    closingWorkerExc = pyqtSignal()
    sendingWorkerResult = pyqtSignal(object)
    stoppingWorkerExc = pyqtSignal()

# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class to define worker for threads
class Worker(QThread):

    # -------------------------------------------------------------------------------------
    # Initialize worker
    def __init__(self, oFn, *args, **kwargs):
        super(Worker, self).__init__()
        QThread.__init__(self)

        self.oFn = oFn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.running = False

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to stop function in thread
    def stop(self):
        self.running = False
        self.terminate()

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to run function in thread
    @pyqtSlot()
    def run(self):

        self.running = True

        # Retrieve args/kwargs here; and fire processing using them
        try:
            oResults = self.oFn(*self.args, **self.kwargs)
            if not self.running:
                return
            self.signals.sendingWorkerResult.emit(oResults)
        except:
            self.signals.stoppingWorkerExc.emit()
        finally:
            self.signals.closingWorkerExc.emit()

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
