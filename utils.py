import json
from typing import Union


from qgis.core import QgsRenderContext, QgsUnitTypes
from qgis.utils import iface


def write_json(data: Union[list, dict], filepath: str):
    # Convert dictionary to JSON string
    json_data = json.dumps(data)

    # Write JSON string to file
    with open(filepath, "w") as outfile:
        outfile.write(json_data)


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
            render_context = QgsRenderContext()
            to_pt = render_context.convertToPainterUnits(
                1, QgsUnitTypes.RenderUnit.RenderPoints
            )
            return self.value * to_pt

        if self.unit == QgsUnitTypes.RenderMillimeters:
            return self.value * 2.8346456693

        if self.unit == QgsUnitTypes.RenderMetersInMapUnits:
            return self.value / (self.scale / 2834.65)  # 1m = 2834.65pt

        if self.unit == QgsUnitTypes.RenderMapUnits:
            # MapUnitがメートルの場合のみ対応する
            mapunit = iface.activeLayer().crs().mapUnits()
            if mapunit == QgsUnitTypes.DistanceMeters:
                return self.value / (self.scale / 2834.65)  # 1m = 2834.65pt

        if self.unit == QgsUnitTypes.RenderInches:
            return self.value * 72
