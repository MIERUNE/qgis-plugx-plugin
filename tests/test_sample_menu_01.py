from qgis.core import QgsApplication
from qgis.gui import QgisInterface

from sample_menu_01 import SampleMenu01


def test_cancel(qgis_app: QgsApplication, qgis_iface: QgisInterface):
    sample_menu_01 = SampleMenu01()
    sample_menu_01.show()
    assert sample_menu_01.isVisible() is True
    sample_menu_01.ui.pushButton_cancel.click()
    assert sample_menu_01.isVisible() is False
