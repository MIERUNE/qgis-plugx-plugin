import os
import shutil

from qgis.core import Qgis, QgsSymbol

from .line import get_line_symbol_data
from .marker import get_point_symbol_data
from .fill import get_polygon_symbol_data
from .hybrid import get_hybrid_symbol_data
from translator.vector.symbol.utils import (
    get_asset_raster_dir,
    get_asset_svg_dir,
    get_asset_name,
)


def generate_symbols_data(symbol: QgsSymbol):
    symbols = []
    for symbol_layer in symbol:
        if symbol_layer.type() == Qgis.SymbolType.Marker:
            symbol_layer_dict = get_point_symbol_data(symbol_layer)
        elif symbol_layer.type() == Qgis.SymbolType.Line:
            symbol_layer_dict = get_line_symbol_data(symbol_layer)
        elif symbol_layer.type() == Qgis.SymbolType.Fill:
            symbol_layer_dict = get_polygon_symbol_data(symbol_layer)
        elif symbol_layer.type() == Qgis.SymbolType.Hybrid:
            symbol_layer_dict = get_hybrid_symbol_data(symbol_layer)

        symbol_layer_dict["opacity"] = symbol.opacity()

        symbols.append(symbol_layer_dict)

    return symbols


def export_assets_from(symbol, output_dir: str):
    for symbol_layer in symbol:
        if symbol_layer.type() == Qgis.SymbolType.Marker:
            if symbol_layer.layerType() == "RasterMarker":
                asset_path = get_asset_raster_dir(output_dir)
            elif symbol_layer.layerType() == "SvgMarker":
                asset_path = get_asset_svg_dir(output_dir)
            else:
                return

            if not os.path.exists(asset_path):
                os.makedirs(asset_path)

            asset_path = os.path.join(asset_path, get_asset_name(symbol_layer))
            shutil.copy(
                symbol_layer.path(),
                asset_path,
            )


def is_included_unsupported_symbol_layer(symbol: QgsSymbol):
    # https://api.qgis.org/api/classQgsSymbolLayer.html#a885d2fa0dbeb23dfd11874895b8fc6f7
    SUPPORTED_SYMBOLLAYER_TYPES = (
        "SimpleMarker",
        "RasterMarker",
        "SvgMarker",
        "SimpleLine",
        "SimpleFill",
        "MarkerLine",
    )
    for symbol_layer in symbol:
        if symbol_layer.layerType() not in SUPPORTED_SYMBOLLAYER_TYPES:
            return True

    return False
