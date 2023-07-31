import os
import shutil

from qgis.core import Qgis, QgsSymbol

from .line import get_line_symbol_data
from .marker import get_point_symbol_data
from .fill import get_polygon_symbol_data
from .hybrid import get_hybrid_symbol_data
from translator.vector.symbol.utils import (
    get_asset_dir,
    get_asset_name,
)


def generate_symbols_data(symbol: QgsSymbol):
    symbols = []
    for symbol_layer in symbol:
        if symbol_layer.type() == Qgis.SymbolType.Marker:
            symbol_layer_dict = get_point_symbol_data(symbol_layer, symbol.opacity())
        elif symbol_layer.type() == Qgis.SymbolType.Line:
            symbol_layer_dict = get_line_symbol_data(symbol_layer, symbol.opacity())
        elif symbol_layer.type() == Qgis.SymbolType.Fill:
            symbol_layer_dict = get_polygon_symbol_data(symbol_layer, symbol.opacity())
        elif symbol_layer.type() == Qgis.SymbolType.Hybrid:
            symbol_layer_dict = get_hybrid_symbol_data(symbol_layer, symbol.opacity())

        symbols.append(symbol_layer_dict)

    return symbols


def export_assets_from(symbol: QgsSymbol, output_dir: str):
    asset_dir = get_asset_dir(output_dir)
    if not os.path.exists(asset_dir):
        os.makedirs(asset_dir)

    for symbol_layer in symbol:
        if symbol_layer.subSymbol():
            # recursive: if the symbol layer has sub symbol, extract from it
            export_assets_from(symbol_layer.subSymbol(), output_dir)

        if symbol_layer.type() == Qgis.SymbolType.Marker:
            # extract only raster or svg marker
            if symbol_layer.layerType() not in ["RasterMarker", "SvgMarker"]:
                continue  # if not, skip

            asset_path = os.path.join(asset_dir, get_asset_name(symbol_layer))
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
