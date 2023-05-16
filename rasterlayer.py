from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from qgis.gui import *
from qgis.PyQt import uic
from qgis.utils import iface

import os
import processing
from utils import write_json


class RasterLayer:
    def __init__(self, layer: QgsRasterLayer, extent, dpi, image_width, image_height):
        self.layer = layer
        self.extent = extent
        self.dpi = dpi
        self.image_width = image_width
        self.image_height = image_height
        # self.directory = directory

    def xyz_to_png(self, layer, output_path):
        # Create empty image
        image = QImage(
            self.image_width, self.image_height, QImage.Format_ARGB32_Premultiplied
        )
        image.setDotsPerMeterX(self.dpi / 0.0254)
        image.setDotsPerMeterY(self.dpi / 0.0254)
        image.fill(0)

        # Map extent and size settings
        map_settings = QgsMapSettings()
        map_settings.setExtent(self.extent)
        map_settings.setOutputSize(QSize(self.image_width, self.image_height))
        map_settings.setOutputDpi(self.dpi)

        # Create image
        map_settings.setLayers([layer])
        render = QgsMapRendererParallelJob(map_settings)
        render.start()
        render.waitForFinished()
        image = render.renderedImage()
        format = QByteArray(b"PNG")
        image.save(output_path, format, 100)
