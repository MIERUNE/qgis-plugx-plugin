import os

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from qgis.gui import QgisInterface

from ui.main_dialog import MainDialog
from ui.about_dialog import AboutDialog

PLUGIN_NAME = "QGIS2PlugX"


class QGIS2PlugX:
    def __init__(self, iface: QgisInterface):
        self.iface = iface
        self.win = self.iface.mainWindow()
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = PLUGIN_NAME
        self.toolbar = self.iface.addToolBar(PLUGIN_NAME)
        self.toolbar.setObjectName(PLUGIN_NAME)

        # QDialogを保存するためのクラス変数
        self.main_dialog = None
        self.about_dialog = None

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        return action

    def initGui(self):
        self.add_action(
            icon_path=None,
            text="QGIS2PlugX",
            callback=self.show_dialog,
            parent=self.win,
            add_to_menu=False,
        )

        self.add_action(
            icon_path=None,
            text="Export",
            callback=self.show_dialog,
            parent=self.win,
            add_to_toolbar=False,
        )

        self.add_action(
            icon_path=None,
            text="About",
            callback=self.show_about,
            parent=self.win,
            add_to_toolbar=False,
        )

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(PLUGIN_NAME, action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def show_dialog(self):
        if self.main_dialog is None:
            self.main_dialog = MainDialog()

        self.main_dialog.show()
        self.main_dialog.process_node()

    def show_about(self):
        if self.about_dialog is None:
            self.about_dialog = AboutDialog()

        self.about_dialog.show()
