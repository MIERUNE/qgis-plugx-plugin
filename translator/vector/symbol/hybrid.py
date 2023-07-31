from qgis.core import QgsSymbolLayer


def get_hybrid_symbol_data(symbol_layer: QgsSymbolLayer, symbol_opacity: float) -> dict:
    # never to be supported...
    symbol_layer_dict = {
        "type": "unsupported",
        "color": "#000000",
        "level": symbol_layer.renderingPass(),
        "opacity": symbol_opacity
        # "geometry": symbol_layer.geometryExpression(),
    }

    return symbol_layer_dict
