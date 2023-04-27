import os
import processing
from utils import write_json

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from qgis.gui import *
from qgis.PyQt import uic
from qgis.utils import iface

from maplayer import MapLayer


class QGIS2PlugX_dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi(
            os.path.join(os.path.dirname(__file__), "QGIS2PlugX_dialog.ui"), self
        )

        self.ui.pushButton_run.clicked.connect(self.run)
        self.ui.pushButton_cancel.clicked.connect(self.close)
        self.ui.mExtentGroupBox.setCurrentExtent(iface.mapCanvas().extent(), QgsProject.instance().crs())
        self.ui.mExtentGroupBox.setMapCanvas(iface.mapCanvas())
        self.ui.mExtentGroupBox.setOutputCrs(QgsProject.instance().crs())

        self.ui.setUnitToPtButton.clicked.connect(self.set_unit_to_pt)

        self.load_layer_list()

        self.layers = None
        self.extent = None

    def load_layer_list(self):
        vector_names = [l.layer().name() for l in QgsProject.instance().layerTreeRoot().children() if
                        isinstance(l.layer(), QgsVectorLayer)]

        for item in vector_names:
            i = QListWidgetItem(item)
            i.setFlags(i.flags() | Qt.ItemIsUserCheckable)
            i.setCheckState(Qt.Unchecked)
            self.layerListWidget.addItem(i)

    def run(self):
        # チェックしたレイヤをリストに取得する
        self.layers = self.get_checked_layers()
        if not self.layers:
            return
        # 処理範囲を取得する
        self.extent = self.ui.mExtentGroupBox.outputExtent()
        if not self.extent:
            return

        # 出力先のディレクトリを作成する
        directory = self.ui.outputFileWidget.filePath()

        # project.jsonにレイヤ順序情報を書き出し
        project_json = {}

        project_json["project_name"] = os.path.basename(QgsProject.instance().fileName()).split(".")[0]
        project_json["crs"] = QgsProject.instance().crs().authid()
        project_json["extent"] = [self.extent.xMinimum(), self.extent.yMinimum(), self.extent.xMaximum(),
                                  self.extent.yMaximum()]
        project_json["scale"] = iface.mapCanvas().scale()
        project_json["layers"] = []

        # ラベルSHPを出力する
        canvas = iface.mapCanvas()
        all_labels = processing.run("native:extractlabels",
                                    {'EXTENT': self.extent,
                                     'SCALE': canvas.scale(),
                                     'MAP_THEME': None,
                                     'INCLUDE_UNPLACED': True,
                                     'DPI': 96,
                                     'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']

        for lyr in self.layers:
            # 指定範囲内の地物を抽出し、元のスタイルを適用する
            qml_path = os.path.join(directory, 'layer.qml')
            lyr.saveNamedStyle(qml_path, categories=QgsMapLayer.Symbology | QgsMapLayer.Labeling)

            lyr_intersected = processing.run("native:extractbyextent",
                                             {'INPUT': lyr,
                                              'EXTENT': self.extent,
                                              'CLIP': True,
                                              'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
            lyr_intersected.loadNamedStyle(qml_path)
            if os.path.exists(qml_path):
                os.remove(qml_path)

            # レイヤ名をlayer_indexに変更する
            lyr_intersected.setName(f"layer_{self.layers.index(lyr)}")
            project_json["layers"].append(lyr_intersected.name())

            # スタイル出力用のMapLayerインスランスを作成する
            maplyr = MapLayer(lyr_intersected, directory)

            # シンボロジごとのSHPとjsonを出力
            maplyr.generate_symbols()

            if maplyr.layer.labelsEnabled():
                # レイヤlabelのjsonを出力
                maplyr.generate_label_json(all_labels, lyr.name())

        # project.jsonを出力
        write_json(project_json, os.path.join(directory, 'project.json'))

        QMessageBox.information(None, '完了', f"処理が完了しました。\n\n出力先:\n{directory}")

    def get_checked_layers(self):
        layers = []
        for i in range(self.layerListWidget.count()):
            if self.layerListWidget.item(i).checkState() == Qt.Checked:
                layers.append(QgsProject.instance().mapLayersByName(self.layerListWidget.item(i).text())[0])
        return layers

    def set_unit_to_pt(self):
        # シンボロジ
        for layer in self.get_checked_layers():
            renderer_type = layer.renderer().type()
            if renderer_type == "singleSymbol":
                symbol = layer.renderer().symbol()
                symbol_type = symbol.symbolLayer(0).type()

                # point
                if symbol_type == 0:
                    symbol.setSizeUnit(4)
                    symbol.symbolLayer(0).setStrokeWidthUnit(4)

                # line
                if symbol_type == 1:
                    symbol.symbolLayer(0).setWidthUnit(4)

                # polygon
                if symbol_type == 2:
                    symbol.symbolLayer(0).setStrokeWidthUnit(4)

            # if renderer_type == "categorizedSymbol":
            #     symbol_items = layer.renderer().legendSymbolItems()
            #     symbol_type = symbol_items[0].symbol().symbolLayer(0).type()
            #     for category in layer.renderer().categories():
            #         symbol = category.symbol()
            #
            #         # point
            #         if symbol_type == 0:
            #             symbol.setSizeUnit(4)
            #             symbol.symbolLayer(0).setStrokeWidthUnit(4)
            #
            #         # line
            #         if symbol_type == 1:
            #             symbol.symbolLayer(0).setWidthUnit(4)
            #
            #         # polygon
            #         if symbol_type == 2:
            #             symbol.symbolLayer(0).setStrokeWidthUnit(4)

            layer.triggerRepaint()
        # ラベル
