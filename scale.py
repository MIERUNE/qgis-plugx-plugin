from qgis.core import (
    QgsProject,
    QgsRectangle,
    QgsPoint,
    QgsScaleCalculator,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
)
from qgis.utils import iface


def get_scale_from_canvas() -> float:
    """get scale from map canvas.
    For web mercator projection (EPSG:3857) case,
    calculate scale with map extent correction according to scale factor"""

    if QgsProject.instance().crs().authid() == "EPSG:3857":
        canvas = iface.mapCanvas()
        # get map canvas center coordinates in geographic
        transform = QgsCoordinateTransform(
            canvas.mapSettings().destinationCrs(),
            QgsCoordinateReferenceSystem("EPSG:4326"),
            QgsProject.instance(),
        )
        center_geographic = transform.transform(canvas.center())
        center_point = QgsPoint(center_geographic.x(), center_geographic.y())

        # calculate scale_factor from center_point
        # https://en.wikipedia.org/wiki/Mercator_projection#Scale_factor
        scale_factor_x = (
            QgsProject.instance().crs().factors(center_point).parallelScale()
        )
        scale_factor_y = (
            QgsProject.instance().crs().factors(center_point).meridionalScale()
        )

        # determine extension corrected with scale factor
        extent = canvas.extent()
        delta_x = (extent.width() * scale_factor_x) - extent.width()
        delta_y = (extent.height() * scale_factor_y) - extent.height()
        corrected_extent = QgsRectangle(
            extent.xMinimum() - delta_x / 2,
            extent.yMinimum() - delta_y / 2,
            extent.xMaximum() + delta_x / 2,
            extent.yMaximum() + delta_y / 2,
        )

        # calculate scale based on corrected map extent
        scale_calculator = QgsScaleCalculator(
            canvas.mapSettings().outputDpi(), canvas.mapUnits()
        )
        return scale_calculator.calculate(corrected_extent, canvas.size().width())
    else:
        return iface.mapCanvas().scale()


def set_map_extent_from(web_mercator_scale: float):
    """Calculate map extent with correction according to scale factor
    related to webmercator projection
    input: web mercator scale
    action: update map canvas extent
    """
    canvas = iface.mapCanvas()
    canvas_width_px = canvas.width()
    canvas_height_px = canvas.height()
    canvas_dpi = canvas.mapSettings().outputDpi()

    # Get the center point of the canvas extent
    transform = QgsCoordinateTransform(
        canvas.mapSettings().destinationCrs(),
        QgsCoordinateReferenceSystem("EPSG:4326"),
        QgsProject.instance(),
    )
    center_geographic = transform.transform(canvas.center())
    center_point = QgsPoint(center_geographic.x(), center_geographic.y())

    # calculate scale_factor from center_point
    # https://en.wikipedia.org/wiki/Mercator_projection#Scale_factor
    scale_factor_x = QgsProject.instance().crs().factors(center_point).parallelScale()
    scale_factor_y = QgsProject.instance().crs().factors(center_point).meridionalScale()

    # Calculate map units per pixel
    meter_per_inch = 0.0254  # 0.0254m in 1 inch
    map_units_per_pixel = (meter_per_inch / canvas_dpi) * web_mercator_scale

    # Calculate extent width and height in map units
    extent_width_map_units = canvas_width_px * map_units_per_pixel / scale_factor_x
    extent_height_map_units = canvas_height_px * map_units_per_pixel / scale_factor_y

    # Calculate the corrected extent
    canvas_center = canvas.extent().center()
    corrected_extent = QgsRectangle(
        canvas_center.x() - extent_width_map_units / 2,
        canvas_center.y() - extent_height_map_units / 2,
        canvas_center.x() + extent_width_map_units / 2,
        canvas_center.y() + extent_height_map_units / 2,
    )

    # update map canvas
    canvas.setExtent(corrected_extent)
    canvas.refresh()
