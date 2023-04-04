import os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from qgis.gui import *
from qgis.PyQt import uic
from qgis.utils import iface


def main():
    layer = iface.activeLayer()

    print(get_polygon_symbol(layer))


def get_polygon_symbol(layer: QgsVectorLayer):
    result = []

    symbol_items = layer.renderer().legendSymbolItems()
    for symbol_item in symbol_items:
        result.append({
            "type": symbol_item.symbol().symbolLayer(0).type(),
            "legend": symbol_item.label(),
            "fill_color": symbol_item.symbol().symbolLayer(0).fillColor().getRgb(),
            "outline_color": symbol_item.symbol().symbolLayer(0).strokeColor().getRgb(),
            "outline_width": symbol_item.symbol().symbolLayer(0).strokeWidth(),
            "outline_unit": symbol_item.symbol().symbolLayer(0).strokeWidthUnit()
        })
    return result

def get_polygon_label(layer: QgsVectorLayer):
    # use "native:extractlabels" algorithm
    pass


if __name__ == "__console__":
    main()
