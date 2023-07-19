from qgis.core import QgsSymbolLayer
from utils import convert_to_point
from PyQt5.QtCore import Qt

from .marker import get_point_symbol_data


def _get_penstyle_from(symbol_layer: QgsSymbolLayer) -> dict:
    penstyle = {
        "stroke": {
            Qt.NoPen: "no pen",
            Qt.SolidLine: "solid line",
            Qt.DashLine: "dash line",
            Qt.DotLine: "dot line",
            Qt.DashDotLine: "dash dot line",
            Qt.DashDotDotLine: "dash dot dot line",
            Qt.CustomDashLine: "custom dash line",
        }.get(symbol_layer.penStyle(), "solid line"),
        "join": {
            Qt.MiterJoin: "miter",
            Qt.BevelJoin: "bevel",
            Qt.RoundJoin: "round",
        }.get(symbol_layer.penJoinStyle(), "miter"),
        "cap": {Qt.FlatCap: "flat", Qt.SquareCap: "square", Qt.RoundCap: "round"}.get(
            symbol_layer.penCapStyle(), "flat"
        ),
    }

    # custom dash pattern
    if symbol_layer.useCustomDashPattern():
        penstyle["dash_pattern"] = [
            convert_to_point(dash_value, symbol_layer.customDashPatternUnit())
            for dash_value in symbol_layer.customDashVector()
        ]

    return penstyle


def get_line_symbol_data(symbol_layer: QgsSymbolLayer) -> dict:
    if symbol_layer.layerType() == "SimpleLine":
        symbol_layer_dict = {
            "type": "simple",
            "color": symbol_layer.color().name(),
            "penstyle": _get_penstyle_from(symbol_layer),
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
        symbol_layer_dict = {
            "type": "marker",
            "markers": [
                get_point_symbol_data(marker) for marker in symbol_layer.subSymbol()
            ],
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
