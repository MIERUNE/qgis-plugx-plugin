import os
import shutil
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
            "type": "raster",
            "asset_path": "assets/symbol_raster/" + _get_asset_name(symbol_layer),
            "level": symbol_layer.renderingPass(),  # renderingPass means symbolLevels
            # https://github.com/qgis/QGIS/blob/65d40ee0ce59e761ee2de366ca9a963f35adfcfd/src/core/vector/qgsvectorlayerrenderer.cpp#L702
        }

    elif symbol_layer.layerType() == "SvgMarker":
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "color": symbol_layer.color().name(),
            "outline_color": symbol_layer.strokeColor().name(),
            "outline_width": convert_to_point(
                symbol_layer.strokeWidth(), symbol_layer.strokeWidthUnit()
            ),
            "type": "svg",
            "asset_path": "assets/symbol_svg/" + _get_asset_name(symbol_layer),
            "level": symbol_layer.renderingPass(),
        }

    elif symbol_layer.layerType() == "SimpleMarker":
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "color": symbol_layer.color().name(),
            "outline_color": symbol_layer.strokeColor().name(),
            "outline_width": convert_to_point(
                symbol_layer.strokeWidth(), symbol_layer.strokeWidthUnit()
            ),
            "type": "simple",
            "level": symbol_layer.renderingPass(),
        }

    elif symbol_layer.layerType() == "FontMarker":
        # TODO: implement
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "color": symbol_layer.color().name(),
            "type": "font",
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "AnimatedMarker":
        # TODO: implement
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "type": "animated",
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "EllipseMarker":
        # TODO: implement
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "color": symbol_layer.color().name(),
            "type": "ellipse",
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "FilledMarker":
        # TODO: implement
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "type": "filled",
            "level": symbol_layer.renderingPass(),
        }
    elif (
        symbol_layer.layerType() == "GeometryGenerator"
        or symbol_layer.layerType() == "VectorField"
        or symbol_layer.layerType() == "MaskMarker"
    ):
        # never to be supported...
        symbol_layer_dict = {
            "size": 0,
            "color": "#000000",
            "type": "unsupported",
            "level": symbol_layer.renderingPass(),
        }
    else:
        raise Exception("Unexpected symbol layer type")

    return symbol_layer_dict


def _get_line_symbol_data(symbol_layer: QgsSymbolLayer) -> dict:
    if symbol_layer.layerType() == "SimpleLine":
        symbol_layer_dict = {
            "type": "simple",
            "color": symbol_layer.color().name(),
            "width": convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "InterpolatedLine":
        # TODO: implement
        symbol_layer_dict = {
            "type": "interpolated",
            "color": symbol_layer.color().name(),
            "width": convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "MarkerLine":
        # TODO: implement
        symbol_layer_dict = {
            "type": "marker",
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "HashLine":
        # TODO: implement
        symbol_layer_dict = {
            "type": "hash",
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "RasterLine":
        # TODO: implement
        symbol_layer_dict = {
            "type": "raster",
            "width": convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "Lineburst":
        # TODO: implement
        symbol_layer_dict = {
            "type": "lineburst",
            "width": convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "ArrowLine":
        # TODO: implement
        symbol_layer_dict = {
            "type": "arrow",
            "width": convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "GeometryGenerator":
        # never to be supported...
        symbol_layer_dict = {
            "type": "unsupported",
            "width": 0,
            "color": "#000000",
            "level": symbol_layer.renderingPass(),
        }
    else:
        raise Exception("Unexpected symbol layer type")

    return symbol_layer_dict


def _get_polygon_symbol_data(symbol_layer: QgsSymbolLayer) -> dict:
    # Case of simple fill
    if symbol_layer.layerType() == "SimpleFill":
        symbol_layer_dict = {
            "type": "simple",
            "color": symbol_layer.fillColor().name(),
            "outline_color": symbol_layer.strokeColor().name(),
            "outline_width": convert_to_point(
                symbol_layer.strokeWidth(), symbol_layer.strokeWidthUnit()
            ),
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "CentroidFill":
        symbol_layer_dict = {
            "type": "centroid",
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "PointPatternFill":
        # TODO: implement
        symbol_layer_dict = {
            "type": "pointpattern",
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "RandomMarkerFill":
        # TODO: implement
        symbol_layer_dict = {
            "type": "randommarker",
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "LinePatternFill":
        # TODO: implement
        symbol_layer_dict = {
            "type": "linepattern",
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "RasterFill":
        # TODO: implement
        symbol_layer_dict = {
            "type": "raster",
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "SVGFill":
        # TODO: implement
        symbol_layer_dict = {
            "type": "simple",
            "color": symbol_layer.color().name(),
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "GradientFill":
        # TODO: implement
        symbol_layer_dict = {
            "type": "gradient",
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "ShapeburstFill":
        # TODO: implement
        symbol_layer_dict = {
            "type": "shapeburst",
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "GeometryGenerator":
        # never to be supported...
        symbol_layer_dict = {
            "type": "unsupported",
            "color": "#000000",
            "level": symbol_layer.renderingPass(),
        }
    else:
        raise Exception("Unexpected symbol layer type")

    return symbol_layer_dict


def _get_hybrid_symbol_data(symbol_layer: QgsSymbolLayer) -> dict:
    # TODO: implement
    symbol_layer_dict = {
        "type": symbol_layer.layerType().lower(),
        "color": symbol_layer.color().name(),
        "level": symbol_layer.renderingPass(),
        # "geometry": symbol_layer.geometryExpression(),
    }

    return symbol_layer_dict
