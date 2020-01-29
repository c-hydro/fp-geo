"""
Library Features:

Name:          hmc_tools_parameters
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20170925'
Version:       '1.0.0'
"""

# -------------------------------------------------------------------------------------
# Library
from numpy import asarray, transpose, vstack, float32, int32
from os.path import exists

from qgis.core import *

from hmc_apps_parameters import computeParamsMapDistributed, computeParamsMapConstant, defineParamsMapDefault

from hmc_apps_io import setOutFolder, setVarsInfo, \
    updateVarsInfo, readRasterFile, saveRasterFile, getRasterLayer, \
    readTableFile
from hmc_apps_geo import defineGeoIndex
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Set variable(s) name
sVarName_DEM = 'DEM'
sVarName_WATERMARK = 'WATERMARK'
sVarName_PARAM = 'PARAMETERS'
sVarName_CT = 'CT'
sVarName_CF = 'CF'
sVarName_UC = 'UC'
sVarName_UH = 'UH'
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class Tool Parameters
class ToolParameters:

    # -------------------------------------------------------------------------------------
    # Init class variable(s)
    oVarsHeader = None
    oProcExc = None
    callback = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to initialize algorithm
    def __init__(self, sFileName_DEM, sFileName_WATERMARK, sFileName_PARAMETERS,
                 sOutPath,
                 dParConst_CT, dParConst_CF, dParConst_UC, dParConst_UH,
                 iEpsgCode, sDomainName,
                 oVarsDict, callback):

        # Set class variable(s)
        self.sFileName_DEM = sFileName_DEM
        self.sFileName_WATERMARK = sFileName_WATERMARK
        self.sFileName_PARAMETERS = sFileName_PARAMETERS

        self.sOutPath = sOutPath
        self.dParConst_CT = dParConst_CT
        self.dParConst_CF = dParConst_CF
        self.dParConst_UC = dParConst_UC
        self.dParConst_UH = dParConst_UH

        self.iEpsgCode = iEpsgCode
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
            QgsMessageLog.logMessage(' ====> KEY: ' + sVar_Key, level=QgsMessageLog.INFO)

            # Save variable(s) to ASCII grid format
            saveRasterFile(sVar_FILENAME, oVar_DATAVALUE, oVar_HEADER, sVar_DATAFORMAT, dVar_DATAUNDEF)

            QgsMessageLog.logMessage(' ====> SAVE FILENAME: ' + sVar_FILENAME + ' END!', level=QgsMessageLog.INFO)

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

        a2bGeoDataNaN = defineGeoIndex(a2dVarData_DEM, dVarNoData)[0]

        QgsMessageLog.logMessage(' ==> GET DEM ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Get FlowDirections file
        QgsMessageLog.logMessage(' ==> GET WATERMARK ... ', level=QgsMessageLog.INFO)
        a2iVarData_WATERMARK = getRasterLayer(self.sFileName_WATERMARK, sVarName_WATERMARK)
        QgsMessageLog.logMessage(' ==> GET WATERMARK ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Get PARAMETERS file
        QgsMessageLog.logMessage(' ==> GET PARAMETERS ... ', level=QgsMessageLog.INFO)
        a2oVarData_PARAM = readTableFile(self.sFileName_PARAMETERS, 1)
        QgsMessageLog.logMessage(' ==> GET PARAMETERS ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Compute look-up table for CT parameter
        QgsMessageLog.logMessage(' ==> COMPUTE CT ... ', level=QgsMessageLog.INFO)
        a2oVarLink_CT = defineMapLookUp(a2oVarData_PARAM, 3)
        # Compute CT data
        a2dVarData_CT = assignMapValue(a2dVarData_DEM, a2iVarData_WATERMARK,
                                         a2bGeoDataNaN, a2oVarLink_CT,
                                         self.dParConst_CT, dVarNoData)
        QgsMessageLog.logMessage(' ==> COMPUTE CT ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Compute look-up table for CF parameter
        QgsMessageLog.logMessage(' ==> COMPUTE CF ... ', level=QgsMessageLog.INFO)
        a2oVarLink_CF = defineMapLookUp(a2oVarData_PARAM, 4)
        # Compute CF data
        a2dVarData_CF = assignMapValue(a2dVarData_DEM, a2iVarData_WATERMARK,
                                         a2bGeoDataNaN, a2oVarLink_CF,
                                         self.dParConst_CF, dVarNoData)
        QgsMessageLog.logMessage(' ==> COMPUTE CT ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Compute look-up table for UC parameter
        QgsMessageLog.logMessage(' ==> COMPUTE UC ... ', level=QgsMessageLog.INFO)
        a2oVarLink_UC = defineMapLookUp(a2oVarData_PARAM, 1)
        # Compute UC data
        a2dVarData_UC = assignMapValue(a2dVarData_DEM, a2iVarData_WATERMARK,
                                         a2bGeoDataNaN, a2oVarLink_UC,
                                         self.dParConst_UC, dVarNoData)
        QgsMessageLog.logMessage(' ==> COMPUTE UC ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Compute look-up table for UH parameter
        QgsMessageLog.logMessage(' ==> COMPUTE UH ... ', level=QgsMessageLog.INFO)
        a2oVarLink_UH = defineMapLookUp(a2oVarData_PARAM, 2)
        # Compute UH data
        a2dVarData_UH = assignMapValue(a2dVarData_DEM, a2iVarData_WATERMARK,
                                         a2bGeoDataNaN, a2oVarLink_UH,
                                         self.dParConst_UH, dVarNoData)
        QgsMessageLog.logMessage(' ==> COMPUTE UH ... DONE!', level=QgsMessageLog.INFO)
        self.progress()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Update variable(s) in a common workspace
        oDictVarName = {'Var_01': sVarName_CF, 'Var_02': sVarName_CT,
                        'Var_03': sVarName_UC, 'Var_04': sVarName_UH
                        }
        oDictVarValue = {'Var_01': a2dVarData_CF, 'Var_02': a2dVarData_CT,
                         'Var_03': a2dVarData_UC, 'Var_04': a2dVarData_UH,
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

# -------------------------------------------------------------------------------------
# Method to define look-up table between domain parameter(s) and code(s)
def defineMapLookUp(a2oVarData_PARAM, iVarData_Idx):

    if a2oVarData_PARAM is not None:
        a1dVarData_PARAM = asarray(a2oVarData_PARAM[iVarData_Idx], dtype=float32)
        a1iVarData_CODE = asarray(a2oVarData_PARAM[0], dtype=int32)
        # Create link data
        a2oVarData_LINK = transpose(vstack((a1dVarData_PARAM, a1iVarData_CODE)))
    else:
        a2oVarData_LINK = None

    return a2oVarData_LINK
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to assign values to map
def assignMapValue(a2dVarData, a2iVarWM, a2bVarNan, a2oVarParam, dConstParam, dNoData=-9999):

    if a2oVarParam is not None:
        # Distributed method
        a2dVarMap = defineParamsMapDefault(a2dVarData, dConstParam)
        a2dVarMap = computeParamsMapConstant(a2dVarMap, a2bVarNan, dNoData)
        a2dVarMap = computeParamsMapDistributed(a2dVarMap, a2iVarWM, a2oVarParam, a2bVarNan, dNoData)
    else:
        # Constant method
        a2dVarMap = defineParamsMapDefault(a2dVarData, dConstParam)
        a2dVarMap = computeParamsMapConstant(a2dVarMap, a2bVarNan, dNoData)

    return a2dVarMap
# -------------------------------------------------------------------------------------
