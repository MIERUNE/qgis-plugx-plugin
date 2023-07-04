import os

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from qgis.gui import QgisInterface

from QGIS2PlugX_dialog import QGIS2PlugX_dialog

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
        self.qgis2plugx_dialog = None

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
        # メニュー設定
        self.add_action(
            icon_path=None,
            text="QGIS2PlugX",
            callback=self.show_dialog,
            parent=self.win,
        )

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(PLUGIN_NAME, action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def show_dialog(self):
        if self.qgis2plugx_dialog is None:
            self.qgis2plugx_dialog = QGIS2PlugX_dialog()
        else:
            self.qgis2plugx_dialog.load_layer_list()
        self.qgis2plugx_dialog.show()
