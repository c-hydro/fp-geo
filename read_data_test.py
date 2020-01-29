# --------------------------------------------------------------------------------------------------------------
# Library
from hmc_apps_io_ascii import openFile, closeFile, readArcGrid, writeArcGrid, readTable, writeTable
from hmc_apps_geo import Km2Deg, defineGeoGrid, readGeoHeader, defineGeoCorner, defineGeoHeader, resampleGeoGrid

from hmc_op_interpolation import interpVarGridNN

from copy import deepcopy
from numpy import linspace, meshgrid, flipud, min, nan

from hmc_apps_var import adjustVarF2Py, adjustVarPy2F

from hmc_apps_dataland import computeMaskDomain
from hmc_apps_dataland import computeCellArea
from hmc_apps_dataland import computeFlowDirections
from hmc_apps_dataland import computeDrainageArea
from hmc_apps_dataland import computeChannelsNetwork
from hmc_apps_dataland import computeWatertableSlopes
from hmc_apps_dataland import computeCoeffResolution

import matplotlib.pylab as plt
# --------------------------------------------------------------------------------------------------------------

# writeArcGrid(oFile, a2dVarData, a1oVarHeader, sDataFormat=None, dNoData=None):

# --------------------------------------------------------------------------------------------------------------
# Info
sFileName_CN = '/home/fabio/Desktop/data_barbados/barbados_cn.txt'

#sFileName_DEM = '/home/fabio/Desktop/data_barbados/barbados_dem.txt'
sFileName_DEM = '/home/fabio/Desktop/data_barbados/10m/barbados.dem.gcp.txt'
sFileName_CN_REGRID = '/home/fabio/Desktop/data_barbados/10m/barbados.cn.gcp.txt'
dResValue = float(90)
# --------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------
# Open file handle
oFileHandle = openFile(sFileName_CN, 'r')
# Read file
[a2iDataCN, a1oHeaderCN] = readArcGrid(oFileHandle)

# Open file handle
oFileHandle = openFile(sFileName_DEM, 'r')
# Read file
[a2dDataDEM, a1oHeaderDEM] = readArcGrid(oFileHandle)
# --------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------
# Define ancillary data information CN
[iRowsCN, iColsCN, dGeoXMinCN, dGeoYMinCN, dGeoXStepCN, dGeoYStepCN, dNoDataCN] = readGeoHeader(a1oHeaderCN)
[dGeoXMinCN, dGeoXMaxCN, dGeoYMinCN, dGeoYMaxCN] = defineGeoCorner(dGeoXMinCN, dGeoYMinCN, dGeoXStepCN, dGeoYStepCN, iColsCN, iRowsCN)
[a2dGeoXCN, a2dGeoYCN, a1dGeoBoxCN] = defineGeoGrid(dGeoYMinCN, dGeoXMinCN, dGeoYMaxCN, dGeoXMaxCN, dGeoYStepCN, dGeoXStepCN)

# Define ancillary data information DEM
[iRowsDEM, iColsDEM, dGeoXMinDEM, dGeoYMinDEM, dGeoXStepDEM, dGeoYStepDEM, dNoDataDEM] = readGeoHeader(a1oHeaderDEM)
[dGeoXMinDEM, dGeoXMaxDEM, dGeoYMinDEM, dGeoYMaxDEM] = defineGeoCorner(dGeoXMinDEM, dGeoYMinDEM, dGeoXStepDEM, dGeoYStepDEM, iColsDEM, iRowsDEM)
[a2dGeoXDEM, a2dGeoYDEM, a1dGeoBoxDEM] = defineGeoGrid(dGeoYMinDEM, dGeoXMinDEM, dGeoYMaxDEM, dGeoXMaxDEM, dGeoYStepDEM, dGeoXStepDEM)
# --------------------------------------------------------------------------------------------------------------


a2iDataCN_REGRID = interpVarGridNN(a2dGeoXDEM, a2dGeoYDEM, a2iDataCN, a2dGeoXCN, a2dGeoYCN, dNoData_OUT=-9999)

oFileHandle = openFile(sFileName_CN_REGRID, 'w')
writeArcGrid(oFileHandle, a2iDataCN_REGRID, a1oHeaderDEM, sDataFormat='i', dNoData=-9999)

print('ciao')

[a2dGeoX_UPD, a2dGeoY_UPD, a1oVarHeader_UPD] = resampleGeoGrid(a2dGeoX, a2dGeoY,
                                                               dResValue/1000, bGeoStepDegree=False, dNoData=-9999.0)

# --------------------------------------------------------------------------------------------------------------
# Set cellsize
dGeoXStep_UPD = Km2Deg(dResValue/1000)
dGeoYStep_UPD = Km2Deg(dResValue/1000)

# Compute updated Rows (iI) and Cols (iJ)
iCols_UPD = int(abs(dGeoXMax - dGeoXMin) / dGeoYStep_UPD)
iRows_UPD = int(abs(dGeoYMax - dGeoYMin) / dGeoXStep_UPD)

# Comptue updated geographical information
a1dGeoX_UPD = linspace(dGeoXMin, dGeoXMax, iCols_UPD, endpoint=True)
a1dGeoY_UPD = linspace(dGeoYMin, dGeoYMax, iRows_UPD, endpoint=True)
a2dGeoX_UPD, a2dGeoY_UPD = meshgrid(a1dGeoX_UPD, a1dGeoY_UPD)
a2dGeoY_UPD = flipud(a2dGeoY_UPD)

# Update general information
dGeoXMin_UPD = min(a2dGeoX_UPD)
dGeoYMin_UPD = min(a2dGeoY_UPD)
dNoData_UPD = dNoData

# Create data header information
a1oVarHeader = defineGeoHeader(iRows_UPD, iCols_UPD, dGeoXMin_UPD, dGeoYMin_UPD,
                               dGeoXStep_UPD, dGeoYStep_UPD, dNoData_UPD)
# Compute data values based on updated features
a2dData_UPD = interpVarGridNN(a2dGeoX_UPD, a2dGeoY_UPD, a2dData,a2dGeoX, a2dGeoY, dNoData_OUT=dNoData_UPD)
# --------------------------------------------------------------------------------------------------------------

a2dVarData_DEM_F = adjustVarPy2F(deepcopy(a2dData_UPD), 'float32')
a2iVarData_PNT_F = computeFlowDirections(a2dVarData_DEM_F)



#plt.figure(1)
#plt.imshow(a2dVarData_DEM_F_GRAPH); plt.colorbar()
#plt.figure(2)
#plt.imshow(a2iVarData_PNT_F_GRAPH); plt.colorbar()
#plt.show()


a2iVarData_DAREA_F = computeDrainageArea(a2dVarData_DEM_F, a2iVarData_PNT_F)


a2dVarData_DEM_F_GRAPH = deepcopy(a2dVarData_DEM_F)
a2iVarData_PNT_F_GRAPH = deepcopy(a2iVarData_PNT_F)
a2iVarData_DAREA_F_GRAPH = deepcopy(a2iVarData_DAREA_F)

a2dVarData_DEM_F_GRAPH[a2dVarData_DEM_F_GRAPH == dNoData_UPD] = nan
a2iVarData_PNT_F_GRAPH[a2iVarData_PNT_F_GRAPH == dNoData_UPD] = 0
a2iVarData_DAREA_F_GRAPH[a2iVarData_DAREA_F_GRAPH == dNoData_UPD] = 0

plt.figure(1)
plt.imshow(a2dVarData_DEM_F_GRAPH); plt.colorbar()
plt.figure(2)
plt.imshow(a2iVarData_PNT_F_GRAPH); plt.colorbar()
plt.figure(3)
plt.imshow(a2iVarData_DAREA_F_GRAPH); plt.colorbar()
plt.show()

print('ciao')







# --------------------------------------------------------------------------------------------------------------
a2dData_UPD[a2dData_UPD == dNoData_UPD] = nan
a2dData[a2dData == dNoData] = nan

plt.figure(1)
plt.imshow(a2dData_UPD); plt.colorbar()
plt.figure(2)
plt.imshow(a2dData); plt.colorbar()
plt.show()

print('ciao1')

plt.figure(3)
plt.imshow(a2dGeoX_UPD); plt.colorbar()
plt.figure(4)
plt.imshow(a2dGeoY_UPD); plt.colorbar()
plt.figure(5)
plt.imshow(a2dGeoX); plt.colorbar()
plt.figure(6)
plt.imshow(a2dGeoY); plt.colorbar()
plt.show()

print('ciao2')
# --------------------------------------------------------------------------------------------------------------
