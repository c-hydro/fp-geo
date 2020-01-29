"""
Library Features:

Name:          hmc_tools_land
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20170907'
Version:       '1.0.0'
"""

# -------------------------------------------------------------------------------------
# Library
from multiprocessing import Process, Manager

from copy import deepcopy
from numpy import sqrt, nanmean
from os.path import exists

from qgis.core import *

from hmc_apps_io import setOutFolder, setVarsInfo, updateVarsInfo, readRasterFile, saveRasterFile

from hmc_apps_dataland import computeMaskDomain
from hmc_apps_dataland import computeCellArea
from hmc_apps_dataland import computeFlowDirections
from hmc_apps_dataland import computeDrainageArea
from hmc_apps_dataland import computeChannelsNetwork
from hmc_apps_dataland import computeWatertableSlopes
from hmc_apps_dataland import computeCoeffResolution

from hmc_apps_var import adjustVarF2Py, adjustVarPy2F
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Set variable(s) name
sVarName_DEM = 'DEM'
sVarName_GEOX = 'LONGITUDE'
sVarName_GEOY = 'LATITUDE'
sVarName_MASK = 'MASK'
sVarName_CAREA = 'CELLAREA'
sVarName_PNT = 'FLOW_DIRECTIONS'
sVarName_DAREA = 'DRAINAGE_AREA'
sVarName_CNET = 'CHANNELS_NETWORK'
sVarName_PDIST = 'PARTIAL_DISTANCE'
sVarName_ALPHA = 'WT_ALPHA'
sVarName_BETA = 'WT_BETA'
sVarName_CRES = 'COEFF_RESOLUTION'

iAlgStep = 0
iAlgTot = 10
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class Tool Land
class ToolLand:

    # -------------------------------------------------------------------------------------
    # Init class variable(s)
    oVarsHeader = None
    oProcExc = None
    callback = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to initialize algorithm
    def __init__(self, sFileName, sOutPath,
                 dThrAsk, dThrCRes, dThrWts,
                 iEpsgCode, sDomainName,
                 oVarsDict, callback):

        # Set class variable(s)
        self.sFileName = sFileName
        self.sOutPath = sOutPath
        self.dThrAsk = dThrAsk
        self.dThrCRes = dThrCRes
        self.dThrWts = dThrWts

        self.iEpsgCode = iEpsgCode
        self.sDomainName = sDomainName

        self.oVarsDict = oVarsDict

        self.callback = callback
        self.iAlgStep = 0

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to save algorithm result(s)
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

            # Save variable(s) to ASCII grid format
            saveRasterFile(sVar_FILENAME, oVar_DATAVALUE, oVar_HEADER, sVar_DATAFORMAT, dVar_DATAUNDEF)

        self.progress()

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to run algorithm
    def run(self):

        # -------------------------------------------------------------------------------------
        # Set output data folder
        self.sOutPath = setOutFolder(self.sFileName, self.sOutPath)
        # Set land variable(s) information
        self.oVarsDict = setVarsInfo(self.oVarsDict, self.sOutPath, self.sDomainName)
        # Info progress algorithm
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Read filename and get DEM, LONGITUDE and LATITUDE data
        QgsMessageLog.logMessage(' ==> GET DEM ... ', level=QgsMessageLog.INFO)
        [a2dVarData_DEM, a1oVarHeader,
         a2dVarData_GEOX, a2dVarData_GEOY, dVarGeoXStep, dVarGeoYStep, dVarNoData] = readRasterFile(self.sFileName)
        a2dVarData_DEM_F = adjustVarPy2F(deepcopy(a2dVarData_DEM), 'float32')
        QgsMessageLog.logMessage(' ==> GET DEM ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Compute MASK data
        QgsMessageLog.logMessage(' ==> COMPUTE MASK ... ', level=QgsMessageLog.INFO)
        a2iVarData_MASK = computeMaskDomain(a2dVarData_DEM, dVarNoData)
        QgsMessageLog.logMessage(' ==> COMPUTE MASK ... DONE!', level=QgsMessageLog.INFO)
        # Info progress algorithm
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Compute CELL_AREA data
        QgsMessageLog.logMessage(' ==> COMPUTE CELLAREA ... ', level=QgsMessageLog.INFO)
        a2dVarData_CAREA = computeCellArea(a2dVarData_GEOY, dVarGeoXStep, dVarGeoYStep)
        dVarAvg_CAREA = sqrt(nanmean(a2dVarData_CAREA))
        a2dVarData_CAREA_F = adjustVarPy2F(deepcopy(a2dVarData_CAREA), 'float32')
        QgsMessageLog.logMessage(' ==> COMPUTE CELLAREA ... DONE!', level=QgsMessageLog.INFO)
        # Info progress algorithm
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Compute FLOW_DIRECTIONS data
        QgsMessageLog.logMessage(' ==> COMPUTE FLOW DIRECTIONS ... ', level=QgsMessageLog.INFO)

        oProcManager = Manager()
        oProcDict = oProcManager.dict()
        self.oProcExc = Process(target=computeFlowDirections, args=(a2dVarData_DEM_F, oProcDict))
        self.oProcExc.start()
        self.oProcExc.join()

        a2iVarData_PNT_F = oProcDict['PNT']
        a2iVarData_PNT = adjustVarF2Py(a2iVarData_PNT_F, 'int32')

        QgsMessageLog.logMessage(' ==> COMPUTE FLOW DIRECTIONS ... DONE!', level=QgsMessageLog.INFO)
        # Info progress algorithm
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Compute DRAINAGE AREA data
        QgsMessageLog.logMessage(' ==> COMPUTE DRAINAGE AREA ... ', level=QgsMessageLog.INFO)

        oProcManager = Manager()
        oProcDict = oProcManager.dict()
        self.oProcExc = Process(target=computeDrainageArea, args=(a2dVarData_DEM_F, a2iVarData_PNT_F, oProcDict))
        self.oProcExc.start()
        self.oProcExc.join()

        a2iVarData_DAREA_F = oProcDict['DAREA']

        a2iVarData_DAREA = adjustVarF2Py(a2iVarData_DAREA_F, 'int32')
        QgsMessageLog.logMessage(' ==> COMPUTE DRAINAGE AREA ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Compute CHANNELS NETWORK and PARTIAL DISTANCE
        QgsMessageLog.logMessage(' ==> COMPUTE CHANNELS NETWORK AND PARTIAL DISTANCE ... ', level=QgsMessageLog.INFO)

        oProcManager = Manager()
        oProcDict = oProcManager.dict()
        self.oProcExc = Process(target=computeChannelsNetwork, args=(a2dVarData_DEM_F, a2iVarData_PNT_F,
                                                                     a2iVarData_DAREA_F,
                                                                     dVarAvg_CAREA, self.dThrAsk, oProcDict))
        self.oProcExc.start()
        self.oProcExc.join()

        a2iVarData_CNET_F = oProcDict['CNET']
        a2dVarData_PDIST_F = oProcDict['PDIST']

        a2iVarData_CNET = adjustVarF2Py(a2iVarData_CNET_F, 'int32')
        a2dVarData_PDIST = adjustVarF2Py(a2dVarData_PDIST_F, 'float32')
        QgsMessageLog.logMessage(' ==> COMPUTE CHANNELS NETWORK AND PARTIAL DISTANCE ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Compute ALPHA and BETA data
        QgsMessageLog.logMessage(' ==> COMPUTE ALPHA AND BETA ... ', level=QgsMessageLog.INFO)

        oProcManager = Manager()
        oProcDict = oProcManager.dict()
        self.oProcExc = Process(target=computeWatertableSlopes, args=(a2dVarData_DEM_F, a2iVarData_PNT_F,
                                                                      a2iVarData_CNET_F, a2iVarData_DAREA_F,
                                                                      self.dThrWts, oProcDict))
        self.oProcExc.start()
        self.oProcExc.join()

        a2dVarData_ALPHA_F = oProcDict['ALPHA']
        a2dVarData_BETA_F = oProcDict['BETA']

        a2dVarData_ALPHA = adjustVarF2Py(a2dVarData_ALPHA_F, 'float64')
        a2dVarData_BETA = adjustVarF2Py(a2dVarData_BETA_F, 'float64')
        QgsMessageLog.logMessage(' ==> COMPUTE ALPHA AND BETA ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Compute COEFF RESOLUTION data
        QgsMessageLog.logMessage(' ==> COMPUTE COEFF RESOLUTION ... ', level=QgsMessageLog.INFO)

        oProcManager = Manager()
        oProcDict = oProcManager.dict()
        self.oProcExc = Process(target=computeCoeffResolution, args=(a2dVarData_DEM_F, a2iVarData_DAREA_F,
                                                                     a2iVarData_CNET_F, a2dVarData_CAREA_F,
                                                                     self.dThrCRes, oProcDict))
        self.oProcExc.start()
        self.oProcExc.join()

        a2dVarData_CRES_F = oProcDict['CRES']

        a2dVarData_CRES = adjustVarF2Py(a2dVarData_CRES_F, 'float32')
        QgsMessageLog.logMessage(' ==> COMPUTE COEFF RESOLUTION ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Update variable(s) in a common workspace
        oDictVarName = {'Var_01': sVarName_DEM, 'Var_02': sVarName_GEOX, 'Var_03': sVarName_GEOY,
                        'Var_04': sVarName_MASK,'Var_05': sVarName_CAREA, 'Var_06': sVarName_PNT,
                        'Var_07': sVarName_DAREA, 'Var_08': sVarName_CNET, 'Var_09': sVarName_PDIST,
                        'Var_10': sVarName_ALPHA, 'Var_11': sVarName_BETA, 'Var_12': sVarName_CRES,
                        }
        oDictVarValue = {'Var_01': a2dVarData_DEM, 'Var_02': a2dVarData_GEOX, 'Var_03': a2dVarData_GEOY,
                        'Var_04': a2iVarData_MASK,'Var_05': a2dVarData_CAREA, 'Var_06': a2iVarData_PNT,
                        'Var_07': a2iVarData_DAREA, 'Var_08': a2iVarData_CNET, 'Var_09': a2dVarData_PDIST,
                        'Var_10': a2dVarData_ALPHA, 'Var_11': a2dVarData_BETA, 'Var_12': a2dVarData_CRES
                         }
        # Update variable(s) information
        self.oVarsDict = updateVarsInfo(self.oVarsDict, oDictVarName, oDictVarValue, 'DataValue')
        self.oVarsHeader = a1oVarHeader
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
