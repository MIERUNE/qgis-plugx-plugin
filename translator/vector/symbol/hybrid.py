import os
import shutil
from qgis.core import Qgis, QgsSymbolLayer, QgsSymbol
from utils import convert_to_point
from PyQt5.QtCore import Qt


def _get_hybrid_symbol_data(symbol_layer: QgsSymbolLayer) -> dict:
    # TODO: implement
    symbol_layer_dict = {
        "type": symbol_layer.layerType().lower(),
        "color": symbol_layer.color().name(),
        "level": symbol_layer.renderingPass(),
        # "geometry": symbol_layer.geometryExpression(),
    }

    return symbol_layer_dict
