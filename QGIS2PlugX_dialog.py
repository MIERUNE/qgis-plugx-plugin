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

        # 処理範囲を取得する
        extent = self.ui.mExtentGroupBox.outputExtent()
        if not extent:
            return

        # 出力先のディレクトリを作成する
        output_dir = self.ui.outputFileWidget.filePath()

        # ラベルSHPを出力する
        all_labels = processing.run(
            "native:extractlabels",
            {
                "EXTENT": extent,
                "SCALE": iface.mapCanvas().scale(),
                "MAP_THEME": None,
                "INCLUDE_UNPLACED": True,
                "DPI": 96,  # TODO: 縮尺から計算すべき
                "OUTPUT": "TEMPORARY_OUTPUT",
            },
        )["OUTPUT"]

        output_layer_names = []
        for layer in layers:
            if isinstance(layer, QgsVectorLayer):
                # 指定範囲内の地物を抽出し、元のスタイルを適用する
                qml_path = os.path.join(output_dir, "layer.qml")
                layer.saveNamedStyle(
                    qml_path, categories=QgsMapLayer.Symbology | QgsMapLayer.Labeling
                )

                layer_intersected = processing.run(
                    "native:extractbyextent",
                    {
                        "INPUT": layer,
                        "EXTENT": extent,
                        "CLIP": True,
                        "OUTPUT": "TEMPORARY_OUTPUT",
                    },
                )["OUTPUT"]
                layer_intersected.loadNamedStyle(qml_path)
                if os.path.exists(qml_path):
                    os.remove(qml_path)

                # レイヤ名をlayer_indexに変更する
                layer_intersected.setName(f"layer_{layers.index(layer)}")
                output_layer_names.append(layer_intersected.name())

                # スタイル出力用のVectorLayerインスランスを作成する
                vector_layer = VectorLayer(layer_intersected, output_dir)

                # シンボロジごとのSHPとjsonを出力
                vector_layer.generate_symbols()

                if vector_layer.layer.labelsEnabled():
                    vector_layer.generate_label_json(all_labels, layer.name())

            elif isinstance(layer, QgsRasterLayer):
                rasterlayer = RasterLayer(layer, extent, output_dir)
                rasterlayer.raster_to_png()
                rasterlayer.write_json()
                output_layer_names.append(layer.name())

        self.write_project_json(output_layer_names)
        QMessageBox.information(
            None,
            "完了",
            f"処理が完了しました。\
            \n\n出力先:\n{output_dir}",
        )

    def write_project_json(self, output_layer_names: list):
        """project.jsonにレイヤ情報を書き出す"""

        project_json = {
            "project_name": os.path.basename(QgsProject.instance().fileName()),
            "crs": QgsProject.instance().crs().authid(),
            "crs_type": (
                "geographic"
                if QgsProject.instance().crs().isGeographic()
                else "projected"
            ),
            "extent": [
                self.ui.mExtentGroupBox.outputExtent().xMinimum(),
                self.ui.mExtentGroupBox.outputExtent().yMinimum(),
                self.ui.mExtentGroupBox.outputExtent().xMaximum(),
                self.ui.mExtentGroupBox.outputExtent().yMaximum(),
            ],
            "scale": iface.mapCanvas().scale(),
            "layers": output_layer_names,
        }
        # project.jsonを出力
        with open(
            os.path.join(self.ui.outputFileWidget.filePath(), "project.json"), mode="w"
        ) as f:
            json.dump(project_json, f, ensure_ascii=False)

    def get_checked_layers(self):
        layers = []
        for i in range(self.layerListWidget.count()):
            if self.layerListWidget.item(i).checkState() == Qt.Checked:
                layers.append(self.layerListWidget.item(i).data(Qt.UserRole))
        return layers
