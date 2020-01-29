"""
Library Features:

Name:          hmc_form_section
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20170907'
Version:       '1.0.0'
"""

# -------------------------------------------------------------------------------------
# Library
import time

from PyQt4.QtCore import SIGNAL, pyqtSignal
from PyQt4.QtGui import QVBoxLayout, QLineEdit, QLabel, QWidget, QPushButton
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Class FormSection
class FormSection(QWidget):

    # Class signal(s)
    pressButtonYes = pyqtSignal()

    oSectionForm = []
    callback = None

    def __init__(self, parent=None, callback=None):
        super(FormSection, self).__init__(parent)

        self.callback = callback

        self.oSectionForm = []

        self.setWindowTitle('Section Information')
        self.resize(400, 300)

        layout = QVBoxLayout()

        self.textbox1 = QLineEdit()
        self.textbox1.setPlaceholderText('<type domain name here>')

        self.textbox2 = QLineEdit()
        self.textbox2.setPlaceholderText('<type section name here>')

        self.textbox3 = QLineEdit()
        self.textbox3.setPlaceholderText('<type section hydrometer code here>')
        self.textbox3.setText('-9999')

        self.textbox4 = QLineEdit()
        self.textbox4.setPlaceholderText('<type section drainage area here>')
        self.textbox4.setText('-9999')

        self.textbox5 = QLineEdit()
        self.textbox5.setPlaceholderText('<type section alert threshold here>')
        self.textbox5.setText('-9999')

        self.textbox6 = QLineEdit()
        self.textbox6.setPlaceholderText('<type section alarm threshold here>')
        self.textbox6.setText('-9999')

        layout.addWidget(QLabel("Domain Name:"))
        layout.addWidget(self.textbox1)
        layout.addWidget(QLabel("Section Name:"))
        layout.addWidget(self.textbox2)
        layout.addWidget(QLabel("Section Hydrometer Code:"))
        layout.addWidget(self.textbox3)
        layout.addWidget(QLabel("Section Area [km^2]:"))
        layout.addWidget(self.textbox4)
        layout.addWidget(QLabel("Section Alert Threshold [m^3/s]:"))
        layout.addWidget(self.textbox5)
        layout.addWidget(QLabel("Section Alarm Threshold [m^3/s]:"))
        layout.addWidget(self.textbox6)

        self.textbox1.editingFinished.connect(self.enterPress)
        self.textbox2.editingFinished.connect(self.enterPress)
        self.textbox3.editingFinished.connect(self.enterPress)
        self.textbox4.editingFinished.connect(self.enterPress)
        self.textbox5.editingFinished.connect(self.enterPress)
        self.textbox6.editingFinished.connect(self.enterPress)

        button_yes = QPushButton('Yes', self)
        button_cancel = QPushButton('Cancel', self)
        layout.addWidget(button_yes)
        layout.addWidget(button_cancel)

        layout.connect(button_yes, SIGNAL("clicked()"), self.button_click)
        layout.connect(button_cancel, SIGNAL("clicked()"), self.button_cancel)

        # ButtonYes connection(s)
        button_yes.clicked.connect(self.emitSignal)
        button_yes.clicked.connect(self.close)
        # ButtonCancel connection(s)
        button_cancel.clicked.connect(self.close)

        # Set layout
        self.setLayout(layout)
        self.layout = layout

    # Method to emit signal
    def emitSignal(self):
        # Emit ButtonYes signal
        self.pressButtonYes.emit()

    def enterPress(self):
        print('information edited')

    # Method to save form
    def button_click(self):

        sText1 = str(self.textbox1.text())
        sText2 = str(self.textbox2.text())
        sText3 = str(self.textbox3.text())
        sText4 = str(self.textbox4.text())
        sText5 = str(self.textbox5.text())
        sText6 = str(self.textbox6.text())

        if not sText1:
            sText1 = 'default'

        if not sText2:
            sText2 = time.strftime("%Y,%m,%d,%H,%M,%S")
            sText2 = sText2.replace(',', '')

        sText1 = sText1.replace(' ', '_')
        sText2 = sText2.replace(' ', '_')

        self.oSectionForm = [sText1, sText2, sText3, sText4, sText5, sText6]

        if self.callback:
            self.callback(self.oSectionForm)

    # Method to nullify form
    def button_cancel(self):

        self.oSectionForm = None

        if self.callback:
            self.callback(self.oSectionForm)
# -------------------------------------------------------------------------------------
