import json
import os

import processing
import sip
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QMessageBox, QTreeWidgetItem
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsMapLayer,
    QgsMapLayerModel,
    QgsProject,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsLayerTree,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsApplication,
    QgsMapLayerType,
)
from qgis.PyQt import uic
from qgis.utils import iface

from rasterlayer import RasterLayer
from vectorlayer import VectorLayer


class MainDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(
            os.path.join(os.path.dirname(__file__), "main_dialog.ui"), self
        )

        self.init_ui()

    def init_ui(self):
        # connect signals
        self.ui.pushButton_run.clicked.connect(self.run)
        self.ui.pushButton_cancel.clicked.connect(self.close)

        # QgsExtentGroupBox
        self.ui.mExtentGroupBox.setMapCanvas(iface.mapCanvas())
        self.ui.mExtentGroupBox.setOutputCrs(QgsProject.instance().crs())
        self.ui.mExtentGroupBox.setOutputExtentFromCurrent()

        # レイヤーが追加されるなど、レイヤー一覧が変更されたときに更新する
        QgsProject.instance().layerTreeRoot().layerOrderChanged.connect(
            self.process_node
        )
        QgsProject.instance().layerRemoved.connect(self.process_node)
        QgsProject.instance().layersAdded.connect(self.process_node)
        self.process_node()  # 初回読み込み

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
                "DPI": iface.mapCanvas().mapSettings().outputDpi(),
                "OUTPUT": "TEMPORARY_OUTPUT",
            },
        )["OUTPUT"]

        output_layer_names = []
        svgs = []
        rasters = []

        symbol_error_layers: list = []

        for layer in layers:
            if isinstance(layer, QgsVectorLayer):
                # 指定範囲内の地物を抽出し、元のスタイルを適用する
                qml_path = os.path.join(output_dir, "layer.qml")
                layer.saveNamedStyle(
                    qml_path, categories=QgsMapLayer.Symbology | QgsMapLayer.Labeling
                )

                reprojected = processing.run(
                    "native:reprojectlayer",
                    {
                        "INPUT": layer,
                        "TARGET_CRS": QgsProject.instance().crs(),
                        "OUTPUT": "TEMPORARY_OUTPUT",
                    },
                )["OUTPUT"]

                clip_extent = f"{extent.xMinimum()}, \
                        {extent.xMaximum()}, \
                        {extent.yMinimum()}, \
                        {extent.yMaximum()}  \
                        [{QgsProject.instance().crs().authid()}]"

                layer_intersected = processing.run(
                    "native:extractbyextent",
                    {
                        "INPUT": reprojected,
                        "EXTENT": clip_extent,
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
                vector_layer = VectorLayer(layer_intersected, output_dir, layer.name())

                # シンボロジごとのSHPとjsonを出力
                vector_layer.update_svgs_rasters_list(rasters, svgs)
                vector_layer.generate_symbols()
                svgs = vector_layer.svgs
                rasters = vector_layer.rasters

                if vector_layer.layer.labelsEnabled():
                    vector_layer.generate_label_json(all_labels, layer.name())
                if vector_layer.unsupported_symbols:
                    symbol_error_layers.append(layer.name())

            elif isinstance(layer, QgsRasterLayer):
                output_layer_name = f"layer_{layers.index(layer)}"
                rasterlayer = RasterLayer(layer, output_layer_name, extent, output_dir)
                rasterlayer.raster_to_png()
                rasterlayer.write_json()
                output_layer_names.append(output_layer_name)

        self.write_project_json(output_layer_names)

        msg = f"処理が完了しました。\n\n出力先:\n{output_dir}"

        if symbol_error_layers:
            msg += (
                "\n\n以下レイヤに対応不可なシンボロジがあるため、\n\
            シンプルシンボルに変換しました。\n"
                + "\n".join(symbol_error_layers)
            )

        QMessageBox.information(
            None,
            "完了",
            msg,
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
        # QTreeWidgetの子要素を再帰的に取得する
        for i in range(self.layerTree.topLevelItemCount()):
            item = self.layerTree.topLevelItem(i)
            layers.extend(self.get_checked_layers_recursive(item))
        return layers

    def get_checked_layers_recursive(self, item):
        layers = []
        if item.checkState(0) == Qt.CheckState.Checked:
            layer = QgsProject.instance().mapLayer(item.text(1))
            if layer:
                layers.append(layer)
        for i in range(item.childCount()):
            child_item = item.child(i)
            layers.extend(self.get_checked_layers_recursive(child_item))
        return layers

    def process_node(self):
        """
        QGISのレイヤーツリーを読み込み
        """
        self.layerTree.clear()
        self.process_node_recursive(QgsProject.instance().layerTreeRoot(), None)

    def process_node_recursive(self, node, parent_node):
        """
        QGISのレイヤーツリーを再帰的に読み込み

        Args:
            node (_type_): _description_
            parent_node (_type_): _description_
            parent_tree (_type_): _description_

        Raises:
            Exception: _description_
        """
        for child in node.children():
            if QgsLayerTree.isGroup(child):
                if not isinstance(child, QgsLayerTreeGroup):
                    # Sip cast issue , Lizmap plugin #299
                    child = sip.cast(child, QgsLayerTreeGroup)
                child_type = "group"
                child_icon = QIcon(QgsApplication.iconPath("mActionFolder.svg"))
                child_id = ""

            elif QgsLayerTree.isLayer(child):
                if not isinstance(child, QgsLayerTreeLayer):
                    # Sip cast issue , Lizmap plugin #299
                    child = sip.cast(child, QgsLayerTreeLayer)
                child_type = "layer"
                child_icon = QgsMapLayerModel.iconForLayer(child.layer())
                child_id = child.layer().id()

                if not (
                    child.layer().type() == QgsMapLayerType.VectorLayer
                    or child.layer().type() == QgsMapLayerType.RasterLayer
                ):
                    # Unsupported QgsMapLayerType
                    continue

            else:
                raise Exception("Unknown child type")

            item = QTreeWidgetItem([child.name(), child_id])
            item.setIcon(0, child_icon)
            item.setFlags(
                item.flags()
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsAutoTristate
            )
            item.setCheckState(
                0,
                Qt.CheckState.Checked if child.isVisible() else Qt.CheckState.Unchecked,
            )

            # Move group or layer to its parent node
            if not parent_node:
                self.layerTree.addTopLevelItem(item)
            else:
                parent_node.addChild(item)

            if child_type == "group":
                self.process_node_recursive(child, item)
