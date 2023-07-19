import os
import shutil
from qgis.core import Qgis, QgsSymbolLayer, QgsSymbol
from utils import convert_to_point
from PyQt5.QtCore import Qt


def _get_pen_style_from_id(pen_style_id):
    pen_style_names = {
        Qt.NoPen: "no pen",
        Qt.SolidLine: "solid line",
        Qt.DashLine: "dash line",
        Qt.DotLine: "dot line",
        Qt.DashDotLine: "dash dot line",
        Qt.DashDotDotLine: "dash dot dot line",
        Qt.CustomDashLine: "custom dash line",
    }
    return pen_style_names.get(pen_style_id, "unknown pen style")


def _get_cap_style_from_id(cap_style_id):
    cap_style_names = {Qt.FlatCap: "flat", Qt.SquareCap: "square", Qt.RoundCap: "round"}
    return cap_style_names.get(cap_style_id, "unknown cap style")


def _get_join_style_from_id(join_style_id):
    join_style_names = {
        Qt.MiterJoin: "miter",
        Qt.BevelJoin: "bevel",
        Qt.RoundJoin: "round",
    }
    return join_style_names.get(join_style_id, "unknown join style")


def get_line_symbol_data(symbol_layer: QgsSymbolLayer) -> dict:
    if symbol_layer.layerType() == "SimpleLine":
        symbol_layer_dict = {
            "type": "simple",
            "color": symbol_layer.color().name(),
            "stroke_style": _get_pen_style_from_id(symbol_layer.penStyle()),
            "join_style": _get_join_style_from_id(symbol_layer.penJoinStyle()),
            "cap_style": _get_cap_style_from_id(symbol_layer.penCapStyle()),
            "width": convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
            "level": symbol_layer.renderingPass(),
        }
        if symbol_layer.useCustomDashPattern():
            symbol_layer_dict["dash_pattern"] = []
            for dash_value in symbol_layer.customDashVector():
                symbol_layer_dict["dash_pattern"].append(
                    convert_to_point(dash_value, symbol_layer.customDashPatternUnit())
                )

    elif symbol_layer.layerType() == "InterpolatedLine":
        # TODO: implement
        symbol_layer_dict = {
            "type": "interpolated",
            "color": symbol_layer.color().name(),
            "width": convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "MarkerLine":
        symbol_layer_dict = {
            "type": "marker",
            "markers": generate_symbols_data(symbol_layer.subSymbol()),
            "interval": convert_to_point(
                symbol_layer.interval(), symbol_layer.intervalUnit()
            ),
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
