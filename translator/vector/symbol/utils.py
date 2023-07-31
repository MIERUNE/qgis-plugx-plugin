import os

from qgis.core import QgsSymbolLayer
from PyQt5.QtGui import QColor


def get_asset_dir(output_dir: str):
    return os.path.join(output_dir, "assets")


def get_asset_name(symbol_layer: QgsSymbolLayer):
    return os.path.basename(symbol_layer.path())


def to_rgba(color: QColor):
    """calculate #rgba from #rgb + alpha percent value"""

    # alpha percentage value (0.0-1.0) to hex (00-ff)
    alpha = hex(int(color.alphaF() * 255))[2:].zfill(2)

    return f"{color.name()}{alpha}"
