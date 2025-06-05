import os

# QGIS-API
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QKeyEvent
from qgis.PyQt.QtWidgets import QDialog, QMessageBox


class ProgressDialog(QDialog):
    def __init__(self, set_abort_flag_callback):
        """_summary_

        Args:
            set_abort_flag_callback (optional, method()): called when abort clicked
        """
        super().__init__()
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.ui = uic.loadUi(
            os.path.join(os.path.dirname(__file__), "progress_dialog.ui"), self
        )

        self.set_abort_flag_callback = set_abort_flag_callback
        self.init_ui()

    def init_ui(self):
        self.label.setText(self.tr("Initializing process..."))
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(0)
        self.abortButton.setEnabled(True)
        self.abortButton.setText(self.tr("Cancel"))
        self.abortButton.clicked.connect(self.on_abort_click)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            return
        super().keyPressEvent(event)

    def on_abort_click(self):
        if QMessageBox.Yes == QMessageBox.question(
            self,
            self.tr("Check"),
            self.tr("Are you sure to abort the process?"),
            QMessageBox.Yes,
            QMessageBox.No,
        ):
            if self.abortButton.isEnabled():  # abort if possible
                self.set_abort_flag_callback()
                self.abortButton.setEnabled(False)
                self.abortButton.setText(self.tr("Aborting..."))

    def set_maximum(self, value: int):
        self.progressBar.setMaximum(value)

    def add_progress(self, value: int):
        self.progressBar.setValue(self.progressBar.value() + value)

    def set_messsage(self, message: str):
        self.label.setText(message)

    def set_abortable(self, abortable=True):
        self.abortButton.setEnabled(abortable)

    def translate(self, message: str):
        """translate messages coming from outside UI"""
        message_dic = {
            "Processing: ": self.tr("Processing: "),
        }
        translated_message = message_dic.get(
            message, message
        )  # fallback is self message

        return translated_message
