import os

import processing
from qgis.core import (
    QgsProject,
    QgsRendererCategory,
    QgsVectorFileWriter,
    QgsVectorLayer,
)

from unit_converter import UnitConverter
from utils import write_json
import shutil

symbol_types = {
    0: "point",
    1: "line",
    2: "polygon",
}


class VectorLayer:
    def __init__(
        self,
        layer: QgsVectorLayer,
        directory: str,
        layer_original_name: str,
        svgs: list,
        rasters: list,
    ):
        self.layer = layer
        self.renderer_type = layer.renderer().type()
        self.directory = directory
        self.layer_original_name = layer_original_name
        self.symbols = []
        self.svgs_path = os.path.join(directory, "assets", "symbol_svg")
        self.rasters_path = os.path.join(directory, "assets", "symbol_raster")
        self.svgs = svgs
        self.rasters = rasters

    def generate_single_symbols(self):
        # SHPを出力
        self.export_simple_symbol_shp()
        # symbol layerごとにスタイルJsonを作成
        symbol = self.layer.renderer().symbol()

        symbol_dict = self.generate_symbol_dict(symbol)

        write_json(
            symbol_dict, os.path.join(self.directory, f"{self.layer.name()}.json")
        )

    def generate_category_symbols(self):
        # category id
        idx = 0
        for category in self.layer.renderer().categories():
            # LegendごとにSHPを作成
            self.export_shps_by_category(category, idx)
            # スタイルJsonを作成
            symbol = category.symbol()

            symbol_dict = self.generate_symbol_dict(symbol)
            symbol_dict["legend"] = category.label()

            write_json(
                symbol_dict,
                os.path.join(self.directory, f"{self.layer.name()}_{idx}.json"),
            )

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

        label_dict = {"layer": self.layer_original_name, "labels": []}

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
        if label_dict["labels"]:
            write_json(
                label_dict,
                os.path.join(
                    self.directory, f"label_{self.layer.name().split('_')[1]}.json"
                ),
            )

    def generate_symbol_dict(self, symbol):
        symbol_dict = {
            "layer": self.layer_original_name,
        }
        symbol_list = []
        for symbol_layer in symbol:
            symbol_type = symbol_layer.type()

            # point
            if symbol_type == 0:
                pt_size = UnitConverter(symbol_layer.size(), symbol_layer.sizeUnit())
                symbol_layer_dict = {
                    "type": symbol_types[symbol_type],
                    "size": pt_size.convert_to_point(),
                    "fill_color": symbol_layer.color().name(),
                    "outline_color": symbol_layer.strokeColor().name(),
                    "symbol_layer_type": symbol_layer.layerType()
                    .split("Marker")[0]
                    .lower(),
                    "symbol_path": "",
                }

                if symbol_layer.layerType() == "RasterMarker":
                    symbol_layer_dict["outline_width"] = None
                    symbol_layer_dict[
                        "symbol_path"
                    ] = "assets/symbol_raster/" + self.export_raster_symbol(
                        symbol_layer
                    )

                else:
                    outline_size = UnitConverter(
                        symbol_layer.strokeWidth(),
                        symbol_layer.strokeWidthUnit(),
                    )
                    symbol_layer_dict["outline_width"] = outline_size.convert_to_point()

                if symbol_layer.layerType() == "SvgMarker":
                    symbol_layer_dict[
                        "symbol_path"
                    ] = "assets/symbol_svg/" + self.export_svg_symbol(symbol_layer)

            # line
            if symbol_type == 1:
                line_size = UnitConverter(
                    symbol_layer.width(), symbol_layer.widthUnit()
                )
                symbol_layer_dict = {
                    "type": symbol_types[symbol_type],
                    "color": symbol_layer.color().name(),
                    "width": line_size.convert_to_point(),
                }

            # polygon
            if symbol_type == 2:
                outline_size = UnitConverter(
                    symbol_layer.strokeWidth(),
                    symbol_layer.strokeWidthUnit(),
                )
                symbol_layer_dict = {
                    "type": symbol_types[symbol_type],
                    "fill_color": symbol_layer.fillColor().name(),
                    "outline_color": symbol_layer.strokeColor().name(),
                    "outline_width": outline_size.convert_to_point(),
                }
            symbol_list.append(symbol_layer_dict)
        symbol_dict["symbol"] = symbol_list
        return symbol_dict

    def export_svg_symbol(self, symbol_layer):
        # create svg folder if not exists
        if not os.path.exists(self.svgs_path):
            os.makedirs(self.svgs_path)
        # make svg file name as 0.svg, 1.svg etc.
        if symbol_layer.path() in self.svgs:
            # svg already exists in svgs folder
            svg_index = self.svgs.index(symbol_layer.path())
        else:
            # svg not exists in svgs folder
            self.svgs.append(symbol_layer.path())
            svg_index = self.svgs.index(symbol_layer.path())
            shutil.copy(
                symbol_layer.path(),
                os.path.join(self.svgs_path, f"{svg_index}.svg"),
            )
        return f"{svg_index}.svg"

    def export_raster_symbol(self, symbol_layer):
        # create raster folder if not exists
        if not os.path.exists(self.rasters_path):
            os.makedirs(self.rasters_path)
        # make rster file name as 0.jpg, 1.png etc.
        if symbol_layer.path() in self.rasters:
            # raster already exists in rasters folder
            raster_index = self.rasters.index(symbol_layer.path())
        else:
            # raster not exists in rasters folder
            self.rasters.append(symbol_layer.path())
            raster_index = self.rasters.index(symbol_layer.path())
            shutil.copy(
                symbol_layer.path(),
                os.path.join(
                    self.rasters_path,
                    f"{raster_index}{os.path.splitext(symbol_layer.path())[1]}",
                ),
            )
        return f"{raster_index}{os.path.splitext(symbol_layer.path())[1]}"

    def update_svgs_list(self):
        return self.svgs

    def update_rasters_list(self):
        return self.rasters

    def generate_symbols(self):
        if self.renderer_type == "categorizedSymbol":
            self.generate_category_symbols()
        if self.renderer_type == "singleSymbol":
            self.generate_single_symbols()
