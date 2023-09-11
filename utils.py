import os
import json
from typing import Union


from qgis.core import (
    QgsRenderContext,
    QgsUnitTypes,
)
from qgis.utils import iface


def write_json(data: Union[list, dict], filepath: str):
    # Convert dictionary to JSON string
    json_data = json.dumps(data, ensure_ascii=False)

    # Write JSON string to file
    with open(filepath, "w") as outfile:
        outfile.write(json_data)


def convert_to_point(value: float, unit: QgsUnitTypes.RenderUnit) -> float:
    """calculate value in any unit to point"""

    if unit == QgsUnitTypes.RenderPoints:
        return value

    if unit == QgsUnitTypes.RenderPixels:
        render_context = QgsRenderContext()
        to_pt = render_context.convertToPainterUnits(
            1, QgsUnitTypes.RenderUnit.RenderPoints
        )
        return value * to_pt

    if unit == QgsUnitTypes.RenderMillimeters:
        return value * 2.8346456693

    if unit == QgsUnitTypes.RenderMetersInMapUnits:
        return value / (iface.mapCanvas().scale() / 2834.65)  # 1m = 2834.65pt

    if unit == QgsUnitTypes.RenderMapUnits:
        # MapUnitがメートルの場合のみ対応する
        mapunit = iface.activeLayer().crs().mapUnits()
        if mapunit == QgsUnitTypes.DistanceMeters:
            return value / (iface.mapCanvas().scale() / 2834.65)  # 1m = 2834.65pt

    if unit == QgsUnitTypes.RenderInches:
        return value * 72


def get_tempdir(output_dir: str) -> str:
    """return tempdir path shared by all modules. if not exists, create it."""
    temp_dir_path = os.path.join(output_dir, "temp")
    if not os.path.exists(os.path.join(output_dir, temp_dir_path)):
        os.mkdir(os.path.join(output_dir, temp_dir_path))

    return os.path.join(output_dir, temp_dir_path)
