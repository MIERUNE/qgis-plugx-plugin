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
    def __init__(self, layer: QgsRasterLayer, extent, dpi, directory):
        self.layer = layer
        self.extent = extent
        self.dpi = dpi
        # self.image_width = image_width
        # self.image_height = image_height
        self.directory = directory

    def xyz_to_png(self):
        output_path = os.path.join(self.directory, self.layer.name() + ".png")

        # Check CRS type
        crs = QgsProject.instance().crs()

        transform = QgsCoordinateTransform(
            crs, QgsCoordinateReferenceSystem("EPSG:3857"), QgsProject.instance()
        )
        map_extent = transform.transformBoundingBox(self.extent)

        # Calculate image size
        extent_width = map_extent.xMaximum() - map_extent.xMinimum()
        extent_height = map_extent.yMaximum() - map_extent.yMinimum()
        image_width = int(extent_width / self.dpi / 0.0254)
        image_height = int(extent_height / self.dpi / 0.0254)
        QMessageBox.information(
            None, "Info", str(image_height) + " " + str(image_width)
        )
        # Create empty image
        image = QImage(image_width, image_height, QImage.Format_ARGB32_Premultiplied)
        image.setDotsPerMeterX(self.dpi / 0.0254)
        image.setDotsPerMeterY(self.dpi / 0.0254)
        image.fill(0)

        # Map extent and size settings
        map_settings = QgsMapSettings()
        map_settings.setExtent(map_extent)
        map_settings.setOutputSize(QSize(image_width, image_height))
        map_settings.setOutputDpi(self.dpi)

        # Create image
        map_settings.setLayers([self.layer])
        render = QgsMapRendererParallelJob(map_settings)
        render.start()
        render.waitForFinished()
        image = render.renderedImage()
        format = QByteArray(b"PNG")
        image.save(output_path, format, 100)

    def generate_raster_info(self):
        raster_info = {
            "type": "raster",
            "extent": [
                self.extent.xMinimum(),
                self.extent.yMinimum(),
                self.extent.xMaximum(),
                self.extent.yMaximum(),
            ],
        }
        write_json(
            raster_info, os.path.join(self.directory, f"{self.layer.name()}.json")
        )
