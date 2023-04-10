from qgis.core import QgsApplication
from qgis.gui import QgisInterface

from QGIS2PlugX_dialog import QGIS2PlugX_dialog


def test_cancel(qgis_app: QgsApplication, qgis_iface: QgisInterface):
    sample_menu_01 = QGIS2PlugX_dialog()
    sample_menu_01.show()
    assert sample_menu_01.isVisible() is True
    sample_menu_01.ui.pushButton_cancel.click()
    assert sample_menu_01.isVisible() is False
