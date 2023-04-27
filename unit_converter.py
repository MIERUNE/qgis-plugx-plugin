from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from qgis.gui import *
from qgis.PyQt import uic
from qgis.utils import iface


class UnitConverter:
    def __init__(self, value: float, unit: QgsUnitTypes.RenderUnit):
        self.value = value
        self.unit = unit

        self.dpi = iface.mapCanvas().mapSettings().outputDpi()
        self.scale = iface.mapCanvas().scale()

    def convert_to_point(self):
        if self.unit == QgsUnitTypes.RenderPoints:
            return self.value

        if self.unit == QgsUnitTypes.RenderPixels:
            return self.value * self.dpi

        if self.unit == QgsUnitTypes.RenderMillimeters:
            return self.value * 2.8346456693

        if self.unit == QgsUnitTypes.RenderMetersInMapUnits:
            render_context = QgsRenderContext()
            return render_context.convertFromMapUnits(self.value,
                                                      QgsUnitTypes.RenderPoints) * self.scale / 2834.65  # 1m = 2834.65pt

        if self.unit == QgsUnitTypes.RenderMapUnits:
            render_context = QgsRenderContext()
            return render_context.convertFromMapUnits(self.value, QgsUnitTypes.RenderPoints)

        if self.unit == QgsUnitTypes.RenderInches:
            return self.value * 72