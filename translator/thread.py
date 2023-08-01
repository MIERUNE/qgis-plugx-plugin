from PyQt5.QtCore import QThread, pyqtSignal
from qgis.core import QgsRasterLayer, QgsVectorLayer

from translator.raster.process import process_raster
from translator.vector.process import process_vector
from translator.vector.label import generate_label_json


class ProcessingThread(QThread):
    processStarted = pyqtSignal(int)
    addProgress = pyqtSignal(int)
    postMessage = pyqtSignal(str)
    processFinished = pyqtSignal()
    setAbortable = pyqtSignal(bool)
    processFailed = pyqtSignal(str)

    def __init__(self, layers: list, all_labels: QgsVectorLayer, params: dict):
        super().__init__()

        self.layers = layers
        self.all_labels = all_labels
        self.params = params
        self.abort_flag = False

        self.results = []

    def set_abort_flag(self, flag=True):
        self.abort_flag = flag

    def run(self):
        try:
            for idx, layer in enumerate(self.layers):
                if self.abort_flag:
                    break

                if isinstance(layer, QgsRasterLayer):
                    result = process_raster(
                        layer, self.params["extent"], idx, self.params["output_dir"]
                    )
                    self.results.append(result)
                elif isinstance(layer, QgsVectorLayer):
                    result = process_vector(
                        layer, self.params["extent"], idx, self.params["output_dir"]
                    )

                    if layer.labelsEnabled():
                        generate_label_json(
                            self.all_labels,
                            layer.name(),
                            idx,
                            self.params["output_dir"],
                        )
                    self.results.append(result)

                # emit progress
                self.postMessage.emit(f"処理中: {layer.name()}")
                self.setAbortable.emit(True)
                self.addProgress.emit(1)
        except Exception as e:
            # エラーはまとめてキャッチして呼び出し元に報告・処理を中断
            self.processFailed.emit(f"layer:{layer.name()} - error:{str(e)}")
            return

        self.processFinished.emit()
