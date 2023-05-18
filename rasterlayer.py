import json
import os

import processing
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsProject,
    QgsRasterFileWriter,
    QgsRasterLayer,
    QgsRasterPipe,
    QgsRectangle,
)
from qgis.utils import iface


class RasterLayer:
    def __init__(
        self,
        layer: QgsRasterLayer,
        extent: QgsRectangle,
        output_dir: str,
    ):
        self.layer = layer
        self.extent = extent
        """ user defined extent to clip, in project crs """
        self.output_dir = output_dir

    def xyz_to_png(self):
        clipped_tiff_path = os.path.join(
            self.output_dir, self.layer.name() + "_clipped.tif"
        )

        # Convert Bbox to EPSG:3857
        transform = QgsCoordinateTransform(
            QgsProject.instance().crs(),
            QgsCoordinateReferenceSystem("EPSG:3857"),
            QgsProject.instance(),
        )
        extent_3857 = transform.transformBoundingBox(self.extent)
        extent_to_clip = QgsRectangle(
            extent_3857.xMinimum(),
            extent_3857.yMinimum(),
            extent_3857.xMaximum(),
            extent_3857.yMaximum(),
        )

        # Calculate extent in EPSG:3857
        extent_width = extent_to_clip.xMaximum() - extent_to_clip.xMinimum()
        extent_height = extent_to_clip.yMaximum() - extent_to_clip.yMinimum()

        dpi = iface.mapCanvas().mapSettings().outputDpi()
        scale = iface.mapCanvas().scale()
        inch_to_meter = 0.0254
        image_width = int(extent_width / scale * dpi / inch_to_meter)
        image_height = int(extent_height / scale * dpi / inch_to_meter)

        # Save TIFF file in EPSG:3857
        file_writer = QgsRasterFileWriter(clipped_tiff_path)
        pipe = QgsRasterPipe()
        pipe.set(self.layer.dataProvider().clone())
        file_writer.writeRaster(
            pipe,
            image_width,
            image_height,
            extent_to_clip,
            QgsCoordinateReferenceSystem("EPSG:3857"),
        )

        # Convert to Project CRS
        warped = processing.run(
            "gdal:warpreproject",
            {
                "INPUT": clipped_tiff_path,
                "SOURCE_CRS": QgsCoordinateReferenceSystem("EPSG:3857"),
                "TARGET_CRS": QgsProject.instance().crs(),
                "OUTPUT": "TEMPORARY_OUTPUT",
            },
        )["OUTPUT"]

        # Create clip PNG file in Project CRS
        self.clip_raster_to_png(warped)

        # clean up
        os.remove(clipped_tiff_path)
        os.remove(clipped_tiff_path + ".aux.xml")

    def clip_raster_to_png(self, input_raster):
        # Create clip PNG file in Project CRS
        output_png_path = os.path.join(self.output_dir, self.layer.name() + ".png")

        clip_extent = f"{self.extent.xMinimum()}, \
                        {self.extent.xMaximum()}, \
                        {self.extent.yMinimum()}, \
                        {self.extent.yMaximum()}  \
                        [{QgsProject.instance().crs().authid()}]"

        processing.run(
            "gdal:cliprasterbyextent",
            {
                "INPUT": input_raster,
                "PROJWIN": clip_extent,
                "OVERCRS": False,
                "NODATA": None,
                "OPTIONS": "",
                "DATA_TYPE": 0,
                "EXTRA": "",
                "OUTPUT": output_png_path,
            },
        )

    def write_json(self):
        raster_info = {
            "type": "raster",
            "crs": self.layer.crs().authid(),
            "extent": [
                self.extent.xMinimum(),
                self.extent.yMinimum(),
                self.extent.xMaximum(),
                self.extent.yMaximum(),
            ],
        }
        with open(
            os.path.join(self.output_dir, f"{self.layer.name()}.json"), mode="w"
        ) as f:
            json.dump(raster_info, f)
