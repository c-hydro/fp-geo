"""
Library Features:

Name:          hmc_op_interpolation
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20171205'
Version:       '1.0.0'
"""

# --------------------------------------------------------------------------------
# Libraries
from numpy import arange, max, nanmax, min, nanmin, unravel_index, reshape, around, nan

from scipy.interpolate import griddata
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to interpolate grid index using NN
def interpIndexGridNN(oGeoX_IN, oGeoY_IN, oGeoX_OUT, oGeoY_OUT):
    a2dGeoX_IN = oGeoX_IN
    a2dGeoY_IN = oGeoY_IN
    a2dGeoX_OUT = oGeoX_OUT
    a2dGeoY_OUT = oGeoY_OUT

    iGeoDim_IN = a2dGeoX_IN.shape[0] * a2dGeoY_IN.shape[1]

    a1iGeoVal_IN = arange(0, iGeoDim_IN)

    a2iIndex_OUT = griddata((a2dGeoX_IN.ravel(), a2dGeoY_IN.ravel()), a1iGeoVal_IN,
                            (a2dGeoX_OUT, a2dGeoY_OUT),
                            method='nearest')

    return a2iIndex_OUT

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to interpolate grid Data using NN
def interpVarGridNN(oGeoX_OUT, oGeoY_OUT,
                    oData_IN, oGeoX_IN, oGeoY_IN,
                    dNoData_OUT=nan, a2iIndex_OUT=None, bGeoCut_OUT=False):

    # Retrieve variable information
    a2dGeoXVar = oGeoX_IN
    a2dGeoYVar = oGeoY_IN
    a2dDataVar = oData_IN

    # Retrieve reference information
    a2dGeoXRef = oGeoX_OUT
    a2dGeoYRef = oGeoY_OUT

    # Cut geo domain for avoiding large griddata interpolation (set bGeoCut==True)
    if bGeoCut_OUT:
        dGeoXRefMax = nanmax(a2dGeoXRef)
        dGeoXRefMin = nanmin(a2dGeoXRef)
        dGeoYRefMax = nanmax(a2dGeoYRef)
        dGeoYRefMin = nanmin(a2dGeoYRef)

        # UPPER RIGHT CORNER
        oURCorner = abs(a2dGeoYVar - dGeoYRefMax) + abs(a2dGeoXVar - dGeoXRefMax)
        iURIndexI, iURIndexJ = unravel_index(oURCorner.argmin(), oURCorner.shape, order='C')
        # LOWER RIGHT CORNER
        oLRCorner = abs(a2dGeoYVar - dGeoYRefMin) + abs(a2dGeoXVar - dGeoXRefMax)
        iLRIndexI, iLRIndexJ = unravel_index(oLRCorner.argmin(), oLRCorner.shape, order='C')
        # UPPER LEFT CORNER
        oULCorner = abs(a2dGeoYVar - dGeoYRefMax) + abs(a2dGeoXVar - dGeoXRefMin)
        iULIndexI, iULIndexJ = unravel_index(oULCorner.argmin(), oULCorner.shape, order='C')
        # LOWER LEFT CORNER
        oLLCorner = abs(a2dGeoYVar - dGeoYRefMin) + abs(a2dGeoXVar - dGeoXRefMin)
        iLLIndexI, iLLIndexJ = unravel_index(oLLCorner.argmin(), oLLCorner.shape, order='C')

        iIndexIMax = max([iURIndexI, iLRIndexI, iULIndexI, iLLIndexI])
        iIndexIMin = min([iURIndexI, iLRIndexI, iULIndexI, iLLIndexI])
        iIndexJMax = max([iURIndexJ, iLRIndexJ, iULIndexJ, iLLIndexJ])
        iIndexJMin = min([iURIndexJ, iLRIndexJ, iULIndexJ, iLLIndexJ])

        a2dGeoXVar_SUB = a2dGeoXVar[iIndexIMin:iIndexIMax, iIndexJMin:iIndexJMax]
        a2dGeoYVar_SUB = a2dGeoYVar[iIndexIMin:iIndexIMax, iIndexJMin:iIndexJMax]
        a2dDataVar_SUB = a2dDataVar[iIndexIMin:iIndexIMax, iIndexJMin:iIndexJMax]

    else:
        a2dGeoXVar_SUB = a2dGeoXVar
        a2dGeoYVar_SUB = a2dGeoYVar
        a2dDataVar_SUB = a2dDataVar

    # GridNN methods (or griddata or using indexes)
    if a2iIndex_OUT is not None:

        a1dDataVarRegrid = a2dDataVar_SUB.ravel()[a2iIndex_OUT.ravel()]
        a2dDataVarRegrid = reshape(a1dDataVarRegrid, [a2dGeoXRef.shape[0], a2dGeoYRef.shape[1]])

    else:
        a2dDataVarRegrid = griddata((a2dGeoXVar_SUB.ravel(), a2dGeoYVar_SUB.ravel()), a2dDataVar_SUB.ravel(),
                                    (a2dGeoXRef, a2dGeoYRef),
                                    method='nearest', fill_value=dNoData_OUT)

    # Round re-gridded variable
    a2dDataVarRegrid = around(a2dDataVarRegrid, decimals=3)

    # Return results
    return a2dDataVarRegrid
    # --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
