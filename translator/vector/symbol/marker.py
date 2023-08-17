from qgis.core import (
    QgsMarkerSymbolLayer,
    QgsSimpleMarkerSymbolLayerBase,
    QgsRasterMarkerSymbolLayer,
    QgsSvgMarkerSymbolLayer,
)
from typing import Union

from utils import convert_to_point
from translator.vector.symbol.utils import get_asset_name, to_rgba
from translator.vector.symbol.penstyle import get_penstyle_from


def _get_markershape_from(symbol_shape: QgsSimpleMarkerSymbolLayerBase.Shape) -> str:
    return {
        QgsSimpleMarkerSymbolLayerBase.Shape.Square: "square",
        QgsSimpleMarkerSymbolLayerBase.Shape.Diamond: "diamond",
        QgsSimpleMarkerSymbolLayerBase.Shape.Pentagon: "pentagon",
        QgsSimpleMarkerSymbolLayerBase.Shape.Hexagon: "hexagon",
        QgsSimpleMarkerSymbolLayerBase.Shape.Triangle: "triangle",
        QgsSimpleMarkerSymbolLayerBase.Shape.EquilateralTriangle: "equilateraltriangle",
        QgsSimpleMarkerSymbolLayerBase.Shape.Star: "star",
        QgsSimpleMarkerSymbolLayerBase.Shape.Arrow: "arrow",
        QgsSimpleMarkerSymbolLayerBase.Shape.Circle: "circle",
        QgsSimpleMarkerSymbolLayerBase.Shape.Cross: "cross",
        QgsSimpleMarkerSymbolLayerBase.Shape.CrossFill: "crossfill",
        QgsSimpleMarkerSymbolLayerBase.Shape.Cross2: "cross2",
        QgsSimpleMarkerSymbolLayerBase.Shape.Line: "line",
        QgsSimpleMarkerSymbolLayerBase.Shape.ArrowHead: "arrowhead",
        QgsSimpleMarkerSymbolLayerBase.Shape.ArrowHeadFilled: "arrowheadfilled",
        QgsSimpleMarkerSymbolLayerBase.Shape.SemiCircle: "semicircle",
        QgsSimpleMarkerSymbolLayerBase.Shape.ThirdCircle: "thirdcircle",
        QgsSimpleMarkerSymbolLayerBase.Shape.QuarterCircle: "quartercircle",
        QgsSimpleMarkerSymbolLayerBase.Shape.QuarterSquare: "quartersquare",
        QgsSimpleMarkerSymbolLayerBase.Shape.HalfSquare: "halfsquare",
        QgsSimpleMarkerSymbolLayerBase.Shape.DiagonalHalfSquare: "diagonalhalfsquare",
        QgsSimpleMarkerSymbolLayerBase.Shape.RightHalfTriangle: "righthalftriangle",
        QgsSimpleMarkerSymbolLayerBase.Shape.LeftHalfTriangle: "lefthalftriangle",
        QgsSimpleMarkerSymbolLayerBase.Shape.Trapezoid: "trapezoid",
        QgsSimpleMarkerSymbolLayerBase.Shape.ParallelogramLeft: "parallelogramleft",
        QgsSimpleMarkerSymbolLayerBase.Shape.ParallelogramRight: "parallelogramright",
        QgsSimpleMarkerSymbolLayerBase.Shape.Shield: "shield",
        QgsSimpleMarkerSymbolLayerBase.Shape.Octagon: "octagon",
        QgsSimpleMarkerSymbolLayerBase.Shape.Decagon: "decagon",
        QgsSimpleMarkerSymbolLayerBase.Shape.SquareWithCorners: "squarecorners",
        QgsSimpleMarkerSymbolLayerBase.Shape.RoundedSquare: "squarerounded",
        QgsSimpleMarkerSymbolLayerBase.Shape.DiamondStar: "diamondstar",
        QgsSimpleMarkerSymbolLayerBase.Shape.Heart: "heart",
        QgsSimpleMarkerSymbolLayerBase.Shape.HalfArc: "halfarc",
        QgsSimpleMarkerSymbolLayerBase.Shape.ThirdArc: "thirdarc",
        QgsSimpleMarkerSymbolLayerBase.Shape.QuarterArc: "quarterarc",
        QgsSimpleMarkerSymbolLayerBase.Shape.AsteriskFill: "asteriskfill",
    }.get(
        symbol_shape, "circle"  # fallback
    )


def _is_customizable_color(svg_path: str) -> bool:
    is_customizable_color = False
    svg_tree = ET.parse(svg_path)
    svg_root = svg_tree.getroot()
    for param in svg_root.iter():
        if param.get("fill") == "param(fill)":
            is_customizable_color = True
    return is_customizable_color


def _get_asset_height(
    symbol_layer: Union[QgsRasterMarkerSymbolLayer, QgsSvgMarkerSymbolLayer]
) -> float:
    """calculate svg/raster marker height in symbol units"""
    if symbol_layer.fixedAspectRatio() == 0:  # 0 means not 'Lock Aspect Ratio' in GUI
        # defaultAspectRatio = ratio defined in svg/raster file
        return symbol_layer.size() * symbol_layer.defaultAspectRatio()
    else:
        # fixedAspectRatio = user-defined ratio in GUI, calculated by width/height
        return symbol_layer.size() * symbol_layer.fixedAspectRatio()


def get_point_symbol_data(
    symbol_layer: QgsMarkerSymbolLayer, symbol_opacity: float
) -> dict:
    if symbol_layer.layerType() == "RasterMarker":
        symbol_layer_dict = {
            "width": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "height": convert_to_point(
                _get_asset_height(symbol_layer),
                symbol_layer.sizeUnit(),
            ),
            "type": "raster",
            "asset_name": get_asset_name(symbol_layer),
            "offset": [
                convert_to_point(symbol_layer.offset().x(), symbol_layer.offsetUnit()),
                convert_to_point(symbol_layer.offset().y(), symbol_layer.offsetUnit()),
            ],
            "rotation": symbol_layer.angle(),
            "level": symbol_layer.renderingPass(),  # renderingPass means symbolLevels
            # https://github.com/qgis/QGIS/blob/65d40ee0ce59e761ee2de366ca9a963f35adfcfd/src/core/vector/qgsvectorlayerrenderer.cpp#L702
            "opacity": symbol_opacity,
        }

    elif symbol_layer.layerType() == "SvgMarker":
        symbol_layer_dict = {
            "width": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "height": convert_to_point(
                _get_asset_height(symbol_layer),
                symbol_layer.sizeUnit(),
            ),
            "color": to_rgba(symbol_layer.color()),
            "outline_color": to_rgba(symbol_layer.strokeColor()),
            "outline_width": convert_to_point(
                symbol_layer.strokeWidth(), symbol_layer.strokeWidthUnit()
            ),
            "type": "svg",
            "asset_name": get_asset_name(symbol_layer),
            "offset": [
                convert_to_point(symbol_layer.offset().x(), symbol_layer.offsetUnit()),
                convert_to_point(symbol_layer.offset().y(), symbol_layer.offsetUnit()),
            ],
            "rotation": symbol_layer.angle(),
            "level": symbol_layer.renderingPass(),
            "opacity": symbol_opacity,
        }

    elif symbol_layer.layerType() == "SimpleMarker":
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "color": to_rgba(symbol_layer.color()),
            "outline_color": to_rgba(symbol_layer.strokeColor()),
            "outline_width": convert_to_point(
                symbol_layer.strokeWidth(), symbol_layer.strokeWidthUnit()
            ),
            "outline_penstyle": get_penstyle_from(symbol_layer),
            "type": "simple",
            "shape": _get_markershape_from(symbol_layer.shape()),
            "offset": [
                convert_to_point(symbol_layer.offset().x(), symbol_layer.offsetUnit()),
                convert_to_point(symbol_layer.offset().y(), symbol_layer.offsetUnit()),
            ],
            "rotation": symbol_layer.angle(),
            "level": symbol_layer.renderingPass(),
            "opacity": symbol_opacity,
        }

    elif symbol_layer.layerType() == "FontMarker":
        # TODO: implement
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "color": to_rgba(symbol_layer.color()),
            "type": "font",
            "level": symbol_layer.renderingPass(),
            "opacity": symbol_opacity,
        }
    elif symbol_layer.layerType() == "AnimatedMarker":
        # TODO: implement
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "type": "animated",
            "level": symbol_layer.renderingPass(),
            "opacity": symbol_opacity,
        }
    elif symbol_layer.layerType() == "EllipseMarker":
        # TODO: implement
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "color": to_rgba(symbol_layer.color()),
            "type": "ellipse",
            "level": symbol_layer.renderingPass(),
            "opacity": symbol_opacity,
        }
    elif symbol_layer.layerType() == "FilledMarker":
        # TODO: implement
        symbol_layer_dict = {
            "size": convert_to_point(symbol_layer.size(), symbol_layer.sizeUnit()),
            "type": "filled",
            "level": symbol_layer.renderingPass(),
            "opacity": symbol_opacity,
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
            "opacity": symbol_opacity,
        }
    else:
        raise Exception("Unexpected symbol layer type")

    return symbol_layer_dict
