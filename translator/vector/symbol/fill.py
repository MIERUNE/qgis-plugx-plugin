import os
import shutil
from qgis.core import Qgis, QgsSymbolLayer, QgsSymbol
from utils import convert_to_point
from PyQt5.QtCore import Qt


def get_polygon_symbol_data(symbol_layer: QgsSymbolLayer) -> dict:
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
            "type": "svg",
            "color": symbol_layer.color().name(),
            "outline_color": symbol_layer.svgStrokeColor().name(),
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
