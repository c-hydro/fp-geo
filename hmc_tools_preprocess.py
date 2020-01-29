"""
Library Features:

Name:          hmc_tools_preprocess
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20171214'
Version:       '1.0.1'
"""

# -------------------------------------------------------------------------------------
# Library
from multiprocessing import Process, Manager

from copy import deepcopy
from os.path import exists

from qgis.core import *

from hmc_apps_io import setOutFolder, setVarsInfo, updateVarsInfo, readRasterFile, saveRasterFile
from hmc_apps_geo import resampleGeoGrid
from hmc_op_interpolation import interpVarGridNN
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Set variable(s) name
sVarName_DEM = 'DEM'
sVarName_CN = 'CN'
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class Tool PreProcess
class ToolPreProcess:

    # -------------------------------------------------------------------------------------
    # Init class variable(s)
    oVarsHeader = None
    oProcExc = None
    callback = None
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to initialize algorithm
    def __init__(self, sFileName_DEM, sFileName_CN,
                 bMaskDEM=None, bMaskCN=None, bWarpDEM=None, bWarpCN=None, dResValue=None,
                 sOutPath='', iEpsgCode=4326, sDomainName='', oVarsDict=None, callback=None):

        # Set class variable(s)
        self.sFileName_DEM = sFileName_DEM
        self.sFileName_CN = sFileName_CN

        self.bMaskDEM = bMaskDEM
        self.bMaskCN = bMaskCN
        self.bWarpDEM = bWarpDEM
        self.bWarpCN = bWarpCN
        self.dResValue = dResValue

        self.sOutPath = sOutPath
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

            QgsMessageLog.logMessage(' ==> header in save ' + str(sVar_FILENAME), level=QgsMessageLog.INFO)

            # Set temporary file if needed to save previous computation
            if exists(sVar_FILENAME):
                sVar_FILENAME = sVar_FILENAME + '_TEMP_'

            # Save variable(s) to ASCII grid format
            if oVar_DATAVALUE is not None:
                saveRasterFile(sVar_FILENAME, oVar_DATAVALUE, oVar_HEADER, sVar_DATAFORMAT, dVar_DATAUNDEF)

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to run algorithm
    def run(self):

        # -------------------------------------------------------------------------------------
        # Set output data folder
        self.sOutPath = setOutFolder(self.sFileName_DEM, self.sOutPath)
        # Set land variable(s) information
        self.oVarsDict = setVarsInfo(self.oVarsDict, self.sOutPath, self.sDomainName)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Read filename and get DEM
        QgsMessageLog.logMessage(' ==> GET DEM ... ', level=QgsMessageLog.INFO)
        [a2dVarDEM_VALUE, a1oVarDEM_HEADER, a2dVarDEM_GEOX, a2dVarDEM_GEOY,
         dVarDEM_GEOXSTEP, dVarDEM_GEOYSTEP, dVarDEM_NODATA] = readRasterFile(self.sFileName_DEM)
        QgsMessageLog.logMessage(' ==> GET DEM ... DONE!', level=QgsMessageLog.INFO)
        # Read filename and get CN
        QgsMessageLog.logMessage(' ==> GET CN ... ', level=QgsMessageLog.INFO)
        [a2dVarCN_VALUE, a1oVarCN_HEADER, a2dVarCN_GEOX, a2dVarCN_GEOY,
         dVarCN_GEOXSTEP, dVarCN_GEOYSTEP, dVarCN_NODATA] = readRasterFile(self.sFileName_CN)
        QgsMessageLog.logMessage(' ==> GET CN ... DONE!', level=QgsMessageLog.INFO)

        a2dVarDEM_VALUE_CMP = None
        a2dVarCN_VALUE_CMP = None
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Init process manager (not used in preprocess tool)
        oProcManager = Manager()
        self.oProcExc = Process()
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Mask data
        if self.bMaskDEM is True:
            a2dVarCN_VALUE[a2dVarDEM_VALUE == dVarDEM_NODATA] = dVarCN_NODATA
            a1oVarHeader_CMP = a1oVarDEM_HEADER
            a2dVarCN_VALUE_CMP = deepcopy(a2dVarCN_VALUE)
            a2dVarDEM_VALUE_CMP = deepcopy(a2dVarDEM_VALUE)
        elif self.bMaskCN is True:
            a2dVarDEM_VALUE[a2dVarCN_VALUE == dVarCN_NODATA] = dVarDEM_NODATA
            a1oVarHeader_CMP = a1oVarCN_HEADER
            a2dVarDEM_VALUE_CMP = deepcopy(a2dVarDEM_VALUE)
            a2dVarCN_VALUE_CMP = deepcopy(a2dVarCN_VALUE)
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Warp data
        if self.bWarpDEM is True:

            QgsMessageLog.logMessage(' ==> warp over dem start! ' + str(self.bWarpDEM), level=QgsMessageLog.INFO)
            if a2dVarDEM_VALUE_CMP is None:
                a2dVarDEM_VALUE_CMP = deepcopy(a2dVarDEM_VALUE)
            if a2dVarCN_VALUE_CMP is not None:
                a2dVarCN_VALUE = deepcopy(a2dVarCN_VALUE_CMP)

            a2dVarCN_VALUE_CMP = interpVarGridNN(a2dVarDEM_GEOX, a2dVarDEM_GEOY,
                                                  a2dVarCN_VALUE, a2dVarCN_GEOX, a2dVarCN_GEOY,
                                                  dNoData_OUT=a1oVarCN_HEADER['NODATA_value'])
            a1oVarHeader_CMP = a1oVarDEM_HEADER

            QgsMessageLog.logMessage(' ==> warp over dem end!', level=QgsMessageLog.INFO)

        elif self.bWarpCN is True:
            if a2dVarCN_VALUE_CMP is None:
                a2dVarCN_VALUE_CMP = deepcopy(a2dVarCN_VALUE)
            if a2dVarDEM_VALUE_CMP is not None:
                a2dVarDEM_VALUE = deepcopy(a2dVarDEM_VALUE_CMP)

            a2dVarDEM_VALUE_CMP = interpVarGridNN(a2dVarCN_GEOX, a2dVarCN_GEOY,
                                                  a2dVarDEM_VALUE, a2dVarDEM_GEOX, a2dVarDEM_GEOY,
                                                  dNoData_OUT=a1oVarDEM_HEADER['NODATA_value'])
            a1oVarHeader_CMP = a1oVarCN_HEADER
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Rescale data
        if self.dResValue is not None:

            if a2dVarCN_VALUE_CMP is not None:
                a2dVarCN_VALUE = deepcopy(a2dVarCN_VALUE_CMP)
            if a2dVarDEM_VALUE_CMP is not None:
                a2dVarDEM_VALUE = deepcopy(a2dVarDEM_VALUE_CMP)

            # Get resolution value
            dResValue = float(self.dResValue)

            # Rescale DEM data
            [a2dVarDEM_GEOX_UPD, a2dVarDEM_GEOY_UPD,
             a1oVarHeader_UPD] = resampleGeoGrid(a2dVarDEM_GEOX, a2dVarDEM_GEOY,
                                                 dResValue/1000, bGeoStepDegree=False, dNoData=-9999.0)

            a2dVarDEM_VALUE_CMP = interpVarGridNN(a2dVarDEM_GEOX_UPD, a2dVarDEM_GEOY_UPD,
                                                  a2dVarDEM_VALUE, a2dVarDEM_GEOX, a2dVarDEM_GEOY,
                                                  dNoData_OUT=a1oVarHeader_UPD['NODATA_value'])
            # Rescale CN data
            [a2dVarCN_GEOX_UPD, a2dVarCN_GEOY_UPD,
             a1oVarHeader_UPD] = resampleGeoGrid(a2dVarCN_GEOX, a2dVarCN_GEOY,
                                                 dResValue/1000, bGeoStepDegree=False, dNoData=-9999.0)

            a2dVarCN_VALUE_CMP = interpVarGridNN(a2dVarCN_GEOX_UPD, a2dVarCN_GEOY_UPD,
                                                  a2dVarCN_VALUE, a2dVarCN_GEOX, a2dVarCN_GEOY,
                                                  dNoData_OUT=a1oVarHeader_UPD['NODATA_value'])
            # Define Header data
            a1oVarHeader_CMP = a1oVarHeader_UPD
        # -------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------
        # Update variable(s) in a common workspace
        oDictVarName = {'Var_01': sVarName_DEM, 'Var_02': sVarName_CN}
        oDictVarValue = {'Var_01': a2dVarDEM_VALUE_CMP, 'Var_02': a2dVarCN_VALUE_CMP}
        # Update variable(s) information
        self.oVarsDict = updateVarsInfo(self.oVarsDict, oDictVarName, oDictVarValue, 'DataValue')
        self.oVarsHeader = a1oVarHeader_CMP

        QgsMessageLog.logMessage(' ==> header! ' + str(self.oVarsHeader), level=QgsMessageLog.INFO)
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
