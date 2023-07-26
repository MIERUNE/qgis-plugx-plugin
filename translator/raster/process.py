import os

from qgis.core import (
    QgsRasterLayer,
    QgsRectangle,
)

from utils import write_json
from translator.utils import get_blend_mode_string
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
        "extent": [
            extent.xMinimum(),
            extent.yMinimum(),
            extent.xMaximum(),
            extent.yMaximum(),
        ],
        "opacity": layer.opacity(),
        "blend_mode": get_blend_mode_string(layer.blendMode()),
    }
    write_json(raster_info, os.path.join(output_dir, f"layer_{idx}.json"))
