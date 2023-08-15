import os

import processing
from qgis.core import (
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsRectangle,
    NULL,
)
from .symbol import (
    generate_symbols_data,
    export_assets_from,
    is_included_unsupported_symbol_layer,
)

from utils import write_json
from translator.utils import get_blend_mode_string


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


def _preprocess_layer(
    layer: QgsVectorLayer, extent: QgsRectangle
) -> (QgsVectorLayer, str):
    """clip and calculate on-the-fly attribute
    layer -> clip by extent -> if has on-the-fly attribute, calculate it -> return
    """
    layer_clipped = _clip_in_projectcrs(layer, extent)

    if layer.renderer().classAttribute() in layer.fields().names():
        return layer_clipped, layer.renderer().classAttribute()
    else:
        target_field = "tmp_calc"
        calculated_layer = processing.run(
            "native:fieldcalculator",
            {
                "INPUT": layer_clipped,
                "FIELD_NAME": target_field,
                "FIELD_TYPE": _get_field_value_type(layer),
                "FIELD_LENGTH": 0,
                "FIELD_PRECISION": 0,
                "FORMULA": f"{layer.renderer().classAttribute()}",
                "OUTPUT": "TEMPORARY_OUTPUT",
            },
        )["OUTPUT"]
        return calculated_layer, target_field


def _generate_shapefile(layer: QgsVectorLayer, features: list, shp_path: str):
    output_layer = QgsVectorFileWriter(
        shp_path,
        "UTF-8",
        layer.fields(),
        layer.wkbType(),
        QgsProject.instance().crs(),
        "ESRI Shapefile",
    )
    output_layer.addFeatures(features)
    del output_layer


def _get_field_value_type(layer: QgsVectorLayer) -> int:
    if layer.renderer().type() == "categorizedSymbol":
        # enum for calculate field class
        # https://docs.qgis.org/3.28/en/docs/user_manual/processing_algs/qgis/vectortable.html#qgisfieldcalculator
        if type(layer.renderer().categories()[0].value()) == float:
            return 0
        elif type(layer.renderer().categories()[0].value()) == int:
            return 1
        elif type(layer.renderer().categories()[0].value()) == str:
            return 2

    elif layer.renderer().type() == "graduatedSymbol":
        # graduated ranges are float values
        return 0


def process_vector(
    layer: QgsVectorLayer, extent: QgsRectangle, idx: int, output_dir: str
) -> dict:
    if layer.renderer().type() == "categorizedSymbol":
        result = _process_categorical(layer, extent, idx, output_dir)
    elif layer.renderer().type() == "graduatedSymbol":
        result = _process_graduated(layer, extent, idx, output_dir)
    elif layer.renderer().type() == "singleSymbol":
        result = _process_singlesymbol(layer, extent, idx, output_dir)
    else:
        result = _process_unsupported_renderer(layer, extent, idx, output_dir)
    return result


def _process_categorical(
    layer: QgsVectorLayer, extent: QgsRectangle, idx: int, output_dir: str
) -> dict:
    layer_normalized, target_field = _preprocess_layer(layer, extent)

    # Make uncompleted if no feature in canvas
    if layer_normalized.featureCount() == 0:
        return {
            "idx": idx,
            "layer_name": layer.name(),
            "has_unsupported_symbol": False,
            "reason": "no feature in canvas",
            "completed": False,
        }

    has_unsupported_symbol = False

    for sub_idx, category in enumerate(layer.renderer().categories()):
        # extract features by category
        if category.value() == "" or category.value() == NULL:
            # all other values (defined with "" or NULL value)

            # get list of all defined category values
            #  → [1, 2, 4, '', NULL]
            category_values = [cat.value() for cat in layer.renderer().categories()]

            # List unempty category values (remove NULL and '' values)
            #  → [1, 2, 4]
            exclude_values = list(filter(None, category_values))

            # Get features excluding unempty defined category values (5, 9, '', etc.)
            filtered_features = list(
                filter(
                    lambda f: f[target_field] not in exclude_values,
                    layer_normalized.getFeatures(),
                )
            )
        else:
            filtered_features = list(
                filter(
                    lambda f: f[target_field] == category.value(),
                    layer_normalized.getFeatures(),
                )
            )

        # no produce shp, json or asset if no feature
        if len(filtered_features) == 0:
            continue

        # shp
        shp_path = os.path.join(output_dir, f"layer_{idx}_{sub_idx}.shp")
        _generate_shapefile(layer, filtered_features, shp_path)

        # json
        layer_json = {
            "layer": layer.name(),
            "type": _get_layer_type(layer),
            "symbols": generate_symbols_data(category.symbol()),
            "usingSymbolLevels": layer.renderer().usingSymbolLevels(),
            "legend": category.label(),
            "opacity": layer.opacity(),
            "blend_mode": get_blend_mode_string(layer.blendMode()),
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
        "idx": idx,
        "layer_name": layer.name(),
        "has_unsupported_symbol": has_unsupported_symbol,
        "completed": True,
    }


def _process_graduated(
    layer: QgsVectorLayer, extent: QgsRectangle, idx: int, output_dir: str
) -> dict:
    layer_normalized, target_field = _preprocess_layer(layer, extent)

    # Make uncompleted if no feature in canvas
    if layer_normalized.featureCount() == 0:
        return {
            "idx": idx,
            "layer_name": layer.name(),
            "has_unsupported_symbol": False,
            "reason": "no feature in canvas",
            "completed": False,
        }

    has_unsupported_symbol = False

    for sub_idx, range in enumerate(layer.renderer().ranges()):
        # filter features
        # 1: filter out null value: on-the-fly attribute may have null value
        # 2: extract features by range
        filtered_features = list(
            filter(
                lambda f: f[target_field] is not None
                and range.lowerValue() < f[target_field] <= range.upperValue(),
                layer_normalized.getFeatures(),
            )
        )

        # no produce shp, json or asset if no feature
        if len(filtered_features) == 0:
            continue

        # shp
        shp_path = os.path.join(output_dir, f"layer_{idx}_{sub_idx}.shp")
        _generate_shapefile(layer, filtered_features, shp_path)

        # json
        layer_json = {
            "layer": layer.name(),
            "type": _get_layer_type(layer),
            "symbols": generate_symbols_data(range.symbol()),
            "usingSymbolLevels": layer.renderer().usingSymbolLevels(),
            "legend": range.label(),
            "opacity": layer.opacity(),
            "blend_mode": get_blend_mode_string(layer.blendMode()),
        }
        write_json(
            layer_json,
            os.path.join(output_dir, f"layer_{idx}_{sub_idx}.json"),
        )

        # asset
        export_assets_from(range.symbol(), output_dir)

        has_unsupported_symbol = (
            has_unsupported_symbol
            or is_included_unsupported_symbol_layer(range.symbol())
        )

    return {
        "idx": idx,
        "layer_name": layer.name(),
        "has_unsupported_symbol": has_unsupported_symbol,
        "completed": True,
    }


def _process_singlesymbol(
    layer: QgsVectorLayer, extent: QgsRectangle, idx: int, output_dir: str
) -> dict:
    layer_intersected = _clip_in_projectcrs(layer, extent)

    # no produce shp, json or asset if no feature
    if layer_intersected.featureCount() == 0:
        return {
            "idx": idx,
            "layer_name": layer.name(),
            "has_unsupported_symbol": False,
            "reason": "no feature in canvas",
            "completed": False,
        }

    # shp
    shp_path = os.path.join(output_dir, f"layer_{idx}.shp")
    _generate_shapefile(layer, layer_intersected.getFeatures(), shp_path)

    # json
    layer_json = {
        "layer": layer.name(),
        "type": _get_layer_type(layer),
        "symbols": generate_symbols_data(layer.renderer().symbol()),
        "usingSymbolLevels": layer.renderer().usingSymbolLevels(),
        "opacity": layer.opacity(),
        "blend_mode": get_blend_mode_string(layer.blendMode()),
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
        "idx": idx,
        "layer_name": layer.name(),
        "has_unsupported_symbol": has_unsupported_symbol,
        "completed": True,
    }


def _process_unsupported_renderer(
    layer: QgsVectorLayer, extent: QgsRectangle, idx: int, output_dir: str
) -> dict:
    return {
        "idx": idx,
        "layer_name": layer.name(),
        "has_unsupported_symbol": False,
        "reason": "unsupported renderer",
        "completed": False,
    }
