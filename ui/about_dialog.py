import os

from PyQt5.QtWidgets import QDialog, QLabel

from qgis.PyQt import uic


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(
            os.path.join(os.path.dirname(__file__), "about_dialog.ui"), self
        )

        self.init_ui()

    def init_ui(self):
        # connect signals
        self.ui.pushButton_close.clicked.connect(self.close)
