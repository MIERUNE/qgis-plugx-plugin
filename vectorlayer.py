import json
import os

import processing
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from qgis.gui import *

from unit_converter import UnitConverter

symbol_types = {
    0: "point",
    1: "line",
    2: "polygon",
}


class VectorLayer:
    def __init__(self, layer: QgsVectorLayer, directory: str):
        self.layer = layer
        self.renderer_type = layer.renderer().type()
        self.directory = directory

        self.symbols = []

    def generate_single_symbols(self):
        # SHPを出力
        self.export_simple_symbol_shp()

        symbol = self.layer.renderer().symbol()
        symbol_type = symbol.symbolLayer(0).type()
        symbol_dict = {}
        # point
        if symbol_type == 0:
            pt_size = UnitConverter(symbol.size(), symbol.sizeUnit())
            symbol_dict = {
                "type": symbol_types[symbol_type],
                # "size": symbol.size(),
                "size": pt_size.convert_to_point(),
                "fill_color": symbol.color().name(),
                "outline_color": symbol.symbolLayer(0).strokeColor().name(),
                "outline_width": symbol.symbolLayer(0).strokeWidth(),
            }

        # line
        if symbol_type == 1:
            line_size = UnitConverter(
                symbol.symbolLayer(0).width(), symbol.symbolLayer(0).widthUnit()
            )
            symbol_dict = {
                "type": symbol_types[symbol_type],
                "color": symbol.symbolLayer(0).color().name(),
                # "width": symbol.symbolLayer(0).width(),
                "width": line_size.convert_to_point(),
            }

        # polygon
        if symbol_type == 2:
            outline_size = UnitConverter(
                symbol.symbolLayer(0).strokeWidth(),
                symbol.symbolLayer(0).strokeWidthUnit(),
            )
            symbol_dict = {
                "type": symbol_types[symbol_type],
                "fill_color": symbol.symbolLayer(0).fillColor().name(),
                "outline_color": symbol.symbolLayer(0).strokeColor().name(),
                # "outline_width": symbol.symbolLayer(0).strokeWidth(),
                "outline_width": outline_size.convert_to_point(),
            }

        write_json(
            symbol_dict, os.path.join(self.directory, f"{self.layer.name()}.json")
        )

    def generate_category_symbols(self):
        symbol_items = self.layer.renderer().legendSymbolItems()
        symbol_type = symbol_items[0].symbol().symbolLayer(0).type()

        idx = 0
        for category in self.layer.renderer().categories():
            symbol = category.symbol()
            # LegendごとにSHPを作成
            self.export_shps_by_category(category, idx)

            # スタイルJsonを作成
            symbol_dict = None
            # point
            if symbol_type == 0:
                outline_size = UnitConverter(
                    symbol.symbolLayer(0).strokeWidth(),
                    symbol.symbolLayer(0).strokeWidthUnit(),
                )
                symbol_dict = {
                    "type": symbol_types[symbol_type],
                    "size": symbol.size(),
                    "legend": category.label(),
                    "fill_color": symbol.color().name(),
                    "outline_color": symbol.symbolLayer(0).strokeColor().name(),
                    "outline_width": outline_size.convert_to_point(),
                    # "outline_width": symbol.symbolLayer(0).strokeWidth(),
                }

            # line
            if symbol_type == 1:
                line_size = UnitConverter(
                    symbol.symbolLayer(0).width(), symbol.symbolLayer(0).widthUnit()
                )
                symbol_dict = {
                    "type": symbol_types[symbol_type],
                    "legend": category.label(),
                    "color": symbol.symbolLayer(0).color().name(),
                    "width": line_size.convert_to_point(),
                }

            # polygon
            if symbol_type == 2:
                outline_size = UnitConverter(
                    symbol.symbolLayer(0).strokeWidth(),
                    symbol.symbolLayer(0).strokeWidthUnit(),
                )
                symbol_dict = {
                    "type": symbol_types[symbol_type],
                    "legend": category.label(),
                    "fill_color": symbol.symbolLayer(0).fillColor().name(),
                    "outline_color": symbol.symbolLayer(0).strokeColor().name(),
                    # "outline_width": symbol.symbolLayer(0).strokeWidth(),
                    "outline_width": outline_size.convert_to_point(),
                }

            with open(os.path.join(self.directory, f"{self.layer.name()}_{idx}.json"), mode='w') as f:
                json.dump(symbol_dict, f, ensure_ascii=False)
            
            idx += 1

    def export_shps_by_category(self, category: QgsRendererCategory, idx: int):
        value = category.value()
        features = self.get_feat_by_value(value)
        shp_path = os.path.join(self.directory, f"{self.layer.name()}_{idx}.shp")
        output_layer = QgsVectorFileWriter(
            shp_path,
            "UTF-8",
            self.layer.fields(),
            self.layer.wkbType(),
            QgsProject.instance().crs(),
            "ESRI Shapefile",
        )
        output_layer.addFeatures(features)
        del output_layer

    def export_simple_symbol_shp(self):
        shp_path = os.path.join(self.directory, f"{self.layer.name()}.shp")
        output_layer = QgsVectorFileWriter(
            shp_path,
            "UTF-8",
            self.layer.fields(),
            self.layer.wkbType(),
            QgsProject.instance().crs(),
            "ESRI Shapefile",
        )
        output_layer.addFeatures(self.layer.getFeatures())
        del output_layer

    def get_feat_by_value(self, value: str) -> list:
        result = []
        if self.renderer_type == "singleSymbol":
            pass

        if self.renderer_type == "categorizedSymbol":
            field = self.layer.renderer().classAttribute()

            for feature in self.layer.getFeatures():
                if feature[field] == value:
                    result.append(feature)
        return result

    def generate_label_json(self, all_labels_layer: QgsVectorLayer, layername: str):
        label_layer = processing.run(
            "native:extractbyattribute",
            {
                "INPUT": all_labels_layer,
                "FIELD": "Layer",
                "OPERATOR": 0,  # '='
                "VALUE": layername,
                "OUTPUT": "TEMPORARY_OUTPUT",
            },
        )["OUTPUT"]

        label_dict = {"labels": []}

        for feature in label_layer.getFeatures():
            if not feature["LabelUnplaced"]:
                # バッファーがない場合は色を#000000にする
                buffer_color = (
                    "#000000"
                    if not feature["BufferColor"]
                    else str(feature["BufferColor"])
                )

                label_dict["labels"].append(
                    {
                        "x": feature.geometry().asPoint().x(),
                        "y": feature.geometry().asPoint().y(),
                        "rotation": feature["LabelRotation"],
                        "text": feature["LabelText"],
                        "font": feature["Family"],
                        "size": feature["Size"],
                        "bold": feature["Bold"],
                        "underline": feature["Underline"],
                        "text:color": feature["Color"],
                        "text:opacity": feature["FontOpacity"],
                        "buffer:width": feature["BufferSize"],
                        "buffer:color": buffer_color,
                        "buffer:opacity": feature["BufferOpacity"],
                    }
                )
        with open(os.path.join(self.directory, f"label_{self.layer.name().split('_')[1]}.json"), mode='w') as f:
            json.dump(label_dict, f, ensure_ascii=False)

    def generate_symbols(self):
        if self.renderer_type == "categorizedSymbol":
            self.generate_category_symbols()
        if self.renderer_type == "singleSymbol":
            self.generate_single_symbols()
