import os

import processing
import sip
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QMessageBox, QTreeWidgetItem
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
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

from translator.raster.process import process_raster
from translator.vector.process import process_vector
from translator.vector.label import generate_label_json
from utils import write_json


class MainDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(
            os.path.join(os.path.dirname(__file__), "main_dialog.ui"), self
        )

        self.init_ui()

    def init_ui(self):
        # connect signals
        self.ui.pushButton_run.clicked.connect(self._run)
        self.ui.pushButton_cancel.clicked.connect(self.close)

        # QgsExtentGroupBox
        self.ui.mExtentGroupBox.setMapCanvas(iface.mapCanvas())
        self.ui.mExtentGroupBox.setOutputCrs(QgsProject.instance().crs())
        self.ui.mExtentGroupBox.setOutputExtentFromCurrent()
        QgsProject.instance().crsChanged.connect(
            lambda: [
                self.ui.mExtentGroupBox.setOutputCrs(QgsProject.instance().crs()),
                self.ui.mExtentGroupBox.setOutputExtentFromCurrent(),
            ]
        )

        # close dialog when project cleared to avoid crash: Issue #55
        QgsProject.instance().cleared.connect(self.close)

        # レイヤーが追加されるなど、レイヤー一覧が変更されたときに更新する
        QgsProject.instance().layerTreeRoot().layerOrderChanged.connect(
            self.process_node
        )

    def _get_excution_params(self):
        params = {
            "extent": self.ui.mExtentGroupBox.outputExtent(),
            "output_dir": self.ui.outputFileWidget.filePath(),
        }

        return params

    def _run(self):
        layers = self._get_checked_layers()
        params = self._get_excution_params()

        # export label shp, includes all layers
        all_labels = processing.run(
            "native:extractlabels",
            {
                "EXTENT": params["extent"],
                "SCALE": iface.mapCanvas().scale(),
                "MAP_THEME": None,
                "INCLUDE_UNPLACED": True,
                "DPI": iface.mapCanvas().mapSettings().outputDpi(),
                "OUTPUT": "TEMPORARY_OUTPUT",
            },
        )["OUTPUT"]

        # process layers
        layers_has_unsupported_symbol = []  # if layer with unsupported symbol, memo it
        for idx, layer in enumerate(layers):
            if isinstance(layer, QgsRasterLayer):
                process_raster(layer, params["extent"], idx, params["output_dir"])
            elif isinstance(layer, QgsVectorLayer):
                result = process_vector(
                    layer, params["extent"], idx, params["output_dir"]
                )

                if layer.labelsEnabled():
                    generate_label_json(
                        all_labels, layer.name(), idx, params["output_dir"]
                    )

                if result["has_unsupported_symbol"]:
                    layers_has_unsupported_symbol.append(layer.name())

        # write project.json
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
            "layers": [f"layer_{idx}" for idx in range(len(layers))],  # layer_0,1,2..
        }
        write_json(
            project_json,
            os.path.join(self.ui.outputFileWidget.filePath(), "project.json"),
        )

        # messaging
        msg = f"処理が完了しました。\n\n出力先:\n{params['output_dir']}"
        if len(layers_has_unsupported_symbol) > 0:
            msg += (
                "\n\n以下レイヤに対応不可なシンボロジがあるため、\n\
            シンプルシンボルに変換しました。\n"
                + "\n".join(layers_has_unsupported_symbol)
            )
        QMessageBox.information(
            None,
            "完了",
            msg,
        )

    def _get_checked_layers(self):
        layers = []
        # QTreeWidgetの子要素を再帰的に取得する
        for i in range(self.layerTree.topLevelItemCount()):
            item = self.layerTree.topLevelItem(i)
            layers.extend(self._get_checked_layers_recursive(item))
        return layers

    def _get_checked_layers_recursive(self, item):
        layers = []
        if item.checkState(0) == Qt.CheckState.Checked:
            layer = QgsProject.instance().mapLayer(item.text(1))
            if layer:
                layers.append(layer)
        for i in range(item.childCount()):
            child_item = item.child(i)
            layers.extend(self._get_checked_layers_recursive(child_item))
        return layers

    def process_node(self):
        """
        QGISのレイヤーツリーを読み込み
        """
        if not self.isVisible():
            # don't process_node when dialog invisible to avoid crash: Issue #55
            return

        self.layerTree.clear()
        self._process_node_recursive(QgsProject.instance().layerTreeRoot(), None)

    def _process_node_recursive(self, node, parent_node):
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
            # check signal is connected or not
            try:
                child.nameChanged.disconnect(self.process_node)
            except TypeError:
                # when signal is not connected
                pass
            child.nameChanged.connect(self.process_node)

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
                self._process_node_recursive(child, item)
