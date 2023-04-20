from qgis.core import QgsApplication
from qgis.gui import QgisInterface

from qgis2plugx import QGIS2PlugX
from QGIS2PlugX_dialog import QGIS2PlugX_dialog


def test_show_menus(
    qgis_app: QgsApplication, qgis_iface: QgisInterface, plugin: QGIS2PlugX
):
    plugin.show_dialog()
    assert isinstance(plugin.qgis2plugx_dialog, QGIS2PlugX_dialog)