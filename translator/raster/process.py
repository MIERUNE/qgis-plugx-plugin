import os

from qgis.core import (
    QgsRasterLayer,
    QgsRectangle,
    QgsProject,
    QgsMapSettings,
    QgsMapRendererParallelJob,
)
from qgis.utils import iface
from PyQt5.QtCore import QSize

from utils import write_json


def process_raster(
    layer: QgsRasterLayer, extent: QgsRectangle, idx: int, output_dir: str
):
    # xy length in project-crs unit
    extent_width = extent.xMaximum() - extent.xMinimum()
    extent_height = extent.yMaximum() - extent.yMinimum()

    # calculate image size: same to map canvas
    units_per_pixel = iface.mapCanvas().mapUnitsPerPixel()
    image_width = int(extent_width / units_per_pixel)
    image_height = int(extent_height / units_per_pixel)

    # Set map to export image
    settings = QgsMapSettings()
    settings.setDestinationCrs(QgsProject.instance().crs())
    settings.setLayers([layer])
    settings.setExtent(extent)
    settings.setOutputSize(QSize(image_width, image_height))

    # Render the map
    render = QgsMapRendererParallelJob(settings)
    render.start()
    render.waitForFinished()

    # export rendered image as png
    image = render.renderedImage()
    image.save(os.path.join(output_dir, f"layer_{idx}.png"), "png")

    # make world file for check
    with open(os.path.join(output_dir, f"layer_{idx}.pgw"), "w") as f:
        f.write(f"{units_per_pixel}\n0.0\n0.0\n-{units_per_pixel}\n")
        f.write(f"{extent.xMinimum()}\n{extent.yMaximum()}\n")

    # json
    raster_info = {
        "layer": layer.name(),
        "type": "raster",
        "extent": [
            extent.xMinimum(),
            extent.yMinimum(),
            extent.xMaximum(),
            extent.yMaximum(),
        ],
    }
    write_json(raster_info, os.path.join(output_dir, f"layer_{idx}.json"))
