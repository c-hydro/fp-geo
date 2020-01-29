"""
Library Features:

Name:          hmc_form_table
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20170907'
Version:       '1.0.0'
"""

# -------------------------------------------------------------------------------------
# Library
from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QVBoxLayout, QWidget, QMessageBox, QFileDialog, \
    QPushButton, QTableWidget, QAbstractItemView, QTableWidgetItem

from hmc_apps_io import writeTableObj
from hmc_tools_settings import oFormSectionHeader
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class FormTable
class FormTable(QWidget):

    # -------------------------------------------------------------------------------------
    # Form signal(s)
    closingFormTable = pyqtSignal()
    deletingFormTable = pyqtSignal()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method init
    def __init__(self, parent=None):

        # -------------------------------------------------------------------------------------
        # Constructor
        super(FormTable, self).__init__(parent)

        self.setWindowTitle('Section Table')

        oLayout = QVBoxLayout()

        self.TableWidget = QTableWidget()

        self.BtnSave = QPushButton('Save', self)
        self.BtnCancel = QPushButton('Cancel', self)

        # Define layout
        oLayout.addWidget(self.TableWidget)
        oLayout.addWidget(self.BtnSave)
        oLayout.addWidget(self.BtnCancel)

        # Set layout
        self.setLayout(oLayout)
        self.oLayout = oLayout

        # Define action(s)
        self.BtnSave.pressed.connect(self.saveTable)
        self.BtnCancel.pressed.connect(self.cancelTable)

        # Show widget
        self.show()
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to set data
    def setData(self, oData):
        # Check data table
        if oData:

            iDataRows = len(oData)
            iDataCols = len(oData[0])

            self.TableWidget.setRowCount(iDataRows)
            self.TableWidget.setColumnCount(iDataCols)

            self.TableWidget.setHorizontalHeaderLabels(oFormSectionHeader)

            oTableHeader = self.TableWidget.horizontalHeader()
            oTableHeader.setStretchLastSection(True)

            iNL = None
            for iID, a1oLine in enumerate(oData):

                if iNL is None:
                    iNL = len(a1oLine)
                    a2oTable = [[] for iL in range(iNL)]
                else:
                    pass

                for iElemID, oElemVal in enumerate(a1oLine):
                    a2oTable[iElemID].append(oElemVal)

                    oItem = QTableWidgetItem(oElemVal)
                    oItem.setFlags(Qt.ItemIsSelectable)
                    self.TableWidget.setItem(iID, iElemID, oItem)

            self.TableWidget.resizeColumnsToContents()
            self.TableWidget.update()
            #self.TableWidget.repaint()

            self.TableWidget.setEditTriggers(QAbstractItemView.CurrentChanged)

        else:
            # Nullity table object
            #self.TableWidget.setRowCount(0)
            #self.TableWidget.setColumnCount(0)
            self.TableWidget.clearContents()
            self.TableWidget.setItem(0, 0, QTableWidgetItem("No data here ... "))
            #self.TableWidget.setHorizontalHeaderLabels(oFormSectionHeader)

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to cancel table
    def cancelTable(self):
        self.deletingFormTable.emit()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to save table object to ascii file
    def saveTable(self):
        # Select output filename
        sFilePath = str(QFileDialog.getSaveFileName(self, 'Save File', '', 'ASCII (*.txt)'))
        # Check file definition by user
        if sFilePath is not None:
            # Save data to file
            writeTableObj(sFilePath, self.TableWidget)
        else:
            pass

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Method to close event (destroy QWidget); closing plugin will destroy table form too
    def closeEvent(self, oEvent):
        oEvent.accept()
        self.closingFormTable.emit()
    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
