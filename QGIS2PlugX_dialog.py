import json
import os

import processing
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QMessageBox
from qgis.core import (
    QgsMapLayer,
    QgsProject,
    QgsMapLayerModel,
    QgsRasterLayer,
    QgsVectorLayer,
)
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

        # レイヤー一覧を作成する
        self.load_layer_list()
        # レイヤーの追加・削除に反応して一覧を更新する
        QgsProject.instance().layerWasAdded.connect(self.load_layer_list)
        QgsProject.instance().layerRemoved.connect(self.load_layer_list)

    def load_layer_list(self):
        self.layerListWidget.clear()
        for layer in QgsProject.instance().mapLayers().values():
            if not isinstance(layer, QgsRasterLayer) and not isinstance(
                layer, QgsVectorLayer
            ):
                # ラスター、ベクター以外はスキップ: PointCloudLayer, MeshLayer, ...
                continue
            icon = QgsMapLayerModel.iconForLayer(layer)
            item = QListWidgetItem(icon, layer.name())
            item.setData(Qt.UserRole, layer)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.layerListWidget.addItem(item)

    def run(self):
        # チェックしたレイヤをリストに取得する
        layers = self.get_checked_layers()
        raster_layers = self.get_checked_raster_layers()

        # 処理範囲を取得する
        extent = self.ui.mExtentGroupBox.outputExtent()
        if not extent:
            return

        # 出力先のディレクトリを作成する
        output_dir = self.ui.outputFileWidget.filePath()

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
            extent.xMinimum(),
            extent.yMinimum(),
            extent.xMaximum(),
            extent.yMaximum(),
        ]
        project_json["scale"] = iface.mapCanvas().scale()
        project_json["layers"] = []

        # ラベルSHPを出力する
        canvas = iface.mapCanvas()
        all_labels = processing.run(
            "native:extractlabels",
            {
                "EXTENT": extent,
                "SCALE": canvas.scale(),
                "MAP_THEME": None,
                "INCLUDE_UNPLACED": True,
                "DPI": 96,
                "OUTPUT": "TEMPORARY_OUTPUT",
            },
        )["OUTPUT"]

        for lyr in layers:
            # 指定範囲内の地物を抽出し、元のスタイルを適用する
            qml_path = os.path.join(output_dir, "layer.qml")
            lyr.saveNamedStyle(
                qml_path, categories=QgsMapLayer.Symbology | QgsMapLayer.Labeling
            )

            lyr_intersected = processing.run(
                "native:extractbyextent",
                {
                    "INPUT": lyr,
                    "EXTENT": extent,
                    "CLIP": True,
                    "OUTPUT": "TEMPORARY_OUTPUT",
                },
            )["OUTPUT"]
            lyr_intersected.loadNamedStyle(qml_path)
            if os.path.exists(qml_path):
                os.remove(qml_path)

            # レイヤ名をlayer_indexに変更する
            lyr_intersected.setName(f"layer_{layers.index(lyr)}")
            project_json["layers"].append(lyr_intersected.name())

            # スタイル出力用のVectorLayerインスランスを作成する
            maplyr = VectorLayer(lyr_intersected, output_dir)

            # シンボロジごとのSHPとjsonを出力
            maplyr.generate_symbols()

            if maplyr.layer.labelsEnabled():
                # レイヤlabelのjsonを出力
                maplyr.generate_label_json(all_labels, lyr.name())

        for rlyr in raster_layers:
            # 指定範囲内のラスターを抽出

            rasterlayer = RasterLayer(rlyr, extent, output_dir)
            rasterlayer.xyz_to_png()

            # summarize raster info json
            rasterlayer.write_json()

            # Add layer to project json
            project_json["layers"].append(rlyr.name())

        # project.jsonを出力
        with open(os.path.join(output_dir, "project.json"), mode="w") as f:
            json.dump(project_json, f, ensure_ascii=False)

        QMessageBox.information(
            None,
            "完了",
            f"処理が完了しました。\
            \n\n出力先:\n{output_dir}",
        )

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
