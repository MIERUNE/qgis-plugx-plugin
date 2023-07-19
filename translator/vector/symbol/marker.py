from qgis.core import QgsSymbolLayer


from utils import convert_to_point
from translator.vector.symbol.utils import get_asset_name


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
            "color": symbol_layer.color().name(),
            "outline_color": symbol_layer.strokeColor().name(),
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
            "color": symbol_layer.color().name(),
            "outline_color": symbol_layer.strokeColor().name(),
            "outline_width": convert_to_point(
                symbol_layer.strokeWidth(), symbol_layer.strokeWidthUnit()
            ),
            "type": "simple",
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
            "color": symbol_layer.color().name(),
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
            "color": symbol_layer.color().name(),
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
