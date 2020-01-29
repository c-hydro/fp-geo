"""
Library Features:

Name:          hmc_apps_parameters
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20170926'
Version:       '2.0.1'
"""

#######################################################################################

# -------------------------------------------------------------------------------------
# Library
from numpy import zeros, float32, int32, where
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to define default parameter map
def defineParamsMapDefault(a2dVarIN, dVarConst):
    a2dVarOUT = zeros([a2dVarIN.shape[0], a2dVarIN.shape[1]])
    a2dVarOUT[:, :] = float32(dVarConst)
    return a2dVarOUT
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to compute constant parameter maps
def computeParamsMapConstant(a2dVarPAR, a2bVarNaN=None, dVarND=-9999):
    if a2bVarNaN is not None:
        a2dVarPAR[a2bVarNaN] = dVarND
    return a2dVarPAR
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to compute distributed parameter maps
def computeParamsMapDistributed(a2dVarPAR, a2iVarWM, a2dVarLink, a2bVarNaN=None, dVarND=-9999):

    # Iterating over values
    for iIndex in range(a2dVarLink.shape[0]):
        # Get parameter(s) and code(s)
        dVarPAR = float32(a2dVarLink[iIndex, 0])
        iVarWM = int32(a2dVarLink[iIndex, 1])
        # Create distributed parameter(s) map
        a2bVarIndex = where(a2iVarWM == int32(iVarWM))
        a2dVarPAR[a2bVarIndex[0], a2bVarIndex[1]] = float32(dVarPAR)

    if a2bVarNaN is not None:
        a2dVarPAR[a2bVarNaN] = dVarND

    return a2dVarPAR
# -------------------------------------------------------------------------------------
