import os
import shutil

import sip
import webbrowser

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QMessageBox, QTreeWidgetItem, QFileDialog
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
from plugx_utils import write_json, get_tempdir
from scale import get_scale_from_canvas, set_map_extent_from


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
        self.ui.pushButton_help.clicked.connect(self._on_help_button_clicked)

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

        # perform update_ui_scale when it's true
        # become false when UI scale widget is edited by user
        self.enable_update_ui_scale = True

        # set canvas scale when user input scale in ui
        self.ui.scale_widget.scaleChanged.connect(self._zoom_canvas_from_scale)
        # calculate export scale and show to ui
        self._update_ui_scale()
        # update export scale shown in ui when change map extent
        iface.mapCanvas().extentsChanged.connect(self._update_ui_scale)

        # close dialog when project cleared to avoid crash: Issue #55
        QgsProject.instance().cleared.connect(self.close)

        # レイヤーが追加されるなど、レイヤー一覧が変更されたときに更新する
        QgsProject.instance().layerTreeRoot().layerOrderChanged.connect(
            self.process_node
        )

    def _run(self):
        layers = self._get_checked_layers()

        output_dir = QFileDialog.getExistingDirectory(self, "Select Folder")
        if output_dir == "":
            return

        params = {
            "extent": self.ui.mExtentGroupBox.outputExtent(),
            "output_dir": output_dir,
        }

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
                    self,
                    self.tr("Error"),
                    self.tr("An error occured.") + f"\n\n{error_message}",
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

        # list-up layers NOT completed and its reason
        layers_not_completed = list(
            map(
                lambda r: f"{r['layer_name']} : {r['reason']}",
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
            "scale": get_scale_from_canvas(),
            "layers": layers_processed_successfully,  # layer_0,2,5..
            "assets_path": "assets",
        }
        write_json(
            project_json,
            os.path.join(params["output_dir"], "project.json"),
        )

        # messaging
        msg = self.tr("Process completed")
        msg += "\n\n"
        msg += self.tr("Output folder")
        msg += f":\n{params['output_dir']}"

        if len(layers_has_unsupported_symbol) > 0:
            msg += "\n\n"
            msg += self.tr("The following layers contains unsupported symbols")
            msg += self.tr("and have been converted to simple symbols.")
            msg += "\n\n".join(layers_has_unsupported_symbol)

        if len(layers_not_completed) > 0:
            msg += "\n\n"
            msg += self.tr("Failed to export the following layers.")
            msg += "\n\n".join(layers_not_completed)
        QMessageBox.information(
            None,
            self.tr("Completed"),
            msg,
        )

        # remove temp dir including intermediate files
        try:
            shutil.rmtree(get_tempdir(params["output_dir"]))
        # if dir is locked by process
        except PermissionError:
            QMessageBox.warning(
                self,
                self.tr("Error"),
                self.tr(
                    "Failed to delete the temporary folder. Please delete it manually."
                ),
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
                if not child.layer().isSpatial():
                    # exclude no geometry layers such as CSV files
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

    def _update_ui_scale(self):
        # do not update when enable_update_ui_scale is False
        # in case of canvas is calculated from scale widget
        if not self.enable_update_ui_scale:
            return

        # disable auto ui scale update
        try:
            self.ui.scale_widget.scaleChanged.disconnect()
        except TypeError:
            # when signal is not connected
            pass

        # update ui scale
        self.ui.scale_widget.setScale(get_scale_from_canvas())
        # reactivate auto ui scale update
        self.ui.scale_widget.scaleChanged.connect(self._zoom_canvas_from_scale)

    def _zoom_canvas_from_scale(self):
        # disable temporary scale auto-calculation when extent changed
        self.enable_update_ui_scale = False

        # update canvas
        set_map_extent_from(
            scale=self.ui.scale_widget.scale(), crs=QgsProject.instance().crs().authid()
        )

        # reactive scale auto-calculation when extent changed
        self.enable_update_ui_scale = True

    def _on_help_button_clicked(self):
        # show readme page
        webbrowser.open("https://github.com/MIERUNE/qgis-plugx-plugin")
        return
