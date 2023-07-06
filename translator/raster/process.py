import os

from qgis.core import (
    QgsRasterLayer,
    QgsRectangle,
)

from utils import write_json
from .wms import process_wms
from .file import process_file


def process_raster(
    layer: QgsRasterLayer, extent: QgsRectangle, idx: int, output_dir: str
):
    print(layer.name(), layer.providerType())
    if layer.providerType() == "wms":
        process_wms(layer, extent, idx, output_dir)
    else:
        process_file(layer, extent, idx, output_dir)

    # json
    raster_info = {
        "layer": layer.name(),
        "type": "raster",
        "crs": layer.crs().authid(),
        "extent": [
            extent.xMinimum(),
            extent.yMinimum(),
            extent.xMaximum(),
            extent.yMaximum(),
        ],
    }
    write_json(raster_info, os.path.join(output_dir, f"layer_{idx}.json"))
