from qgis.core import QgsSymbolLayer
from utils import convert_to_point
from PyQt5.QtCore import Qt
from translator.vector.symbol.utils import to_rgba


def _get_brushstyle_from(symbol_layer: QgsSymbolLayer) -> dict:
    return {
        Qt.NoBrush: "nobrush",
        Qt.SolidPattern: "solid",
        Qt.Dense1Pattern: "dense1",
        Qt.Dense2Pattern: "dense2",
        Qt.Dense3Pattern: "dense3",
        Qt.Dense4Pattern: "dense4",
        Qt.Dense5Pattern: "dense5",
        Qt.Dense6Pattern: "dense6",
        Qt.Dense7Pattern: "dense7",
        Qt.HorPattern: "horizontal",
        Qt.VerPattern: "vertical",
        Qt.CrossPattern: "cross",
        Qt.BDiagPattern: "backwarddiagonal",
        Qt.FDiagPattern: "forwarddiagonal",
        Qt.DiagCrossPattern: "crossingdiagonal",
    }.get(
        symbol_layer.brushStyle(), "solid"  # fallback
    )


def get_polygon_symbol_data(symbol_layer: QgsSymbolLayer) -> dict:
    # Case of simple fill
    if symbol_layer.layerType() == "SimpleFill":
        symbol_layer_dict = {
            "type": "simple",
            "color": to_rgba(symbol_layer.fillColor()),
            "brushstyle": _get_brushstyle_from(symbol_layer),
            "outline_color": to_rgba(symbol_layer.strokeColor()),
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
            "type": "svg",
            "color": to_rgba(symbol_layer.color()),
            "outline_color": to_rgba(symbol_layer.svgStrokeColor()),
            "outline_width": convert_to_point(
                symbol_layer.svgStrokeWidth(), symbol_layer.svgStrokeWidthUnit()
            ),
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