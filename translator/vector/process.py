import os

import processing
from qgis.core import QgsProject, QgsVectorFileWriter, QgsVectorLayer, QgsRectangle
from .symbol import (
    generate_symbols_data,
    export_assets_from,
    is_included_unsupported_symbol_layer,
)

from utils import write_json


def _clip_in_projectcrs(layer: QgsVectorLayer, extent: QgsRectangle) -> QgsVectorLayer:
    """
    Clip layer by extent

    Args:
        layer (QgsVectorLayer): Any CRS
        extent (QgsRectangle): in Project CRS

    Returns:
        QgsVectorLayer: clipped layer in Project CRS
    """

    reprojected = processing.run(
        "native:reprojectlayer",
        {
            "INPUT": layer,
            "TARGET_CRS": QgsProject.instance().crs(),
            "OUTPUT": "TEMPORARY_OUTPUT",
        },
    )["OUTPUT"]

    clip_extent = f"{extent.xMinimum()}, {extent.xMaximum()}, \
            {extent.yMinimum()}, {extent.yMaximum()}  \
            [{QgsProject.instance().crs().authid()}]"

    layer_intersected = processing.run(
        "native:extractbyextent",
        {
            "INPUT": reprojected,
            "EXTENT": clip_extent,
            "CLIP": True,
            "OUTPUT": "TEMPORARY_OUTPUT",
        },
    )["OUTPUT"]

    return layer_intersected


def _get_layer_type(layer: QgsVectorLayer):
    if layer.geometryType() == 0:
        return "point"
    elif layer.geometryType() == 1:
        return "line"
    elif layer.geometryType() == 2:
        return "polygon"
    else:
        return "unsupported"


def process_vector(
    layer: QgsVectorLayer, extent: QgsRectangle, idx: int, output_dir: str
) -> dict:
    if layer.renderer().type() == "categorizedSymbol":
        result = _process_categorical(layer, extent, idx, output_dir)
    elif layer.renderer().type() == "singleSymbol":
        result = _process_noncategorical(layer, extent, idx, output_dir)

    return result


def _process_categorical(
    layer: QgsVectorLayer, extent: QgsRectangle, idx: int, output_dir: str
) -> dict:
    layer_intersected = _clip_in_projectcrs(layer, extent)
    has_unsupported_symbol = False
    for sub_idx, category in enumerate(layer.renderer().categories()):
        # shp
        shp_path = os.path.join(output_dir, f"layer_{idx}_{sub_idx}.shp")
        output_layer = QgsVectorFileWriter(
            shp_path,
            "UTF-8",
            layer.fields(),
            layer.wkbType(),
            QgsProject.instance().crs(),
            "ESRI Shapefile",
        )
        # extract features by category
        filtered_features = list(
            filter(
                lambda f: f[layer.renderer().classAttribute()] == category.value(),
                layer_intersected.getFeatures(),
            )
        )
        output_layer.addFeatures(filtered_features)
        del output_layer

        # json
        layer_json = {
            "layer": layer.name(),
            "type": _get_layer_type(layer),
            "crs": layer.crs().authid(),
            "symbol": generate_symbols_data(category.symbol()),
            "legend": category.label(),
        }
        write_json(
            layer_json,
            os.path.join(output_dir, f"layer_{idx}_{sub_idx}.json"),
        )

        # asset
        export_assets_from(category.symbol(), output_dir)

        has_unsupported_symbol = (
            has_unsupported_symbol
            or is_included_unsupported_symbol_layer(category.symbol())
        )
    return {
        "has_unsupported_symbol": has_unsupported_symbol,
    }


def _process_noncategorical(
    layer: QgsVectorLayer, extent: QgsRectangle, idx: int, output_dir: str
) -> dict:
    # shp
    shp_path = os.path.join(output_dir, f"layer_{idx}.shp")
    layer_intersected = _clip_in_projectcrs(layer, extent)
    output_layer = QgsVectorFileWriter(
        shp_path,
        "UTF-8",
        layer.fields(),
        layer.wkbType(),
        QgsProject.instance().crs(),
        "ESRI Shapefile",
    )
    output_layer.addFeatures(layer_intersected.getFeatures())
    del output_layer

    # json
    layer_json = {
        "layer": layer.name(),
        "type": _get_layer_type(layer),
        "crs": layer.crs().authid(),
        "symbol": generate_symbols_data(layer.renderer().symbol()),
    }
    write_json(
        layer_json,
        os.path.join(output_dir, f"layer_{idx}.json"),
    )

    # asset
    export_assets_from(layer.renderer().symbol(), output_dir)

    has_unsupported_symbol = is_included_unsupported_symbol_layer(
        layer.renderer().symbol()
    )

    return {
        "has_unsupported_symbol": has_unsupported_symbol,
    }
