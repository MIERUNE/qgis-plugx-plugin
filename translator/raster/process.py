import os

from qgis.core import (
    QgsRasterLayer,
    QgsRectangle,
    QgsProject,
    QgsMapSettings,
    QgsMapRendererParallelJob,
    QgsCoordinateTransform,
)
from qgis.utils import iface
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor

from plugx_utils import write_json
from translator.utils import get_blend_mode_string


def process_raster(
    layer: QgsRasterLayer, extent: QgsRectangle, idx: int, output_dir: str
):
    # transform layer-extent to project-crs
    transform = QgsCoordinateTransform(
        layer.crs(),
        QgsProject.instance().crs(),
        QgsProject.instance(),
    )
    layer_extent = transform.transformBoundingBox(layer.extent())

    # minimal extent of layer-extent and output-extent
    intersected_extent = extent.intersect(layer_extent)
    if intersected_extent.isEmpty():
        # no intersected extent: skip
        return {
            "idx": idx,
            "layer_name": layer.name(),
            "completed": False,
            "reason": "extent is empty",
        }

    # xy length in project-crs unit
    extent_width = intersected_extent.xMaximum() - intersected_extent.xMinimum()
    extent_height = intersected_extent.yMaximum() - intersected_extent.yMinimum()

    # calculate image size: same to map canvas
    units_per_pixel = iface.mapCanvas().mapUnitsPerPixel()
    image_width = int(extent_width / units_per_pixel)
    image_height = int(extent_height / units_per_pixel)

    # Set map to export image
    settings = QgsMapSettings()
    settings.setDestinationCrs(QgsProject.instance().crs())
    settings.setBackgroundColor(QColor(255, 255, 255, 0))  # transparent
    _layer = layer.clone()  # clone to avoid changing opacity of original layer
    _layer.setOpacity(1.0)
    settings.setLayers([_layer])
    settings.setExtent(intersected_extent)
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
        f.write(f"{intersected_extent.xMinimum()}\n{intersected_extent.yMaximum()}\n")

    # json
    raster_info = {
        "layer": layer.name(),
        "type": "raster",
        "extent": [
            intersected_extent.xMinimum(),
            intersected_extent.yMinimum(),
            intersected_extent.xMaximum(),
            intersected_extent.yMaximum(),
        ],
        "opacity": layer.opacity(),
        "blend_mode": get_blend_mode_string(layer.blendMode()),
    }
    write_json(raster_info, os.path.join(output_dir, f"layer_{idx}.json"))

    return {
        "idx": idx,
        "layer_name": layer.name(),
        "completed": True,
    }
