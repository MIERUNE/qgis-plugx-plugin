from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from qgis.gui import *
from qgis.PyQt import uic
from qgis.utils import iface

import os
import processing
import json


class MapLayer:
    def __init__(self, layer: QgsVectorLayer, directory: str):
        self.layer = layer
        self.renderer_type = layer.renderer().type()
        self.directory = directory

        self.symbols = []

    def generate_symbol_files(self):
        symbol_items = self.layer.renderer().legendSymbolItems()
        symbol_type = symbol_items[0].symbol().symbolLayer(0).type()

        for category in self.layer.renderer().categories():
            symbol = category.symbol()
            # LegendごとにSHPを作成
            self.export_shps_by_category(category)

            # スタイルJsonを作成
            symbol_dict = []
            # point
            if symbol_type == 0:
                symbol_dict.append({
                    "type": symbol_type,
                    "legend": category.label(),
                    "color": symbol.color().name(),
                    "size": symbol.size(),
                })

            # line
            if symbol_type == 1:
                symbol_dict.append({
                    "type": symbol_type,
                    "legend": category.label(),
                    "color": symbol.symbolLayer(0).color().name(),
                    "width": symbol.symbolLayer(0).width(),
                })

            # polygon
            if symbol_type == 2:
                symbol_dict.append({
                    "type": symbol_type,
                    "legend": category.label(),
                    "fill_color": symbol.symbolLayer(0).fillColor().name(),
                    "outline_color": symbol.symbolLayer(0).strokeColor().name(),
                    "outline_width": symbol.symbolLayer(0).strokeWidth(),
                    "outline_unit": symbol.symbolLayer(0).strokeWidthUnit()
                })

            def write_json(data: dict, filepath: str):
                # Convert dictionary to JSON string
                json_data = json.dumps(data)

                # Write JSON string to file
                with open(filepath, "w") as outfile:
                    outfile.write(json_data)

            write_json(symbol_dict, os.path.join(self.directory, f"{self.layer.name()}_{category.value()}.json"))

    def export_shps_by_category(self, category: QgsRendererCategory):
        value = category.value()
        feature_ids = self.get_featids_by_symbol(value)
        shp_path = os.path.join(self.directory, f"{self.layer.name()}_{category.label()}.shp")

        print(f'@id = {" or ".join(feature_ids)}')
        if feature_ids:
            try:processing.run("native:extractbyexpression",
                           {'INPUT': self.layer,
                            'EXPRESSION': f'{" or ".join(feature_ids)}',
                            'OUTPUT': shp_path})
            except Exception as e:
                print(e)

    def get_featids_by_symbol(self, value: str) -> list:
        result = []
        if self.renderer_type == "singleSymbol":
            pass

        if self.renderer_type == "categorizedSymbol":
            field = self.layer.renderer().classAttribute()
            # values = [category.value() for category in self.renderer().categories()]

            for feature in self.layer.getFeatures():
                if feature[field] == value:
                    result.append(f"@id = {str(feature.id())}")
        return result


