from qgis.core import QgsApplication
from qgis.gui import QgisInterface

from sample import Sample
from sample_menu_01 import SampleMenu01
from sample_menu_02 import SampleMenu02


def test_show_menus(
    qgis_app: QgsApplication, qgis_iface: QgisInterface, plugin: Sample
):
    plugin.show_menu_01()
    assert isinstance(plugin.sample_menu_01, SampleMenu01)

    plugin.show_menu_02()
    assert isinstance(plugin.sample_menu_02, SampleMenu02)
