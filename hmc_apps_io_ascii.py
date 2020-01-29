"""
Library Features:

Name:          hmc_apps_io_ascii
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20170907'
Version:       '2.0.1'
"""
# --------------------------------------------------------------------------------
# Library
import numpy as np
from time import sleep
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to open ASCII file (in read or write mode)
def openFile(sFileName, sFileMode):
    try:
        oFile = open(sFileName, sFileMode)
        return oFile
    except IOError as oError:
        pass
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to close ASCII file
def closeFile(oFile):
    oFile.close()
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to write table to ASCII file (row by row
def writeTable(oFile, oData):
    for oRow in oData:
        # Parser from list to string
        a1sRow = ' '.join(str(sRow) for sRow in oRow)
        oFile.write(a1sRow)
        oFile.write('\n')
    return oFile
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to read ASCII tabular file with characters and numbers
def readTable(oFile, iSkiprows=0):

    # Convert to index
    if iSkiprows > 0:
        iIndexRow = iSkiprows - 1
    else:
        iIndexRow = -1

    iNL = None
    for iID, sLine in enumerate(oFile):

        # Control to skip row(s)
        if iID > iIndexRow:

            a1oLine = sLine.split()

            if iNL is None:
                iNL = len(a1oLine)
                a2oDataTable = [[] for iL in range(iNL)]
            else:
                pass

            for iElemID, sElemVal in enumerate(a1oLine):
                a2oDataTable[iElemID].append(sElemVal)
        else:
            pass

    return a2oDataTable

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to read ASCII file with 1 or more columns (default mode)
def getVar(oFile):
    oData = np.array([])
    for sFileLine in oFile.readlines():
        sFileLine = sFileLine.strip()
        sLineCols = sFileLine.split()

        oLineCols = np.asarray(sLineCols)
        oData = np.append(oData, oLineCols)

    return oData
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to write Data to ASCII file (default mode)
def writeVar(oFile, sData):
    oFile.write(sData + '\n')
    return oFile
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Read ArcGrid Data
def readArcGrid(oFile):

    # Check method
    try:

        import numpy as np
        from string import atof, atoi, split

        # Read data header
        iNCols = atoi(split(oFile.readline())[1])
        iNRows = atoi(split(oFile.readline())[1])
        dXLLCorner = atof(split(oFile.readline())[1].replace(',', '.'))
        dYLLCorner = atof(split(oFile.readline())[1].replace(',', '.'))
        dCellSize = atof(split(oFile.readline())[1].replace(',', '.'))
        dNOData = atof(split(oFile.readline())[1].replace(',', '.'))
        # Dictionary data header
        a1oVarHeader = {"ncols": iNCols, "nrows": iNRows, "xllcorner": dXLLCorner, "yllcorner": dYLLCorner,
                        "cellsize": dCellSize, "NODATA_value": dNOData}

        # Read data values
        a2dVarData = np.zeros((iNRows, iNCols))
        a2dVarData = np.loadtxt(oFile, skiprows=0)

        # Debugging
        #plt.figure(1)
        #plt.imshow(a2dVarData); plt.colorbar();
        #plt.show()

    except:
        # Exit status with error
        a2dVarData = None
        a1oVarHeader = None

    return a2dVarData, a1oVarHeader

# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Write 2dVar
def writeArcGrid(sFileName, a2dVarData, a1oVarHeader, sDataFormat=None, dNoData=None):

    # sDataFormat: f, i, None
    # dNoData: 0, -9999
    if dNoData:
        a1oVarHeader["NODATA_value"] = dNoData

    # Check method
    try:

        # Defining max number of digits before comma
        dVarDataMin = np.nanmin(np.unique(a2dVarData))
        dVarDataMax = np.nanmax(np.unique(a2dVarData))
        iVarDataMax = int(dVarDataMax)

        # Get Data format and digits
        if sDataFormat == 'f':
            iDigitNum = len(str(iVarDataMax)) + 3
            sFmt = '%'+str(iDigitNum)+'.2' + sDataFormat
        elif sDataFormat == 'i':
            iDigitNum = len(str(iVarDataMax))
            sFmt = '%'+str(iDigitNum) + sDataFormat
        else:
            iDigitNum = len(str(iVarDataMax)) + 3
            sFmt = '%'+str(iDigitNum)+'.2' + sDataFormat

        oFileHeader = "ncols\t%i\n" % a1oVarHeader["ncols"]
        oFileHeader += "nrows\t%i\n" % a1oVarHeader["nrows"]
        oFileHeader += "xllcorner\t%f\n" % a1oVarHeader["xllcorner"]
        oFileHeader += "yllcorner\t%f\n" % a1oVarHeader["yllcorner"]
        oFileHeader += "cellsize\t%f\n" % a1oVarHeader["cellsize"]
        if sDataFormat == 'f':
            oFileHeader += "NODATA_value\t%f\n" % a1oVarHeader["NODATA_value"]
        elif sDataFormat == 'i':
            oFileHeader += "NODATA_value\t%i\n" % a1oVarHeader["NODATA_value"]
        else:
            oFileHeader += "NODATA_value\t%f\n" % a1oVarHeader["NODATA_value"]

        with open(sFileName, "w") as oFile:
            oFile.write(oFileHeader)
            np.savetxt(oFile, a2dVarData, delimiter=' ', fmt=sFmt,  newline='\n')

    except BaseException:
        # Exit status with error
        pass

    # ----------------------------------------------------------------------------
    
# ----------------------------------------------------------------------------
