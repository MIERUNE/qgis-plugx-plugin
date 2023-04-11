import os
import json
import processing

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
        self.add_layer_list()

    def add_layer_list(self):
        self.layerListWidget.clear()
        alllayers = [
            lyr
            for lyr in QgsProject.instance().mapLayers().values()
            # if l.dataProvider().name() == "gdal"
        ]
        items = [f"{i.name()} [{i.crs().authid()}]" for i in alllayers]
        for s in items:
            i = QListWidgetItem(s)
            i.setFlags(i.flags() | Qt.ItemIsUserCheckable)
            i.setCheckState(Qt.Unchecked)
            self.layerListWidget.addItem(i)

    def run(self):
        layers = [
            lyr
            for lyr in QgsProject.instance().mapLayers().values()
        ]

        # プロジェクトファイルのパスとファイル名を取得
        prj_dir = QgsProject.instance().readPath('.')
        prj_name = os.path.basename(QgsProject.instance().fileName()).split('.')[0]

        # 出力先のディレクトリを作成
        directory = os.path.join(prj_dir, prj_name)
        if not os.path.exists(directory):
            os.makedirs(directory)
            # project.jsonを出力
            project = {
                "name": prj_name,
                "layers": []
            }
            with open(os.path.join(directory, 'project.json'), 'w') as f:
                json.dump(project, f)

            # ラベルSHPを出力する
            canvas = iface.mapCanvas()

            all_labels = processing.run("native:extractlabels",
                                        {'EXTENT': canvas.extent(),
                                         'SCALE': canvas.scale(),
                                         'MAP_THEME': None,
                                         'INCLUDE_UNPLACED': True,
                                         'DPI': 96,
                                         'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']

            for lyr in layers:
                maplyr = MapLayer(lyr, directory)

                # シンボロジごとのSHPとjsonを出力
                if maplyr.renderer_type == 'categorizedSymbol':
                    maplyr.generate_category_symbols()
                if maplyr.renderer_type == 'singleSymbol':
                    maplyr.generate_single_symbols()

                # レイヤ後ののラベルSHPを出力
                processing.run("native:extractbyattribute", {
                    'INPUT': all_labels,
                    'FIELD': 'Layer',
                    'OPERATOR': 0,  # '='
                    'VALUE': maplyr.layer.name(),
                    'OUTPUT': os.path.join(directory, f"{maplyr.layer.name()}_label.shp")})

            print("done")



        else:
            print(f"Directory {directory} already exists!")
