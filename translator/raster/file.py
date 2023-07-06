import os

import processing
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsProject,
    QgsRasterLayer,
    QgsRectangle,
    QgsMapSettings,
    QgsMapRendererParallelJob,
)
from qgis.utils import iface
from PyQt5.QtCore import QSize
from qgis.PyQt.QtGui import QImage, QColor


def _process_multiband(
    layer: QgsRasterLayer, extent: QgsRectangle, idx: int, output_dir: str
):
    # Create clip PNG file in Project CRS
    output_png_path = os.path.join(output_dir, f"layer_{idx}.png")

    # Convert to Project CRS
    warped = processing.run(
        "gdal:warpreproject",
        {
            "INPUT": layer,
            "SOURCE_CRS": layer.crs(),
            "TARGET_CRS": QgsProject.instance().crs(),
            "OUTPUT": "TEMPORARY_OUTPUT",
        },
    )["OUTPUT"]

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
            "OUTPUT": output_png_path,
        },
    )


def _process_singleband(
    layer: QgsRasterLayer, extent: QgsRectangle, idx: int, output_dir: str
):
    # single band raster with 1 band
    # Reproject input raster to 2451
    reprojeted = processing.run(
        "gdal:warpreproject",
        {
            "INPUT": layer,
            "SOURCE_CRS": layer.crs(),
            "TARGET_CRS": QgsCoordinateReferenceSystem("EPSG:2451"),
            "OUTPUT": "TEMPORARY_OUTPUT",
        },
    )["OUTPUT"]

    layer_geographic = QgsRasterLayer(reprojeted, "Raster Layer")

    # set style to layer geographic from input raster
    layer_geographic.setRenderer(layer.renderer().clone())

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
    map_settings.setExtent(layer_geographic.extent())
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
        output_dir, layer.name() + "_symbolized.png"
    )
    image.save(output_symbolized_png_path, "png")

    # Generate input raster world file
    pgw_file = output_symbolized_png_path.replace(".png", ".pgw")

    raster_canvas = os.path.join(output_dir, layer.name() + "_canvas.png")
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

    wld_file = os.path.join(output_dir, layer.name() + "_canvas.wld")
    os.rename(wld_file, pgw_file)

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

    # Clip converted PNG file
    output_png_path = os.path.join(output_dir, f"layer_{idx}.png")

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
            "OUTPUT": output_png_path,
        },
    )

    # clean up
    os.remove(output_symbolized_png_path)
    os.remove(output_symbolized_png_path + ".aux.xml")
    os.remove(pgw_file)
    os.remove(raster_canvas)
    os.remove(raster_canvas + ".aux.xml")


def process_file(
    layer: QgsRasterLayer, extent: QgsRectangle, idx: int, output_dir: str
):
    if layer.rasterType() == QgsRasterLayer.LayerType.Multiband:
        # RGB image
        _process_multiband(layer, extent, idx, output_dir)
    elif (
        layer.rasterType() == QgsRasterLayer.LayerType.GrayOrUndefined
        and layer.bandCount() == 1
    ):
        _process_singleband(layer, extent, idx, output_dir)
