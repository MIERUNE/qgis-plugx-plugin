import os

from qgis.core import QgsSymbolLayer, Qgis
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from utils import convert_to_point


def get_asset_dir(output_dir: str):
    return os.path.join(output_dir, "assets")


def get_asset_name(symbol_layer: QgsSymbolLayer):
    return os.path.basename(symbol_layer.path())


def to_rgba(color: QColor):
    """calculate #rgba from #rgb + alpha percent value"""

    # alpha percentage value (0.0-1.0) to hex (00-ff)
    alpha = hex(int(color.alphaF() * 255))[2:].zfill(2)

    return f"{color.name()}{alpha}"


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

    penstyle = {
        "stroke": {
            Qt.NoPen: "nopen",
            Qt.SolidLine: "solid",
            Qt.DashLine: "dash",
            Qt.DotLine: "dash",
            Qt.DashDotLine: "dash",
            Qt.DashDotDotLine: "dash",
            Qt.CustomDashLine: "dash",
            # treat preset dashes as "dash" for more generic: Issue #114
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
    }

    if symbol_layer.type() != Qgis.SymbolType.Fill:  # only fill symbol has no cap
        penstyle["cap"] = {
            Qt.FlatCap: "flat",
            Qt.SquareCap: "square",
            Qt.RoundCap: "round",
        }.get(
            symbol_layer.penCapStyle(), "flat"  # fallback
        )

    # dash pattern
    if penstyle["stroke"] == "dash":
        if symbol_layer.useCustomDashPattern():
            dash_pattern = [
                convert_to_point(dash_value, symbol_layer.customDashPatternUnit())
                for dash_value in symbol_layer.customDashVector()
            ]
        else:
            # preset dash pattern: each value is multiplier to width
            dash_pattern_raw = {
                Qt.DashLine: [4, 2],
                Qt.DotLine: [1, 2],
                Qt.DashDotLine: [4, 2, 1, 2],
                Qt.DashDotDotLine: [4, 2, 1, 2, 1, 2],
            }.get(symbol_layer.penStyle(), [4, 2])
            # as real length, in point
            dash_pattern = [
                dash_value
                * convert_to_point(symbol_layer.width(), symbol_layer.widthUnit())
                for dash_value in dash_pattern_raw
            ]

        penstyle["dash_pattern"] = dash_pattern

    return penstyle
