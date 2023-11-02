import os
import processing

from qgis.core import QgsVectorLayer, QgsRectangle
from qgis.utils import iface

from plugx_utils import write_json


def generate_label_json(
    all_labels_layer: QgsVectorLayer, layername: str, idx: int, output_dir: str
):
    label_layer = processing.run(
        "native:extractbyattribute",
        {
            "INPUT": all_labels_layer,
            "FIELD": "Layer",
            "OPERATOR": 0,  # '='
            "VALUE": layername,
            "OUTPUT": "TEMPORARY_OUTPUT",
        },
    )["OUTPUT"]

    labels = []
    for feature in label_layer.getFeatures():
        if not feature["LabelUnplaced"]:
            # バッファーがない場合は色を#000000にする
            buffer_color = (
                "#000000" if not feature["BufferColor"] else str(feature["BufferColor"])
            )

            labels.append(
                {
                    "x": feature.geometry().asPoint().x(),
                    "y": feature.geometry().asPoint().y(),
                    "rotation": feature["LabelRotation"],
                    "text": feature["LabelText"],
                    "font": feature["Family"],
                    "size": feature["Size"],
                    "bold": feature["Bold"],
                    "underline": feature["Underline"],
                    "text:color": feature["Color"],
                    "text:opacity": feature["FontOpacity"],
                    "buffer:width": feature["BufferSize"],
                    "buffer:color": buffer_color,
                    "buffer:opacity": feature["BufferOpacity"],
                }
            )

    if len(labels) > 0:
        label_dict = {"layer": layername, "labels": labels}
        write_json(
            label_dict,
            os.path.join(output_dir, f"label_{idx}.json"),
        )


def generate_label_vector(extent: QgsRectangle) -> QgsVectorLayer:
    """export QgsVectorLayer of label, includes all layers"""
    label = processing.run(
        "native:extractlabels",
        {
            "EXTENT": extent,
            "SCALE": iface.mapCanvas().scale(),
            "MAP_THEME": None,
            "INCLUDE_UNPLACED": True,
            "DPI": iface.mapCanvas().mapSettings().outputDpi(),
            "OUTPUT": "TEMPORARY_OUTPUT",
        },
    )["OUTPUT"]

    return label
