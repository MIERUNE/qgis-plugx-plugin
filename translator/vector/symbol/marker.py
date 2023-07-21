from qgis.core import QgsSymbolLayer, QgsMarkerSymbolLayer


from utils import convert_to_point
from translator.vector.symbol.utils import get_asset_name, to_rgba


def _get_markershape_from(symbol_layer: QgsSymbolLayer) -> dict:
    return {
        QgsMarkerSymbolLayer.Shape.Square: "square",
        QgsMarkerSymbolLayer.Shape.Diamond: "diamond",
        QgsMarkerSymbolLayer.Shape.Pentagon: "pentagon",
        QgsMarkerSymbolLayer.Shape.Hexagon: "hexagon",
        QgsMarkerSymbolLayer.Shape.Triangle: "triangle",
        QgsMarkerSymbolLayer.Shape.EquilateralTriangle: "equilateraltriangle",
        QgsMarkerSymbolLayer.Shape.Star: "star",
        QgsMarkerSymbolLayer.Shape.Arrow: "arrow",
        QgsMarkerSymbolLayer.Shape.Circle: "circle",
        QgsMarkerSymbolLayer.Shape.Cross: "cross",
        QgsMarkerSymbolLayer.Shape.CrossFill: "crossfill",
        QgsMarkerSymbolLayer.Shape.Cross2: "cross2",
        QgsMarkerSymbolLayer.Shape.Line: "line",
        QgsMarkerSymbolLayer.Shape.ArrowHead: "arrowhead",
        QgsMarkerSymbolLayer.Shape.ArrowHeadFilled: "arrowheadfilled",
        QgsMarkerSymbolLayer.Shape.SemiCircle: "semicircle",
        QgsMarkerSymbolLayer.Shape.ThirdCircle: "thirdcircle",
        QgsMarkerSymbolLayer.Shape.QuarterCircle: "quartercircle",
        QgsMarkerSymbolLayer.Shape.QuarterSquare: "quartersquare",
        QgsMarkerSymbolLayer.Shape.HalfSquare: "halfsquare",
        QgsMarkerSymbolLayer.Shape.DiagonalHalfSquare: "diagonalhalfsquare",
        QgsMarkerSymbolLayer.Shape.RightHalfTriangle: "righthalftriangle",
        QgsMarkerSymbolLayer.Shape.LeftHalfTriangle: "lefthalftriangle",
    }.get(
        symbol_layer.shape(), "circle"  # fallback
    )


def get_point_symbol_data(symbol_layer: QgsSymbolLayer) -> dict:
    if symbol_layer.layerType() == "RasterMarker":
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "type": "raster",
            "asset_path": "assets/raster/" + get_asset_name(symbol_layer),
            "level": symbol_layer.renderingPass(),  # renderingPass means symbolLevels
            # https://github.com/qgis/QGIS/blob/65d40ee0ce59e761ee2de366ca9a963f35adfcfd/src/core/vector/qgsvectorlayerrenderer.cpp#L702
        }

    elif symbol_layer.layerType() == "SvgMarker":
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "color": to_rgba(symbol_layer.color()),
            "outline_color": to_rgba(symbol_layer.strokeColor()),
            "outline_width": convert_to_point(
                symbol_layer.strokeWidth(), symbol_layer.strokeWidthUnit()
            ),
            "type": "svg",
            "asset_path": "assets/svg/" + get_asset_name(symbol_layer),
            "level": symbol_layer.renderingPass(),
        }

    elif symbol_layer.layerType() == "SimpleMarker":
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "color": to_rgba(symbol_layer.color()),
            "outline_color": to_rgba(symbol_layer.strokeColor()),
            "outline_width": convert_to_point(
                symbol_layer.strokeWidth(), symbol_layer.strokeWidthUnit()
            ),
            "type": "simple",
            "shape": _get_markershape_from(symbol_layer),
            "offset": [
                convert_to_point(symbol_layer.offset().x(), symbol_layer.offsetUnit()),
                convert_to_point(symbol_layer.offset().y(), symbol_layer.offsetUnit()),
            ],
            "level": symbol_layer.renderingPass(),
        }

    elif symbol_layer.layerType() == "FontMarker":
        # TODO: implement
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "color": to_rgba(symbol_layer.color()),
            "type": "font",
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "AnimatedMarker":
        # TODO: implement
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "type": "animated",
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "EllipseMarker":
        # TODO: implement
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "color": to_rgba(symbol_layer.color()),
            "type": "ellipse",
            "level": symbol_layer.renderingPass(),
        }
    elif symbol_layer.layerType() == "FilledMarker":
        # TODO: implement
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "type": "filled",
            "level": symbol_layer.renderingPass(),
        }
    elif (
        symbol_layer.layerType() == "GeometryGenerator"
        or symbol_layer.layerType() == "VectorField"
        or symbol_layer.layerType() == "MaskMarker"
    ):
        # never to be supported...
        symbol_layer_dict = {
            "size": 0,
            "color": "#000000",
            "type": "unsupported",
            "level": symbol_layer.renderingPass(),
        }
    else:
        raise Exception("Unexpected symbol layer type")

    return symbol_layer_dict
