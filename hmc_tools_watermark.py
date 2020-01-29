"""
Library Features:

Name:          hmc_tools_watermark
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20171214'
Version:       '1.0.1'
"""

# -------------------------------------------------------------------------------------
# Library
import time

from multiprocessing import Process, Manager

from copy import deepcopy
from numpy import zeros, int32, mean
from os.path import exists, split

from qgis.core import *

from hmc_apps_dataland import computeCorrivationTime, computeWatermarkNested

from hmc_apps_io import setOutFolder, setVarsInfo, \
    updateVarsInfo, readRasterFile, saveRasterFile, getRasterLayer, \
    readTableFile
from hmc_apps_generic import createFolder, defineString
from hmc_apps_var import adjustVarF2Py, adjustVarPy2F
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Set variable(s) name
sVarName_DEM = 'DEM'
sVarName_PNT = 'FLOW_DIRECTIONS'
sVarName_CNET = 'CHANNELS_NETWORK'
sVarName_PDIST = 'PARTIAL_DISTANCE'
sVarName_UC = 'UC'
sVarName_UH = 'UH'
sVarName_CTIME = 'CORRIVATION_TIME.$section'
sVarName_MASK = 'MASK.$section'
sVarName_DEMMASKED = 'DEM_MASKED.$section'
sVarName_WATERMARK = 'WATERMARK'
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class Tool WaterMark
class ToolWaterMark:

    # -------------------------------------------------------------------------------------
    # Init class variable(s)
    oVarsHeader = None
    oProcExc = None
    callback = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to initialize algorithm
    def __init__(self, sFileName_DEM, sFileName_PNT, sFileName_PDIST, sFileName_CNET,
                       sFileName_UC, sFileName_UH, sFileName_SEC,
                       sOutPath, dParConst_UC, dParConst_UH, sDomainName,
                       oVarsDict, callback):

        # Set class variable(s)
        self.sFileName_DEM = sFileName_DEM
        self.sFileName_PNT = sFileName_PNT
        self.sFileName_PDIST = sFileName_PDIST
        self.sFileName_CNET = sFileName_CNET
        self.sFileName_UC = sFileName_UC
        self.sFileName_UH = sFileName_UH
        self.sFileName_SEC = sFileName_SEC

        self.sOutPath = sOutPath
        self.dParConst_UC = dParConst_UC
        self.dParConst_UH = dParConst_UH

        self.sDomainName = sDomainName

        self.oVarsDict = oVarsDict

        self.callback = callback
        self.iAlgStep = 0

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to save data
    def save(self):

        # Get data
        oVarsDict = self.oVarsDict
        oVar_HEADER = self.oVarsHeader

        # Cycle(s) to save all variables
        for sVar_Key, oVar_Attributes in oVarsDict.iteritems():

            # Get information from common dictionary
            # sVar_RASTER = oVar_Attributes['DataName']
            # bVar_VIEW = oVar_Attributes['DataView']
            sVar_FILENAME = oVar_Attributes['DataFile']
            oVar_DATAVALUE = oVar_Attributes['DataValue']
            sVar_DATAFORMAT = oVar_Attributes['DataFormat']
            dVar_DATAUNDEF = oVar_Attributes['DataUndef']

            # Set temporary file if needed to save previous computation
            if exists(sVar_FILENAME):
                sVar_FILENAME = sVar_FILENAME + '_TEMP_'

            QgsMessageLog.logMessage(' ====> SAVE FILENAME: ' + sVar_FILENAME, level=QgsMessageLog.INFO)

            # Save variable(s) to ASCII grid format
            saveRasterFile(sVar_FILENAME, oVar_DATAVALUE, oVar_HEADER, sVar_DATAFORMAT, dVar_DATAUNDEF)

        self.progress()

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to compute data
    def run(self):

        # -------------------------------------------------------------------------------------
        # Set output data folder
        self.sOutPath = setOutFolder(self.sFileName_DEM, self.sOutPath)
        # Set land variable(s) information
        self.oVarsDict = setVarsInfo(self.oVarsDict, self.sOutPath, self.sDomainName)
        # Info progress algorithm
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Read filename and get DEM, LONGITUDE and LATITUDE data
        QgsMessageLog.logMessage(' ==> GET DEM ... ', level=QgsMessageLog.INFO)
        [a2dVarData_DEM, a1oVarHeader,
         a2dVarData_GEOX, a2dVarData_GEOY, dVarGeoXStep, dVarGeoYStep, dVarNoData] = readRasterFile(self.sFileName_DEM)
        a2dVarData_DEM_F = adjustVarPy2F(deepcopy(a2dVarData_DEM), 'float32')
        QgsMessageLog.logMessage(' ==> GET DEM ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Get FlowDirections file
        QgsMessageLog.logMessage(' ==> GET FLOW DIRECTIONS ... ', level=QgsMessageLog.INFO)
        a2iVarData_PNT = getRasterLayer(self.sFileName_PNT, sVarName_PNT)
        a2iVarData_PNT_F = adjustVarPy2F(deepcopy(a2iVarData_PNT), 'int32')
        QgsMessageLog.logMessage(' ==> GET FLOW DIRECTIONS ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Get PartialDistance file
        QgsMessageLog.logMessage(' ==> GET PARTIAL DISTANCE ... ', level=QgsMessageLog.INFO)
        a2dVarData_PDIST = getRasterLayer(self.sFileName_PDIST, sVarName_PDIST)
        a2dVarData_PDIST_F = adjustVarPy2F(deepcopy(a2dVarData_PDIST), 'float32')
        QgsMessageLog.logMessage(' ==> GET PARTIAL DISTANCE ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Get ChannelsNetwork file
        QgsMessageLog.logMessage(' ==> GET CHANNELS NETWORK ... ', level=QgsMessageLog.INFO)
        a2iVarData_CNET = getRasterLayer(self.sFileName_CNET, sVarName_CNET)
        a2iVarData_CNET_F = adjustVarPy2F(deepcopy(a2iVarData_CNET), 'int32')
        QgsMessageLog.logMessage(' ==> GET CHANNELS NETWORK ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Get UC parameter file
        QgsMessageLog.logMessage(' ==> GET UC ... ', level=QgsMessageLog.INFO)
        a2dVarData_UC = getRasterLayer(self.sFileName_UC, sVarName_UC)
        if a2dVarData_UC is not None:
            a2dVarData_UC_F = adjustVarPy2F(deepcopy(a2dVarData_UC), 'float32')
        else:
            a2dVarData_UC = zeros([a2dVarData_DEM.shape[0], a2dVarData_DEM.shape[0]])
            a2dVarData_UC[:, :] = self.dParConst_UC
            a2dVarData_UC_F = adjustVarPy2F(deepcopy(a2dVarData_UC), 'float32')

        QgsMessageLog.logMessage(' ==> GET UC ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Get UH parameter file
        QgsMessageLog.logMessage(' ==> GET UH ... ', level=QgsMessageLog.INFO)
        a2dVarData_UH = getRasterLayer(self.sFileName_UH, sVarName_UH)
        if a2dVarData_UH is not None:
            a2dVarData_UH_F = adjustVarPy2F(deepcopy(a2dVarData_UH), 'float32')
        else:
            a2dVarData_UH = zeros([a2dVarData_DEM.shape[0], a2dVarData_DEM.shape[0]])
            a2dVarData_UH[:, :] = self.dParConst_UH
            a2dVarData_UH_F = adjustVarPy2F(deepcopy(a2dVarData_UH), 'float32')

        QgsMessageLog.logMessage(' ==> GET UH ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Get SECTION file
        QgsMessageLog.logMessage(' ==> GET SECTIONS ... ', level=QgsMessageLog.INFO)
        a2oVarData_SEC = readTableFile(self.sFileName_SEC)
        QgsMessageLog.logMessage(' ==> GET SECTIONS ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Store variable(s) header
        self.oVarsHeader = a1oVarHeader
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Compute CTIME, MASK and DEMMASKED data
        QgsMessageLog.logMessage(' ==> COMPUTE CORRIVATION TIME, MASK AND DEMMASKED ... ', level=QgsMessageLog.INFO)
        if a2oVarData_SEC is not None:

            # -------------------------------------------------------------------------------------
            # Iterate over section(s)
            for iVarID_SEC in range(0, len(a2oVarData_SEC[0])):

                # Select section information
                oVarData_SEC = [oVarItem_SEC[iVarID_SEC] for oVarItem_SEC in a2oVarData_SEC]

                # Get section information
                iVarJOut_SEC = int32(oVarData_SEC[0])
                iVarIOut_SEC = int32(oVarData_SEC[1])
                sVarBasin_SEC = str(oVarData_SEC[2])
                sVarName_SEC = str(oVarData_SEC[3])
                iVarHydID_SEC = int32(oVarData_SEC[4])

                # Set section name
                sVarIdentity_SEC = sVarBasin_SEC.lower() + '_' + sVarName_SEC.lower()
                # Info section (start)
                QgsMessageLog.logMessage(' ====> ANALYZING SECTION: ' + sVarIdentity_SEC + ' ... ',
                                         level=QgsMessageLog.INFO)

                # Update variable key
                sVarName_CTIME_UPD = defineString(sVarName_CTIME, {'$section': sVarIdentity_SEC})
                self.oVarsDict[sVarName_CTIME_UPD] = {}
                self.oVarsDict[sVarName_CTIME_UPD] = deepcopy(self.oVarsDict[sVarName_CTIME])

                sVarName_MASK_UPD = defineString(sVarName_MASK, {'$section': sVarIdentity_SEC})
                self.oVarsDict[sVarName_MASK_UPD] = {}
                self.oVarsDict[sVarName_MASK_UPD] = deepcopy(self.oVarsDict[sVarName_MASK])

                sVarName_DEMMASKED_UPD = defineString(sVarName_DEMMASKED, {'$section': sVarIdentity_SEC})
                self.oVarsDict[sVarName_DEMMASKED_UPD] = {}
                self.oVarsDict[sVarName_DEMMASKED_UPD] = deepcopy(self.oVarsDict[sVarName_DEMMASKED])

                # Set section filename(s)
                sFileName_CTIME_UPD = defineString(
                    self.oVarsDict[sVarName_CTIME]['DataFile'], {'$section': sVarIdentity_SEC})
                createFolder(split(sFileName_CTIME_UPD)[0])
                sFileName_MASK_UPD = defineString(
                    self.oVarsDict[sVarName_MASK]['DataFile'], {'$section': sVarIdentity_SEC})
                createFolder(split(sFileName_MASK_UPD)[0])
                sFileName_DEMMASKED_UPD = defineString(
                    self.oVarsDict[sVarName_DEMMASKED]['DataFile'], {'$section': sVarIdentity_SEC})
                createFolder(split(sFileName_DEMMASKED_UPD)[0])

                # Set section filename(s)
                sRasterName_CTIME_UPD = defineString(
                    self.oVarsDict[sVarName_CTIME]['DataName'], {'$section': sVarIdentity_SEC})
                sRasterName_MASK_UPD = defineString(
                    self.oVarsDict[sVarName_MASK]['DataName'], {'$section': sVarIdentity_SEC})
                sRasterName_DEMMASKED_UPD = defineString(
                    self.oVarsDict[sVarName_DEMMASKED]['DataName'], {'$section': sVarIdentity_SEC})

                QgsMessageLog.logMessage(sFileName_CTIME_UPD,
                                         level=QgsMessageLog.INFO)
                QgsMessageLog.logMessage(sFileName_MASK_UPD,
                                         level=QgsMessageLog.INFO)
                QgsMessageLog.logMessage(sFileName_DEMMASKED_UPD,
                                         level=QgsMessageLog.INFO)

                time.sleep(2)

                # Compute CORRIVATION TIME data
                oProcManager = Manager()
                oProcDict = oProcManager.dict()
                self.oProcExc = Process(target=computeCorrivationTime,
                                        args=(a2dVarData_DEM_F, a2iVarData_PNT_F,
                                              a2dVarData_PDIST_F, a2iVarData_CNET_F,
                                              a2dVarData_UH_F, a2dVarData_UC_F,
                                              iVarJOut_SEC, iVarIOut_SEC, iVarHydID_SEC,
                                              oProcDict))
                self.oProcExc.start()
                self.oProcExc.join()

                a2dVarData_CTIME_F = oProcDict['CTIME']
                a2iVarData_MASK_F = oProcDict['MASK']
                a2dVarData_DEMMASKED_F = oProcDict['DEMMASKED']

                a2dVarData_CTIME = adjustVarF2Py(a2dVarData_CTIME_F, 'float32')
                a2iVarData_MASK = adjustVarF2Py(a2iVarData_MASK_F, 'int32')
                a2dVarData_DEMMASKED = adjustVarF2Py(a2dVarData_DEMMASKED_F, 'float32')

                # Save array(s) in a common workspace
                self.oVarsDict[sVarName_CTIME_UPD]['DataFile'] = deepcopy(sFileName_CTIME_UPD)
                self.oVarsDict[sVarName_CTIME_UPD]['DataName'] = deepcopy(sRasterName_CTIME_UPD)
                self.oVarsDict[sVarName_CTIME_UPD]['DataValue'] = deepcopy(a2dVarData_CTIME)
                self.oVarsDict[sVarName_MASK_UPD]['DataFile'] = deepcopy(sFileName_MASK_UPD)
                self.oVarsDict[sVarName_MASK_UPD]['DataName'] = deepcopy(sRasterName_MASK_UPD)
                self.oVarsDict[sVarName_MASK_UPD]['DataValue'] = deepcopy(a2iVarData_MASK)
                self.oVarsDict[sVarName_DEMMASKED_UPD]['DataFile'] = deepcopy(sFileName_CTIME_UPD)
                self.oVarsDict[sVarName_DEMMASKED_UPD]['DataName'] = deepcopy(sRasterName_DEMMASKED_UPD)
                self.oVarsDict[sVarName_DEMMASKED_UPD]['DataValue'] = deepcopy(a2dVarData_DEMMASKED)

                # Info section (end)
                QgsMessageLog.logMessage(' ====> ANALYZING SECTION: ' + sVarIdentity_SEC + ' ... DONE!',
                                         level=QgsMessageLog.INFO)
            # -------------------------------------------------------------------------------------

            # -------------------------------------------------------------------------------------
            # End cycle(s) over section(s)
            QgsMessageLog.logMessage(
                ' ==> COMPUTE CORRIVATION TIME, MASK AND DEMMASKED ... DONE!', level=QgsMessageLog.INFO)
            self.progress()
            # -------------------------------------------------------------------------------------
        else:

            # -------------------------------------------------------------------------------------
            pass
            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Compute watermark nested data
        QgsMessageLog.logMessage(' ==> COMPUTE WATERMARK ... ', level=QgsMessageLog.INFO)
        if a2oVarData_SEC is not None:

            QgsMessageLog.logMessage(' ==> UPDATE DICTIONARY ' + str(self.oVarsDict), level=QgsMessageLog.INFO)

            # -------------------------------------------------------------------------------------
            # Initialize watermark nested data
            a2iVarData_WTN = zeros([a2dVarData_DEM.shape[0], a2dVarData_DEM.shape[1]], dtype=int32)

            # Iterate over section(s)
            for iVarID_SEC in range(0, len(a2oVarData_SEC[0])):

                # Select section information
                oVarData_SEC = [oVarItem_SEC[iVarID_SEC] for oVarItem_SEC in a2oVarData_SEC]

                # Get section information
                iVarJOut_SEC = int32(oVarData_SEC[0])
                iVarIOut_SEC = int32(oVarData_SEC[1])
                sVarBasin_SEC = str(oVarData_SEC[2])
                sVarName_SEC = str(oVarData_SEC[3])
                iVarHydID_SEC = int32(oVarData_SEC[4])

                # Set section name
                sVarIdentity_SEC = sVarBasin_SEC.lower() + '_' + sVarName_SEC.lower()
                QgsMessageLog.logMessage(' ====> ANALYZING SECTION: ' + sVarIdentity_SEC, level=QgsMessageLog.INFO)

                # Update MASK variable name
                sVarName_MASK_UPD = defineString(sVarName_MASK, {'$section': sVarIdentity_SEC})
                # Get MASK data
                a2iVarData_MASK = self.oVarsDict[sVarName_MASK_UPD]['DataValue']

                # Compute and update nested watermark array
                a2iVarData_WTN = computeWatermarkNested(a2iVarData_WTN, a2iVarData_MASK, 0, 1)

            # Save data in a common dictionary
            self.oVarsDict[sVarName_WATERMARK]['DataValue'] = a2iVarData_WTN
            # End cycle(s) over section(s)
            QgsMessageLog.logMessage(' ==> COMPUTE WATERMARK ... DONE!', level=QgsMessageLog.INFO)
            self.progress()
            # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to stop algorithm
    def stop(self):
        if self.oProcExc:
            self.oProcExc.terminate()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to monitoring algorithm
    def progress(self):
        self.iAlgStep = self.iAlgStep + 1
        if self.callback:
            self.callback(str(self.iAlgStep))

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
