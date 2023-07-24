from qgis.core import QgsSymbolLayer, QgsSimpleMarkerSymbolLayer


from utils import convert_to_point
from translator.vector.symbol.utils import get_asset_name, to_rgba


def _get_markershape_from(symbol_shape: QgsSimpleMarkerSymbolLayer) -> str:
    return {
        QgsSimpleMarkerSymbolLayer.Shape.Square: "square",
        QgsSimpleMarkerSymbolLayer.Shape.Diamond: "diamond",
        QgsSimpleMarkerSymbolLayer.Shape.Pentagon: "pentagon",
        QgsSimpleMarkerSymbolLayer.Shape.Hexagon: "hexagon",
        QgsSimpleMarkerSymbolLayer.Shape.Triangle: "triangle",
        QgsSimpleMarkerSymbolLayer.Shape.EquilateralTriangle: "equilateraltriangle",
        QgsSimpleMarkerSymbolLayer.Shape.Star: "star",
        QgsSimpleMarkerSymbolLayer.Shape.Arrow: "arrow",
        QgsSimpleMarkerSymbolLayer.Shape.Circle: "circle",
        QgsSimpleMarkerSymbolLayer.Shape.Cross: "cross",
        QgsSimpleMarkerSymbolLayer.Shape.CrossFill: "crossfill",
        QgsSimpleMarkerSymbolLayer.Shape.Cross2: "cross2",
        QgsSimpleMarkerSymbolLayer.Shape.Line: "line",
        QgsSimpleMarkerSymbolLayer.Shape.ArrowHead: "arrowhead",
        QgsSimpleMarkerSymbolLayer.Shape.ArrowHeadFilled: "arrowheadfilled",
        QgsSimpleMarkerSymbolLayer.Shape.SemiCircle: "semicircle",
        QgsSimpleMarkerSymbolLayer.Shape.ThirdCircle: "thirdcircle",
        QgsSimpleMarkerSymbolLayer.Shape.QuarterCircle: "quartercircle",
        QgsSimpleMarkerSymbolLayer.Shape.QuarterSquare: "quartersquare",
        QgsSimpleMarkerSymbolLayer.Shape.HalfSquare: "halfsquare",
        QgsSimpleMarkerSymbolLayer.Shape.DiagonalHalfSquare: "diagonalhalfsquare",
        QgsSimpleMarkerSymbolLayer.Shape.RightHalfTriangle: "righthalftriangle",
        QgsSimpleMarkerSymbolLayer.Shape.LeftHalfTriangle: "lefthalftriangle",
        QgsSimpleMarkerSymbolLayer.Shape.Trapezoid: "trapezoid",
        QgsSimpleMarkerSymbolLayer.Shape.ParallelogramLeft: "parallelogramleft",
        QgsSimpleMarkerSymbolLayer.Shape.ParallelogramRight: "parallelogramright",
        QgsSimpleMarkerSymbolLayer.Shape.Shield: "shield",
        QgsSimpleMarkerSymbolLayer.Shape.Octagon: "octagon",
        QgsSimpleMarkerSymbolLayer.Shape.Decagon: "decagon",
        QgsSimpleMarkerSymbolLayer.Shape.SquareWithCorners: "squarecorners",
        QgsSimpleMarkerSymbolLayer.Shape.RoundedSquare: "squarerounded",
        QgsSimpleMarkerSymbolLayer.Shape.DiamondStar: "diamondstar",
        QgsSimpleMarkerSymbolLayer.Shape.Heart: "heart",
        QgsSimpleMarkerSymbolLayer.Shape.HalfArc: "halfarc",
        QgsSimpleMarkerSymbolLayer.Shape.ThirdArc: "thirdarc",
        QgsSimpleMarkerSymbolLayer.Shape.QuarterArc: "quarterarc",
        QgsSimpleMarkerSymbolLayer.Shape.AsteriskFill: "asteriskfill",
    }.get(
        symbol_shape, "circle"  # fallback
    )


def get_point_symbol_data(symbol_layer: QgsSymbolLayer) -> dict:
    if symbol_layer.layerType() == "RasterMarker":
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "type": "raster",
            "asset_path": "assets/raster/" + get_asset_name(symbol_layer),
            "offset": [
                convert_to_point(symbol_layer.offset().x(), symbol_layer.offsetUnit()),
                convert_to_point(symbol_layer.offset().y(), symbol_layer.offsetUnit()),
            ],
            "rotation": symbol_layer.angle(),
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
            "offset": [
                convert_to_point(symbol_layer.offset().x(), symbol_layer.offsetUnit()),
                convert_to_point(symbol_layer.offset().y(), symbol_layer.offsetUnit()),
            ],
            "rotation": symbol_layer.angle(),
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
            "shape": _get_markershape_from(symbol_layer.shape()),
            "offset": [
                convert_to_point(symbol_layer.offset().x(), symbol_layer.offsetUnit()),
                convert_to_point(symbol_layer.offset().y(), symbol_layer.offsetUnit()),
            ],
            "rotation": symbol_layer.angle(),
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
