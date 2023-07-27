from qgis.core import QgsSymbolLayer
from utils import convert_to_point
from PyQt5.QtCore import Qt

from .marker import get_point_symbol_data
from translator.vector.symbol.utils import to_rgba


def _get_penstyle_from(symbol_layer: QgsSymbolLayer) -> dict:
    penstyle = {
        "stroke": {
            Qt.NoPen: "nopen",
            Qt.SolidLine: "solid",
            Qt.DashLine: "dash",
            Qt.DotLine: "dot",
            Qt.DashDotLine: "dashdot",
            Qt.DashDotDotLine: "dashdotdot",
            Qt.CustomDashLine: "customdash",
        }.get(
            symbol_layer.penStyle(), "solid"  # fallback
        ),
        "join": {
            Qt.MiterJoin: "miter",
            Qt.BevelJoin: "bevel",
            Qt.RoundJoin: "round",
        }.get(
            symbol_layer.penJoinStyle(), "miter"  # fallback
        ),
        "cap": {Qt.FlatCap: "flat", Qt.SquareCap: "square", Qt.RoundCap: "round"}.get(
            symbol_layer.penCapStyle(), "flat"  # fallback
        ),
    }

    # custom dash pattern
    if symbol_layer.useCustomDashPattern():
        penstyle["dash_pattern"] = [
            convert_to_point(dash_value, symbol_layer.customDashPatternUnit())
            for dash_value in symbol_layer.customDashVector()
        ]

    return penstyle


def get_line_symbol_data(symbol_layer: QgsSymbolLayer, symbol_opacity: float) -> dict:
    if symbol_layer.layerType() == "SimpleLine":
        symbol_layer_dict = {
            "type": "simple",
            "color": to_rgba(symbol_layer.color()),
            "penstyle": _get_penstyle_from(symbol_layer),
            "width": convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
            "level": symbol_layer.renderingPass(),
            "opacity": symbol_opacity,
        }

    elif symbol_layer.layerType() == "InterpolatedLine":
        # TODO: implement
        symbol_layer_dict = {
            "type": "interpolated",
            "color": to_rgba(symbol_layer.color()),
            "width": convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
            "level": symbol_layer.renderingPass(),
            "opacity": symbol_opacity,
        }
    elif symbol_layer.layerType() == "MarkerLine":
        symbol_layer_dict = {
            "type": "marker",
            "markers": [
                get_point_symbol_data(marker, symbol_layer.subSymbol().opacity())
                for marker in symbol_layer.subSymbol()
            ],
            "interval": convert_to_point(
                symbol_layer.interval(), symbol_layer.intervalUnit()
            ),
            "level": symbol_layer.renderingPass(),
            "opacity": symbol_opacity,
        }
    elif symbol_layer.layerType() == "HashLine":
        # TODO: implement
        symbol_layer_dict = {
            "type": "hash",
            "level": symbol_layer.renderingPass(),
            "opacity": symbol_opacity,
        }
    elif symbol_layer.layerType() == "RasterLine":
        # TODO: implement
        symbol_layer_dict = {
            "type": "raster",
            "width": convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
            "level": symbol_layer.renderingPass(),
            "opacity": symbol_opacity,
        }
    elif symbol_layer.layerType() == "Lineburst":
        # TODO: implement
        symbol_layer_dict = {
            "type": "lineburst",
            "width": convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
            "level": symbol_layer.renderingPass(),
            "opacity": symbol_opacity,
        }
    elif symbol_layer.layerType() == "ArrowLine":
        # TODO: implement
        symbol_layer_dict = {
            "type": "arrow",
            "width": convert_to_point(symbol_layer.width(), symbol_layer.widthUnit()),
            "level": symbol_layer.renderingPass(),
            "opacity": symbol_opacity,
        }
    elif symbol_layer.layerType() == "GeometryGenerator":
        # never to be supported...
        symbol_layer_dict = {
            "type": "unsupported",
            "width": 0,
            "color": "#000000",
            "level": symbol_layer.renderingPass(),
            "opacity": symbol_opacity,
        }
    else:
        raise Exception("Unexpected symbol layer type")

    return symbol_layer_dict
