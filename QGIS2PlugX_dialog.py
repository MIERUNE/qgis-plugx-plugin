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

        self.add_layer_list()

        self.layers = None
        self.extent = None

    def add_layer_list(self):
        self.layerListWidget.clear()
        alllayers = [
            lyr
            for lyr in QgsProject.instance().mapLayers().values()
            # if l.dataProvider().name() == "gdal"
        ]
        items = reversed([i.name() for i in alllayers])
        for item in items:
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
        project_json["layers"] = []

        # ラベルSHPを出力する
        canvas = iface.mapCanvas()
        all_labels = processing.run("native:extractlabels",
                                    {'EXTENT': canvas.extent(),
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
            if maplyr.renderer_type == 'categorizedSymbol':
                maplyr.generate_category_symbols()
            if maplyr.renderer_type == 'singleSymbol':
                maplyr.generate_single_symbols()

            # レイヤごとのラベルSHPを出力
            if maplyr.layer.labelsEnabled():
                processing.run("native:extractbyattribute", {
                    'INPUT': all_labels,
                    'FIELD': 'Layer',
                    'OPERATOR': 0,  # '='
                    'VALUE': maplyr.layer.name(),
                    'OUTPUT': os.path.join(directory, f"{maplyr.layer.name()}_label.shp")})



        write_json(project_json, os.path.join(directory, 'project.json'))

        print("done")

    def get_checked_layers(self):
        layers = []
        for i in range(self.layerListWidget.count()):
            if self.layerListWidget.item(i).checkState() == Qt.Checked:
                layers.append(QgsProject.instance().mapLayersByName(self.layerListWidget.item(i).text())[0])
        return layers
