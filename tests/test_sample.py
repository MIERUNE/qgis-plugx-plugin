from qgis.core import QgsApplication
from qgis.gui import QgisInterface

from qgis2plugx import QGIS2PlugX
from QGIS2PlugX_dialog import QGIS2PlugX_dialog
from sample_menu_02 import SampleMenu02


def test_show_menus(
    qgis_app: QgsApplication, qgis_iface: QgisInterface, plugin: QGIS2PlugX
):
    plugin.show_dialog()
    assert isinstance(plugin.sample_menu_01, QGIS2PlugX_dialog)

    plugin.show_menu_02()
    assert isinstance(plugin.sample_menu_02, SampleMenu02)
