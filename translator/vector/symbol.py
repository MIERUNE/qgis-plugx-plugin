import os
import shutil
from PyQt5.QtCore import Qt
from qgis.core import Qgis, QgsSymbolLayer, QgsSymbol
from utils import convert_to_point


def is_included_unsupported_symbol_layer(symbol: QgsSymbol):
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


def _get_asset_name(symbol_layer: QgsSymbolLayer):
    return os.path.basename(symbol_layer.path())


def _get_symbol_level(symbol_layer: QgsSymbolLayer):
    # https://github.com/qgis/QGIS/blob/65d40ee0ce59e761ee2de366ca9a963f35adfcfd/src/core/vector/qgsvectorlayerrenderer.cpp#L702
    return symbol_layer.renderingPass()  # renderingPass means symbolLevels:


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


def generate_symbols_data(symbol: QgsSymbol):
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


def _get_point_symbol_data(symbol_layer: QgsSymbolLayer) -> dict:
    if symbol_layer.layerType() == "RasterMarker":
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "fill_color": symbol_layer.color().name(),
            "outline_color": symbol_layer.strokeColor().name(),
            "outline_width": None,
            "symbol_layer_type": "raster",
            "symbol_path": "assets/symbol_raster/" + _get_asset_name(symbol_layer),
            "level": _get_symbol_level(symbol_layer),
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
            "level": _get_symbol_level(symbol_layer),
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
            "level": _get_symbol_level(symbol_layer),
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
            "level": _get_symbol_level(symbol_layer),
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
            "level": _get_symbol_level(symbol_layer),
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
            "level": _get_symbol_level(symbol_layer),
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
            "level": _get_symbol_level(symbol_layer),
        }

    return symbol_layer_dict


def _get_line_symbol_data(symbol_layer: QgsSymbolLayer) -> dict:
    if symbol_layer.layerType() == "SimpleLine":
        symbol_layer_dict = {
            "symbol_layer_type": "simple",
            "color": symbol_layer.color().name(),
            "width": 0
            if Qt.PenStyle.NoPen
            else convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
            "level": _get_symbol_level(symbol_layer),
        }
    elif symbol_layer.layerType() == "InterpolatedLine":
        # TODO: implement
        symbol_layer_dict = {
            "symbol_layer_type": "simple",
            "color": symbol_layer.color().name(),
            "width": 0
            if Qt.PenStyle.NoPen
            else convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
            "level": _get_symbol_level(symbol_layer),
        }
    elif symbol_layer.layerType() == "MarkerLine":
        # TODO: implement
        symbol_layer_dict = {
            "symbol_layer_type": "simple",
            "color": symbol_layer.color().name(),
            "width": 0
            if Qt.PenStyle.NoPen
            else convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
            "level": _get_symbol_level(symbol_layer),
        }
    elif symbol_layer.layerType() == "HashedLine":
        # TODO: implement
        symbol_layer_dict = {
            "symbol_layer_type": "simple",
            "color": symbol_layer.color().name(),
            "width": 0
            if Qt.PenStyle.NoPen
            else convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
            "level": _get_symbol_level(symbol_layer),
        }
    elif symbol_layer.layerType() == "RasterLine":
        # TODO: implement
        symbol_layer_dict = {
            "symbol_layer_type": "simple",
            "color": symbol_layer.color().name(),
            "width": 0
            if Qt.PenStyle.NoPen
            else convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
            "level": _get_symbol_level(symbol_layer),
        }

    return symbol_layer_dict


def _get_polygon_symbol_data(symbol_layer: QgsSymbolLayer) -> dict:
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
            "level": _get_symbol_level(symbol_layer),
        }
    elif symbol_layer.layerType() == "CentroidFill":
        symbol_layer_dict = {
            "symbol_layer_type": "simple",  # unsupported yet
            "fill_color": symbol_layer.subSymbol().symbolLayer(0).color().name(),
            "level": _get_symbol_level(symbol_layer),
        }
    elif symbol_layer.layerType() == "PointPatternFill":
        # TODO: implement
        symbol_layer_dict = {
            "symbol_layer_type": "simple",  # unsupported yet
            "fill_color": symbol_layer.color().name(),
            "level": _get_symbol_level(symbol_layer),
        }
    elif symbol_layer.layerType() == "RandomMarkerFill":
        # TODO: implement
        symbol_layer_dict = {
            "symbol_layer_type": "simple",  # unsupported yet
            "fill_color": symbol_layer.color().name(),
            "level": _get_symbol_level(symbol_layer),
        }
    elif symbol_layer.layerType() == "LinePatternFill":
        # TODO: implement
        symbol_layer_dict = {
            "symbol_layer_type": "simple",  # unsupported yet
            "fill_color": symbol_layer.color().name(),
            "level": _get_symbol_level(symbol_layer),
        }
    elif symbol_layer.layerType() == "SVGFill":
        # TODO: implement
        symbol_layer_dict = {
            "symbol_layer_type": "simple",  # unsupported yet
            "fill_color": symbol_layer.color().name(),
            "level": _get_symbol_level(symbol_layer),
        }
    elif symbol_layer.layerType() == "GradientFill":
        # TODO: implement
        symbol_layer_dict = {
            "symbol_layer_type": "simple",  # unsupported yet
            "fill_color": symbol_layer.color().name(),
            "level": _get_symbol_level(symbol_layer),
        }
    elif symbol_layer.layerType() == "ShapeburstFill":
        # TODO: implement
        symbol_layer_dict = {
            "symbol_layer_type": "simple",  # unsupported yet
            "fill_color": symbol_layer.color().name(),
            "level": _get_symbol_level(symbol_layer),
        }
    return symbol_layer_dict


def _get_hybrid_symbol_data(symbol_layer: QgsSymbolLayer) -> dict:
    # TODO: implement
    symbol_layer_dict = {
        "symbol_layer_type": symbol_layer.layerType().lower(),
        "color": symbol_layer.color().name(),
        "level": _get_symbol_level(symbol_layer),
        # "geometry": symbol_layer.geometryExpression(),
    }

    return symbol_layer_dict
