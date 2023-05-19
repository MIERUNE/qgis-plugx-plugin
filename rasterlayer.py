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
    QgsMapSettings,
    QgsMapRendererParallelJob,
)
from qgis.utils import iface
from PyQt5.QtCore import QSize
from qgis.PyQt.QtGui import QImage, QColor


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

    def raster_to_png(self):
        if self.layer.providerType() == "wms":
            # WMS, WMTS or XYZ tile
            self.xyz_to_png()

        if self.layer.rasterType() == QgsRasterLayer.LayerType.Multiband:
            # RGB image
            self.rgb_file_to_png()

        elif (
            self.layer.rasterType() == QgsRasterLayer.LayerType.GrayOrUndefined
            and self.layer.bandCount() == 1
        ):
            # single band raster with 1 band
            self.singleband_file_to_png()

    def xyz_to_png(self):
        output_png_path = os.path.join(self.output_dir, self.layer.name() + ".png")
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
        clip_extent = f"{self.extent.xMinimum()}, \
                        {self.extent.xMaximum()}, \
                        {self.extent.yMinimum()}, \
                        {self.extent.yMaximum()}  \
                        [{QgsProject.instance().crs().authid()}]"

        processing.run(
            "gdal:cliprasterbyextent",
            {
                "INPUT": warped,
                "PROJWIN": clip_extent,
                "OVERCRS": False,
                "NODATA": None,
                "OPTIONS": "",
                "DATA_TYPE": 0,
                "EXTRA": "",
                "OUTPUT": output_png_path,
            },
        )

        # clean up
        os.remove(clipped_tiff_path)
        os.remove(clipped_tiff_path + ".aux.xml")

    def rgb_file_to_png(self):
        # Create clip PNG file in Project CRS
        output_png_path = os.path.join(self.output_dir, self.layer.name() + ".png")

        # Convert to Project CRS
        warped = processing.run(
            "gdal:warpreproject",
            {
                "INPUT": self.layer,
                "SOURCE_CRS": self.layer.crs(),
                "TARGET_CRS": QgsProject.instance().crs(),
                "OUTPUT": "TEMPORARY_OUTPUT",
            },
        )["OUTPUT"]

        clip_extent = f"{self.extent.xMinimum()}, \
                        {self.extent.xMaximum()}, \
                        {self.extent.yMinimum()}, \
                        {self.extent.yMaximum()}  \
                        [{QgsProject.instance().crs().authid()}]"

        processing.run(
            "gdal:cliprasterbyextent",
            {
                "INPUT": warped,
                "PROJWIN": clip_extent,
                "OVERCRS": False,
                "NODATA": None,
                "OPTIONS": "",
                "DATA_TYPE": 0,
                "EXTRA": "",
                "OUTPUT": output_png_path,
            },
        )

    def singleband_file_to_png(self):
        # Reproject input raster to 4326

        reprojeted = processing.run(
            "gdal:warpreproject",
            {
                "INPUT": self.layer,
                "SOURCE_CRS": self.layer.crs(),
                "TARGET_CRS": QgsCoordinateReferenceSystem("EPSG:4326"),
                "OUTPUT": "TEMPORARY_OUTPUT",
            },
        )["OUTPUT"]

        layer_geographic = QgsRasterLayer(reprojeted, "Raster Layer")
        # set style to layer geographic from input raster
        layer_geographic.setRenderer(self.layer.renderer())
        extent = layer_geographic.extent()

        # Create empty image

        image_width = layer_geographic.width()
        image_height = layer_geographic.height()
        dpi = iface.mapCanvas().mapSettings().outputDpi()

        image = QImage(image_width, image_height, QImage.Format_ARGB32_Premultiplied)

        inch_to_meter = 0.0254
        image.setDotsPerMeterX(dpi / inch_to_meter)
        image.setDotsPerMeterY(dpi / inch_to_meter)
        image.fill(0)

        # Set map to export image
        map_settings = QgsMapSettings()
        map_settings.setExtent(extent)
        map_settings.setOutputSize(QSize(image_width, image_height))
        map_settings.setOutputDpi(dpi)

        map_settings.setLayers([layer_geographic])
        map_settings.setBackgroundColor(QColor(0, 0, 0, 0))

        # Render the map with symbology
        render = QgsMapRendererParallelJob(map_settings)
        render.start()
        render.waitForFinished()

        # Get the rendered image
        image = render.renderedImage()
        output_symbolized_png_path = os.path.join(
            self.output_dir, self.layer.name() + "_symbolized.png"
        )
        image.save(output_symbolized_png_path, "png")

        # # Generate input raster world file
        pgw_file = output_symbolized_png_path.replace(".png", ".pgw")

        raster_canvas = os.path.join(self.output_dir, self.layer.name() + "_canvas.png")
        processing.run(
            "gdal:translate",
            {
                "INPUT": layer_geographic,
                "TARGET_CRS": None,
                "NODATA": None,
                "COPY_SUBDATASETS": False,
                "OPTIONS": "",
                "EXTRA": "-co worldfile=yes",
                "DATA_TYPE": 0,
                "OUTPUT": raster_canvas,
            },
        )

        wld_file = os.path.join(self.output_dir, self.layer.name() + "_canvas.wld")
        os.rename(wld_file, pgw_file)

        # Clip converted PNG file
        output_png_path = os.path.join(self.output_dir, self.layer.name() + ".png")

        # Convert to Project CRS
        warped = processing.run(
            "gdal:warpreproject",
            {
                "INPUT": output_symbolized_png_path,
                "SOURCE_CRS": layer_geographic.crs(),
                "TARGET_CRS": QgsProject.instance().crs(),
                "OUTPUT": "TEMPORARY_OUTPUT",
            },
        )["OUTPUT"]

        clip_extent = f"{self.extent.xMinimum()}, \
                        {self.extent.xMaximum()}, \
                        {self.extent.yMinimum()}, \
                        {self.extent.yMaximum()}  \
                        [{QgsProject.instance().crs().authid()}]"

        processing.run(
            "gdal:cliprasterbyextent",
            {
                "INPUT": warped,
                "PROJWIN": clip_extent,
                "OVERCRS": False,
                "NODATA": None,
                "OPTIONS": "",
                "DATA_TYPE": 0,
                "EXTRA": "",
                "OUTPUT": output_png_path,
            },
        )

        # clean up
        os.remove(output_symbolized_png_path)
        os.remove(output_symbolized_png_path + ".aux.xml")
        os.remove(pgw_file)
        os.remove(raster_canvas)
        os.remove(raster_canvas + ".aux.xml")

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
