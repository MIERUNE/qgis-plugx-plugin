import os

from qgis.core import QgsSymbolLayer


def get_asset_raster_dir(output_dir: str):
    return os.path.join(output_dir, "assets", "symbol_raster")


def get_asset_svg_dir(output_dir: str):
    return os.path.join(output_dir, "assets", "symbol_svg")


def get_asset_name(symbol_layer: QgsSymbolLayer):
    return os.path.basename(symbol_layer.path())
