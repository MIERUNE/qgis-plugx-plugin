import os

from qgis.core import QgsSymbolLayer, QgsUnitTypes
from PyQt5.QtGui import QColor
from plugx_utils import convert_to_point


def get_asset_dir(output_dir: str):
    return os.path.join(output_dir, "assets")


def get_asset_name(symbol_layer: QgsSymbolLayer):
    return os.path.basename(symbol_layer.path())


def to_rgba(color: QColor):
    """calculate #rgba from #rgb + alpha percent value"""

    # alpha percentage value (0.0-1.0) to hex (00-ff)
    alpha = hex(int(color.alphaF() * 255))[2:].zfill(2)

    return f"{color.name()}{alpha}"


def get_stroke_width_pt(defined_width: float, unit: QgsUnitTypes.RenderUnit) -> float:
    """get line width in points, considering hairline or not
    symbol layer stroke width is set as 0 when hairline
    to be render as 0.5px (0.375pt) as defined in QGIS code
    https://github.com/qgis/QGIS/blob/e7f5b6f286b6cbaeaad5e73d69fad1448018c7e0/
    tests/src/python/test_qgssymbollayer_createsld.py#L234
    """
    if defined_width == 0:
        hairline_px_size = 0.5
        return convert_to_point(hairline_px_size, QgsUnitTypes.RenderPixels)
    else:
        return convert_to_point(defined_width, unit)
