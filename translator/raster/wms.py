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


def process_wms(layer: QgsRasterLayer, extent: QgsRectangle, idx: int, output_dir: str):
    """process wms, xyz..."""
    # Convert Bbox to EPSG:3857
    transform = QgsCoordinateTransform(
        QgsProject.instance().crs(),
        QgsCoordinateReferenceSystem("EPSG:3857"),
        QgsProject.instance(),
    )
    extent_3857 = transform.transformBoundingBox(extent)
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

    clipped_tiff_path = os.path.join(output_dir, f"{layer.name()}_clipped.tif")

    # Save TIFF file in EPSG:3857
    file_writer = QgsRasterFileWriter(clipped_tiff_path)
    pipe = QgsRasterPipe()
    pipe.set(layer.dataProvider().clone())
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
    clip_extent = f"{extent.xMinimum()}, \
                    {extent.xMaximum()}, \
                    {extent.yMinimum()}, \
                    {extent.yMaximum()}  \
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
            "OUTPUT": os.path.join(output_dir, f"layer_{idx}.png"),
        },
    )

    # clean up
    os.remove(clipped_tiff_path)
    os.remove(clipped_tiff_path + ".aux.xml")
