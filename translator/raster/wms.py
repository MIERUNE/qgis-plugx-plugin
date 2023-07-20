import os

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsProject,
    QgsRasterFileWriter,
    QgsRasterLayer,
    QgsRasterPipe,
    QgsRectangle,
    Qgis,
    QgsCoordinateTransform,
)
from qgis.utils import iface
import processing

from utils import get_tempdir


def _get_multiplier_by_unit_of(crs: QgsCoordinateReferenceSystem) -> float:
    """return multiplier: crs unit -> inch"""
    if crs.mapUnits() == Qgis.DistanceUnit.Meters:
        multiplier_to_meter = 1.0
    elif crs.mapUnits() == Qgis.DistanceUnit.Kilometers:
        multiplier_to_meter = 1000.0
    elif crs.mapUnits() == Qgis.DistanceUnit.Feet:
        multiplier_to_meter = 0.3048
    elif crs.mapUnits() == Qgis.DistanceUnit.NauticalMiles:
        multiplier_to_meter = 1852.0
    elif crs.mapUnits() == Qgis.DistanceUnit.Yards:
        multiplier_to_meter = 0.9144
    elif crs.mapUnits() == Qgis.DistanceUnit.Miles:
        multiplier_to_meter = 1609.344
    elif crs.mapUnits() == Qgis.DistanceUnit.Degrees:
        multiplier_to_meter = 111319.49079327358  # at equator
    elif crs.mapUnits() == Qgis.DistanceUnit.Centimeters:
        multiplier_to_meter = 0.01
    elif crs.mapUnits() == Qgis.DistanceUnit.Millimeters:
        multiplier_to_meter = 0.001
    elif crs.mapUnits() == Qgis.DistanceUnit.Inches:
        multiplier_to_meter = 0.0254
    else:
        multiplier_to_meter = 1.0  # fallback

    multiplier_to_inch = multiplier_to_meter / 0.0254
    return multiplier_to_inch


def process_wms(layer: QgsRasterLayer, extent: QgsRectangle, idx: int, output_dir: str):
    """process wms, xyz..."""

    # extent is in Project crs, transform to layer crs
    transform = QgsCoordinateTransform(
        QgsProject.instance().crs(),
        layer.crs(),
        QgsProject.instance(),
    )
    extent_in_layer_crs = transform.transformBoundingBox(extent)

    # Calculate image size in pixels
    dpi = iface.mapCanvas().mapSettings().outputDpi()  # dots / inch
    inch_to_crs_unit = _get_multiplier_by_unit_of(QgsProject.instance().crs())
    # xy length in project-crs unit
    extent_width = extent.xMaximum() - extent.xMinimum()
    extent_height = extent.yMaximum() - extent.yMinimum()
    # length_in_dots = length_in_crs_unit / (dpm = dpi/inch_to_crs_unit)
    image_width = int(extent_width / dpi * inch_to_crs_unit)
    image_height = int(extent_height / dpi * inch_to_crs_unit)

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
