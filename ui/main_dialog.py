import os
import shutil

import sip
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QMessageBox, QTreeWidgetItem
from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsMapLayerModel,
    QgsProject,
    QgsLayerTree,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsApplication,
    QgsMapLayerType,
    QgsMessageLog,
    Qgis,
)
from qgis.PyQt import uic
from qgis.utils import iface

from translator.vector.label import generate_label_vector
from ui.progress_dialog import ProgressDialog
from translator.thread import ProcessingThread
from utils import write_json, get_tempdir


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

        # generate label vector includes labels of all layers
        all_labels = generate_label_vector(params["extent"])

        # orchestrate thread and progress dialog
        thread = ProcessingThread(layers, all_labels, params)
        progress_dialog = ProgressDialog(thread.set_abort_flag)
        progress_dialog.set_maximum(len(layers))
        # connect signals
        thread.addProgress.connect(progress_dialog.add_progress)
        thread.postMessage.connect(progress_dialog.set_messsage)
        thread.setAbortable.connect(progress_dialog.set_abortable)
        thread.processFinished.connect(progress_dialog.close)
        thread.processFailed.connect(
            lambda error_message: [
                QgsMessageLog.logMessage(error_message, "QGS2PlugX", Qgis.Critical),
                QMessageBox.information(
                    self, "エラー", f"エラーが発生しました。\n\n{error_message}"
                ),  # noqa
                progress_dialog.close(),
            ]
        )
        # start sub thread
        thread.start()
        progress_dialog.exec_()

        results = thread.results  # results stored in thread instance

        # list-up layers has unsupported symbol
        layers_has_unsupported_symbol = list(
            map(
                lambda r: r["layer_name"],
                list(
                    filter(lambda r: r.get("has_unsupported_symbol") is True, results)
                ),
            )
        )

        # list-up layers NOT completed
        layers_not_completed = list(
            map(
                lambda r: r["layer_name"],
                list(filter(lambda r: r["completed"] is False, results)),
            )
        )

        # list-up layers processed successfully: layer_0, layer_2, layer_5, ...
        layers_processed_successfully = list(
            map(
                lambda r: f"layer_{r['idx']}",
                list(filter(lambda r: r["completed"] is True, results)),
            )
        )

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
            "layers": layers_processed_successfully,  # layer_0,2,5..
            "assets_path": "assets",
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
        if len(layers_not_completed) > 0:
            msg += "\n\n以下レイヤに対応不可。\n" + "\n".join(layers_not_completed)
        QMessageBox.information(
            None,
            "完了",
            msg,
        )

        # remove temp dir including intermediate files
        try:
            shutil.rmtree(get_tempdir(params["output_dir"]))
        # if dir is locked by process
        except PermissionError:
            QMessageBox.warning(
                self,
                "エラー",
                "一時フォルダの削除に失敗しました。\n手動で削除してください。",
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
