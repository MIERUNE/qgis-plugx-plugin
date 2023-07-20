import os

from qgis.core import (
    QgsProject,
    QgsRasterFileWriter,
    QgsRasterLayer,
    QgsRasterPipe,
    QgsRectangle,
    QgsCoordinateTransform,
)
from qgis.utils import iface
import processing

from utils import get_tempdir


def process_wms(layer: QgsRasterLayer, extent: QgsRectangle, idx: int, output_dir: str):
    """process wms, xyz..."""

    # extent is in Project crs, transform to layer crs
    transform = QgsCoordinateTransform(
        QgsProject.instance().crs(),
        layer.crs(),
        QgsProject.instance(),
    )
    extent_in_layer_crs = transform.transformBoundingBox(extent)

    # xy length in project-crs unit
    extent_width = extent.xMaximum() - extent.xMinimum()
    extent_height = extent.yMaximum() - extent.yMinimum()

    # calculate image size: same to map canvas
    units_per_pixel = iface.mapCanvas().mapUnitsPerPixel()
    image_width = int(extent_width / units_per_pixel)
    image_height = int(extent_height / units_per_pixel)

    # export layer as tiff
    tiff_path = os.path.join(get_tempdir(output_dir), f"layer_{idx}.tiff")
    file_writer = QgsRasterFileWriter(tiff_path)
    pipe = QgsRasterPipe()
    pipe.set(layer.dataProvider().clone())
    file_writer.writeRaster(
        pipe,
        image_width,
        image_height,
        extent_in_layer_crs,
        layer.crs(),
    )

    # reproject to project crs, output as PNG
    png_path = os.path.join(output_dir, f"layer_{idx}.png")
    processing.run(
        "gdal:warpreproject",
        {
            "INPUT": tiff_path,
            "SOURCE_CRS": layer.crs(),
            "TARGET_CRS": QgsProject.instance().crs(),
            "TARGET_EXTENT": extent,
            "RESAMPLING": 1,
            "OUTPUT": png_path,
        },
    )
