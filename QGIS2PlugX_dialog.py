import json
import os

import processing
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from qgis.gui import *
from qgis.PyQt import uic
from qgis.utils import iface

from rasterlayer import RasterLayer
from vectorlayer import VectorLayer


class QGIS2PlugX_dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(
            os.path.join(os.path.dirname(__file__), "QGIS2PlugX_dialog.ui"), self
        )

        self.ui.pushButton_run.clicked.connect(self.run)
        self.ui.pushButton_cancel.clicked.connect(self.close)
        self.ui.mExtentGroupBox.setCurrentExtent(
            iface.mapCanvas().extent(), QgsProject.instance().crs()
        )
        self.ui.mExtentGroupBox.setMapCanvas(iface.mapCanvas())
        self.ui.mExtentGroupBox.setOutputCrs(QgsProject.instance().crs())

        self.load_layer_list()

        self.layers = None
        self.extent = None

    def load_layer_list(self):
        vector_names = [
            l.layer().name()
            for l in QgsProject.instance().layerTreeRoot().children()
            if isinstance(l.layer(), QgsVectorLayer)
        ]

        for item in vector_names:
            i = QListWidgetItem(item)
            i.setFlags(i.flags() | Qt.ItemIsUserCheckable)
            i.setCheckState(Qt.Unchecked)
            self.layerListWidget.addItem(i)

        raster_names = [
            r.layer().name()
            for r in QgsProject.instance().layerTreeRoot().children()
            if isinstance(r.layer(), QgsRasterLayer)
        ]

        for item in raster_names:
            i = QListWidgetItem(item)
            i.setFlags(i.flags() | Qt.ItemIsUserCheckable)
            i.setCheckState(Qt.Unchecked)
            self.rasterLayerListWidget.addItem(i)

    def run(self):
        # チェックしたレイヤをリストに取得する
        self.layers = self.get_checked_layers()
        self.raster_layers = self.get_checked_raster_layers()

        if not self.layers and not self.raster_layers:
            return
        # 処理範囲を取得する
        self.extent = self.ui.mExtentGroupBox.outputExtent()
        if not self.extent:
            return

        # 出力先のディレクトリを作成する
        directory = self.ui.outputFileWidget.filePath()

        # project.jsonにレイヤ順序情報を書き出す
        project_json = {}

        project_json["project_name"] = os.path.basename(
            QgsProject.instance().fileName()
        ).split(".")[0]
        project_json["crs"] = QgsProject.instance().crs().authid()
        project_json["crs_type"] = (
            "geographic" if QgsProject.instance().crs().isGeographic() else "projected"
        )
        project_json["extent"] = [
            self.extent.xMinimum(),
            self.extent.yMinimum(),
            self.extent.xMaximum(),
            self.extent.yMaximum(),
        ]
        project_json["scale"] = iface.mapCanvas().scale()
        project_json["layers"] = []

        # ラベルSHPを出力する
        canvas = iface.mapCanvas()
        all_labels = processing.run(
            "native:extractlabels",
            {
                "EXTENT": self.extent,
                "SCALE": canvas.scale(),
                "MAP_THEME": None,
                "INCLUDE_UNPLACED": True,
                "DPI": 96,
                "OUTPUT": "TEMPORARY_OUTPUT",
            },
        )["OUTPUT"]

        for lyr in self.layers:
            # 指定範囲内の地物を抽出し、元のスタイルを適用する
            qml_path = os.path.join(directory, "layer.qml")
            lyr.saveNamedStyle(
                qml_path, categories=QgsMapLayer.Symbology | QgsMapLayer.Labeling
            )

            lyr_intersected = processing.run(
                "native:extractbyextent",
                {
                    "INPUT": lyr,
                    "EXTENT": self.extent,
                    "CLIP": True,
                    "OUTPUT": "TEMPORARY_OUTPUT",
                },
            )["OUTPUT"]
            lyr_intersected.loadNamedStyle(qml_path)
            if os.path.exists(qml_path):
                os.remove(qml_path)

            # レイヤ名をlayer_indexに変更する
            lyr_intersected.setName(f"layer_{self.layers.index(lyr)}")
            project_json["layers"].append(lyr_intersected.name())

            # スタイル出力用のVectorLayerインスランスを作成する
            maplyr = VectorLayer(lyr_intersected, directory)

            # シンボロジごとのSHPとjsonを出力
            maplyr.generate_symbols()

            if maplyr.layer.labelsEnabled():
                # レイヤlabelのjsonを出力
                maplyr.generate_label_json(all_labels, lyr.name())

        for rlyr in self.raster_layers:
            # 指定範囲内のラスターを抽出

            rasterlayer = RasterLayer(rlyr, self.extent, directory)
            rasterlayer.xyz_to_png()

            # summarize raster info json
            rasterlayer.write_json()

            # Add layer to project json
            project_json["layers"].append(rlyr.name())

        # project.jsonを出力
        with open(os.path.join(directory, "project.json"), mode="w") as f:
            json.dump(project_json, f, ensure_ascii=False)

        QMessageBox.information(None, "完了", f"処理が完了しました。\n\n出力先:\n{directory}")


    def get_checked_layers(self):
        layers = []
        for i in range(self.layerListWidget.count()):
            if self.layerListWidget.item(i).checkState() == Qt.Checked:
                layers.append(
                    QgsProject.instance().mapLayersByName(
                        self.layerListWidget.item(i).text()
                    )[0]
                )
        return layers

    def get_checked_raster_layers(self):
        raster_layers = []
        for i in range(self.rasterLayerListWidget.count()):
            if self.rasterLayerListWidget.item(i).checkState() == Qt.Checked:
                raster_layers.append(
                    QgsProject.instance().mapLayersByName(
                        self.rasterLayerListWidget.item(i).text()
                    )[0]
                )
        return raster_layers
