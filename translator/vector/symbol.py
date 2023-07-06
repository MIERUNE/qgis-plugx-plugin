import os
import shutil
from PyQt5.QtCore import Qt
from qgis.core import Qgis
from utils import convert_to_point


def is_included_unsupported_symbol_layer(symbol):
    # https://api.qgis.org/api/classQgsSymbolLayer.html#a885d2fa0dbeb23dfd11874895b8fc6f7
    SUPPORTED_SYMBOLLAYER_TYPES = (
        "SimpleMarker",
        "RasterMarker",
        "SvgMarker",
        "SimpleLine",
        "SimpleFill",
    )
    for symbol_layer in symbol:
        if symbol_layer.layerType() not in SUPPORTED_SYMBOLLAYER_TYPES:
            return True

    return False


def _get_asset_raster_dir(output_dir: str):
    return os.path.join(output_dir, "assets", "symbol_raster")


def _get_asset_svg_dir(output_dir: str):
    return os.path.join(output_dir, "assets", "symbol_svg")


def _get_asset_name(symbol_layer):
    return os.path.basename(symbol_layer.path())


def export_assets_from(symbol, output_dir: str):
    for symbol_layer in symbol:
        if symbol_layer.type() == Qgis.SymbolType.Marker:
            if symbol_layer.layerType() == "RasterMarker":
                asset_path = _get_asset_raster_dir(output_dir)
            elif symbol_layer.layerType() == "SvgMarker":
                asset_path = _get_asset_svg_dir(output_dir)
            else:
                return

            if not os.path.exists(asset_path):
                os.makedirs(asset_path)

            asset_path = os.path.join(asset_path, _get_asset_name(symbol_layer))
            shutil.copy(
                symbol_layer.path(),
                asset_path,
            )


def generate_symbols_data(symbol):
    symbols = []
    for symbol_layer in symbol:
        if symbol_layer.type() == Qgis.SymbolType.Marker:
            symbol_layer_dict = _get_point_symbol_data(symbol_layer)
        elif symbol_layer.type() == Qgis.SymbolType.Line:
            symbol_layer_dict = _get_line_symbol_data(symbol_layer)
        elif symbol_layer.type() == Qgis.SymbolType.Fill:
            symbol_layer_dict = _get_polygon_symbol_data(symbol_layer)
        elif symbol_layer.type() == Qgis.SymbolType.Hybrid:
            symbol_layer_dict = _get_hybrid_symbol_data(symbol_layer)

        symbols.append(symbol_layer_dict)

    return symbols


def _get_point_symbol_data(symbol_layer) -> dict:
    if symbol_layer.layerType() == "RasterMarker":
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "fill_color": symbol_layer.color().name(),
            "outline_color": symbol_layer.strokeColor().name(),
            "outline_width": None,
            "symbol_layer_type": "raster",
            "symbol_path": "assets/symbol_raster/" + _get_asset_name(symbol_layer),
        }

    elif symbol_layer.layerType() == "SvgMarker":
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "fill_color": symbol_layer.color().name(),
            "outline_color": symbol_layer.strokeColor().name(),
            "outline_width": convert_to_point(
                symbol_layer.strokeWidth(), symbol_layer.strokeWidthUnit()
            ),
            "symbol_layer_type": "svg",
            "symbol_path": "assets/symbol_svg/" + _get_asset_name(symbol_layer),
        }

    elif symbol_layer.layerType() == "SimpleMarker":
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "fill_color": symbol_layer.color().name(),
            "outline_color": symbol_layer.strokeColor().name(),
            "outline_width": 0
            if symbol_layer.strokeStyle() == Qt.PenStyle.NoPen
            else convert_to_point(
                symbol_layer.strokeWidth(), symbol_layer.strokeWidthUnit()
            ),
            "symbol_layer_type": "simple",
            "symbol_path": "",
        }

    elif symbol_layer.layerType() == "FontMarker":
        # TODO: implement
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "fill_color": symbol_layer.color().name(),
            "outline_color": symbol_layer.strokeColor().name(),
            "outline_width": None,
            "symbol_layer_type": "raster",
            "symbol_path": "assets/symbol_raster/" + _get_asset_name(symbol_layer),
        }
    elif symbol_layer.layerType() == "AnimatedMarker":
        # TODO: implement
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "fill_color": symbol_layer.color().name(),
            "outline_color": symbol_layer.strokeColor().name(),
            "outline_width": None,
            "symbol_layer_type": "raster",
            "symbol_path": "assets/symbol_raster/" + _get_asset_name(symbol_layer),
        }
    elif symbol_layer.layerType() == "FilledMarker":
        # TODO: implement
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "fill_color": symbol_layer.color().name(),
            "outline_color": symbol_layer.strokeColor().name(),
            "outline_width": None,
            "symbol_layer_type": "raster",
            "symbol_path": "assets/symbol_raster/" + _get_asset_name(symbol_layer),
        }
    elif symbol_layer.layerType() == "MaskMarker":
        # TODO: implement
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "fill_color": symbol_layer.color().name(),
            "outline_color": symbol_layer.strokeColor().name(),
            "outline_width": None,
            "symbol_layer_type": "raster",
            "symbol_path": "assets/symbol_raster/" + _get_asset_name(symbol_layer),
        }

    return symbol_layer_dict


def _get_line_symbol_data(symbol_layer) -> dict:
    if symbol_layer.layerType() == "SimpleLine":
        symbol_layer_dict = {
            "symbol_layer_type": "simple",
            "color": symbol_layer.color().name(),
            "width": 0
            if Qt.PenStyle.NoPen
            else convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
        }
    elif symbol_layer.layerType() == "InterpolatedLine":
        # TODO: implement
        symbol_layer_dict = {
            "symbol_layer_type": "simple",
            "color": symbol_layer.color().name(),
            "width": 0
            if Qt.PenStyle.NoPen
            else convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
        }
    elif symbol_layer.layerType() == "MarkerLine":
        # TODO: implement
        symbol_layer_dict = {
            "symbol_layer_type": "simple",
            "color": symbol_layer.color().name(),
            "width": 0
            if Qt.PenStyle.NoPen
            else convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
        }
    elif symbol_layer.layerType() == "HashedLine":
        # TODO: implement
        symbol_layer_dict = {
            "symbol_layer_type": "simple",
            "color": symbol_layer.color().name(),
            "width": 0
            if Qt.PenStyle.NoPen
            else convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
        }
    elif symbol_layer.layerType() == "RasterLine":
        # TODO: implement
        symbol_layer_dict = {
            "symbol_layer_type": "simple",
            "color": symbol_layer.color().name(),
            "width": 0
            if Qt.PenStyle.NoPen
            else convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
        }

    return symbol_layer_dict


def _get_polygon_symbol_data(symbol_layer) -> dict:
    # Case of simple fill
    if symbol_layer.layerType() == "SimpleFill":
        symbol_layer_dict = {
            "symbol_layer_type": "simple",
            "fill_color": symbol_layer.fillColor().name(),
            "outline_color": symbol_layer.strokeColor().name(),
            "outline_width": 0
            if symbol_layer.strokeStyle() == Qt.PenStyle.NoPen
            else convert_to_point(
                symbol_layer.strokeWidth(), symbol_layer.strokeWidthUnit()
            ),
        }
    elif symbol_layer.layerType() == "CentroidFill":
        symbol_layer_dict = {
            "symbol_layer_type": "simple",  # unsupported yet
            "fill_color": symbol_layer.subSymbol().symbolLayer(0).color().name(),
        }
    elif symbol_layer.layerType() == "PointPatternFill":
        symbol_layer_dict = {
            "symbol_layer_type": "simple",  # unsupported yet
            "fill_color": symbol_layer.subSymbol().symbolLayer(0).color().name(),
        }
    elif symbol_layer.layerType() == "RandomMarkerFill":
        symbol_layer_dict = {
            "symbol_layer_type": "simple",  # unsupported yet
            "fill_color": symbol_layer.subSymbol().symbolLayer(0).color().name(),
        }
    elif symbol_layer.layerType() == "LinePatternFill":
        symbol_layer_dict = {
            "symbol_layer_type": "simple",  # unsupported yet
            "fill_color": symbol_layer.subSymbol().symbolLayer(0).color().name(),
        }
    elif symbol_layer.layerType() == "SVGFill":
        symbol_layer_dict = {
            "symbol_layer_type": "simple",  # unsupported yet
            "fill_color": symbol_layer.svgFillColor().name(),
        }
    elif symbol_layer.layerType() == "GradientFill":
        symbol_layer_dict = {
            "symbol_layer_type": "simple",  # unsupported yet
            "fill_color": symbol_layer.color().name(),
        }
    elif symbol_layer.layerType() == "ShapeburstFill":
        symbol_layer_dict = {
            "symbol_layer_type": "simple",  # unsupported yet
            "fill_color": symbol_layer.color().name(),
        }

    return symbol_layer_dict


def _get_hybrid_symbol_data(symbol_layer) -> dict:
    # TODO: implement
    symbol_layer_dict = {
        "symbol_layer_type": symbol_layer.layerType().lower(),
        "color": symbol_layer.color().name(),
        # "geometry": symbol_layer.geometryExpression(),
    }

    return symbol_layer_dict
