"""
Library Features:

Name:          hmc_apps_io_object
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20170926'
Version:       '1.0.0'
"""
# --------------------------------------------------------------------------------
# Library
from PyQt4.QtGui import QTableWidgetItem
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to parser table object
def parserTable(oTableObject):

    oTableData = []
    for iRow in range(oTableObject.rowCount()):
        oTableRow = []
        for iCol in range(oTableObject.columnCount()):
            oTableItem = oTableObject.item(iRow, iCol)
            if oTableItem is not None:
                oTableRow.append(unicode(oTableItem.text()).encode('utf8'))
            else:
                oTableRow.append('')

        oTableData.append(oTableRow)

    return oTableData
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Method to import data into table object
def importTable(oFileHandle, oTableObject):

    oTableObject.setRowCount(0)
    oTableObject.setColumnCount(0)
    for sRowData in oFileHandle:

        oRowData = sRowData.split()

        iRow = oTableObject.rowCount()
        oTableObject.insertRow(iRow)
        oTableObject.setColumnCount(len(oRowData))

        for iCol, oDataItem in enumerate(oRowData):
            oTableItem = QTableWidgetItem(oDataItem.decode('utf8'))
            oTableObject.setItem(iRow, iCol, oTableItem)

    return oTableObject
# --------------------------------------------------------------------------------
