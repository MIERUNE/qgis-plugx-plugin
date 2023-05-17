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
    def __init__(self, layer: QgsRasterLayer, extent, directory, project_crs):
        self.layer = layer
        self.extent = extent
        self.dpi = iface.mapCanvas().mapSettings().outputDpi()
        self.scale = iface.mapCanvas().scale()
        self.directory = directory
        self.project_crs = project_crs

    def xyz_to_png(self):
        output_tiff_path = os.path.join(self.directory, self.layer.name() + ".tiff")
        output_png_path = os.path.join(self.directory, self.layer.name() + ".png")

        # Convert Bbox to EPSG:3857
        new_crs = QgsCoordinateReferenceSystem("EPSG:3857")

        transform = QgsCoordinateTransform(
            self.project_crs, new_crs, QgsProject.instance()
        )
        map_extent = transform.transformBoundingBox(self.extent)

        # QMessageBox.information(None, "Info", str(self.dpi))

        # Calculate image size in EPSG:3857
        extent_width = map_extent.xMaximum() - map_extent.xMinimum()
        extent_height = map_extent.yMaximum() - map_extent.yMinimum()
        # QMessageBox.information(
        #     None, "Info", str(extent_height) + " " + str(extent_width)
        # )

        image_width = int(extent_width / self.scale * self.dpi / 0.0254)
        image_height = int(extent_height / self.scale * self.dpi / 0.0254)

        # QMessageBox.information(
        #     None, "Info", str(image_height) + " " + str(image_width)
        # )

        # Save TIFF file in EPSG:3857
        file_writer = QgsRasterFileWriter(output_tiff_path)
        pipe = QgsRasterPipe()
        pipe.set(self.layer.dataProvider().clone())
        file_writer.writeRaster(pipe, image_width, image_height, map_extent, new_crs)

        # Create clip PNG file in Project CRS
        clip_extent = f"{self.extent.xMinimum()}, {self.extent.xMaximum()}, {self.extent.yMinimum()}, {self.extent.yMaximum()}  [{self.project_crs.authid()}]"
        # QMessageBox.information(None, "Info", str(clip_extent))
        processing.run(
            "gdal:cliprasterbyextent",
            {
                "INPUT": output_tiff_path,
                "PROJWIN": clip_extent,
                "OVERCRS": False,
                "NODATA": None,
                "OPTIONS": "",
                "DATA_TYPE": 0,
                "EXTRA": "",
                "OUTPUT": output_png_path,
            },
        )
        os.remove(output_tiff_path)
        os.remove(output_tiff_path + ".aux.xml")

    def generate_raster_info(self):
        raster_info = {
            "type": "raster",
            "crs": self.project_crs.authid(),
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
