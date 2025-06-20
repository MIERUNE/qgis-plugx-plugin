from qgis.core import (
    QgsSymbolLayer,
    QgsMarkerSymbolLayer,
    QgsLineSymbolLayer,
    QgsFillSymbolLayer,
)
from qgis.PyQt.QtCore import Qt

from plugx_utils import convert_to_point

PRESET_DASHPATTERN_MULTIPLIER = {
    Qt.PenStyle.DashLine: [4, 2],  # ----  ----  ----...
    Qt.PenStyle.DotLine: [1, 2],  # -  -  -  -  -...
    Qt.PenStyle.DashDotLine: [4, 2, 1, 2],  # ----  -  ----  -  ----...
    Qt.PenStyle.DashDotDotLine: [4, 2, 1, 2, 1, 2],  # ----  -  -  ----  -  -  ----...
}

STROKE_STYLE_DICT = {
    Qt.PenStyle.NoPen: "nopen",
    Qt.PenStyle.SolidLine: "solid",
    Qt.PenStyle.DashLine: "dash",
    Qt.PenStyle.DotLine: "dash",
    Qt.PenStyle.DashDotLine: "dash",
    Qt.PenStyle.DashDotDotLine: "dash",
    Qt.PenStyle.CustomDashLine: "dash",
    # treat preset dashes as "dash" for more generic: Issue #114
}

JOIN_STYLE_DICT = {
    Qt.PenJoinStyle.MiterJoin: "miter",
    Qt.PenJoinStyle.BevelJoin: "bevel",
    Qt.PenJoinStyle.RoundJoin: "round",
}

CAP_STYLE_DICT = {
    Qt.PenCapStyle.FlatCap: "flat",
    Qt.PenCapStyle.SquareCap: "square",
    Qt.PenCapStyle.RoundCap: "round",
}


def get_penstyle_from(symbol_layer: QgsSymbolLayer) -> dict:
    """
    Args:
        symbol_layer (QgsSymbolLayer): _description_

    Returns:
        dict: {
            "stroke": "solid", // nopen | solid | dash
            "cap": "square",
            "join": "bevel"
            "dash_pattern": [5, 2] // added only when stroke is dash
        }
    """
    if isinstance(symbol_layer, QgsMarkerSymbolLayer):
        penstyle = _get_penstyle_from_marker(symbol_layer)
    elif isinstance(symbol_layer, QgsLineSymbolLayer):
        penstyle = _get_penstyle_from_line(symbol_layer)
    elif isinstance(symbol_layer, QgsFillSymbolLayer):
        penstyle = _get_penstyle_from_fill(symbol_layer)
    else:
        penstyle = {
            "stroke": "solid",
            "cap": "square",
            "join": "bevel",
        }  # unpexpected: fallback

    return penstyle


def _get_penstyle_from_marker(symbol_layer: QgsMarkerSymbolLayer) -> dict:
    penstyle = {
        "stroke": STROKE_STYLE_DICT.get(
            symbol_layer.strokeStyle(),
            STROKE_STYLE_DICT[Qt.PenStyle.SolidLine],  # fallback
        ),
        "join": JOIN_STYLE_DICT.get(
            symbol_layer.penJoinStyle(),
            JOIN_STYLE_DICT[Qt.PenJoinStyle.MiterJoin],  # fallback
        ),
    }

    # dash pattern
    if penstyle["stroke"] == "dash":
        # preset dash pattern: each value is multiplier to width
        dash_pattern_mul = PRESET_DASHPATTERN_MULTIPLIER.get(
            symbol_layer.strokeStyle(),
            PRESET_DASHPATTERN_MULTIPLIER[Qt.PenStyle.DashLine],  # fallback
        )
        # as real length, in point
        dash_pattern = [
            dash_value
            * convert_to_point(
                symbol_layer.strokeWidth(), symbol_layer.strokeWidthUnit()
            )
            for dash_value in dash_pattern_mul
        ]

        penstyle["dash_pattern"] = dash_pattern

    return penstyle


def _get_penstyle_from_fill(symbol_layer: QgsFillSymbolLayer) -> dict:
    # same logic can be used for marker and fill
    return _get_penstyle_from_marker(symbol_layer)  # type: ignore


def _get_penstyle_from_line(symbol_layer: QgsLineSymbolLayer) -> dict:
    penstyle = {
        "stroke": STROKE_STYLE_DICT.get(
            symbol_layer.penStyle(),
            STROKE_STYLE_DICT[Qt.PenStyle.SolidLine],  # fallback
        ),
        "join": JOIN_STYLE_DICT.get(
            symbol_layer.penJoinStyle(),
            JOIN_STYLE_DICT[Qt.PenJoinStyle.MiterJoin],  # fallback
        ),
        "cap": CAP_STYLE_DICT.get(
            symbol_layer.penCapStyle(),
            CAP_STYLE_DICT[Qt.PenCapStyle.FlatCap],  # fallback
        ),
    }

    # dash pattern
    if penstyle["stroke"] == "dash":
        if symbol_layer.useCustomDashPattern():
            dash_pattern = [
                convert_to_point(dash_value, symbol_layer.customDashPatternUnit())
                for dash_value in symbol_layer.customDashVector()
            ]

        else:
            # preset dash pattern: each value is multiplier to width
            dash_pattern_mul = PRESET_DASHPATTERN_MULTIPLIER.get(
                symbol_layer.penStyle(),
                PRESET_DASHPATTERN_MULTIPLIER[Qt.PenStyle.DashLine],  # fallback
            )
            # as real length, in point
            dash_pattern = [
                dash_value
                * convert_to_point(symbol_layer.width(), symbol_layer.widthUnit())
                for dash_value in dash_pattern_mul
            ]
        penstyle["dash_pattern"] = dash_pattern

    elif penstyle["stroke"] == "solid" and symbol_layer.useCustomDashPattern():
        # customized patterns occurs NOT with dash strole but solid stroke
        penstyle["stroke"] = "dash"
        dash_pattern = [
            convert_to_point(dash_value, symbol_layer.customDashPatternUnit())
            for dash_value in symbol_layer.customDashVector()
        ]

        penstyle["dash_pattern"] = dash_pattern

    return penstyle
