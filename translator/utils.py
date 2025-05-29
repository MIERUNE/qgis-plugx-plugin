from qgis.PyQt.QtGui import QPainter


def get_blend_mode_string(blend_mode: QPainter.CompositionMode) -> str:
    """translate QgsMapLayer.blendMode() to string for layer.json"""
    return {
        QPainter.CompositionMode.CompositionMode_SourceOver: "normal",
        QPainter.CompositionMode.CompositionMode_Lighten: "lighten",
        QPainter.CompositionMode.CompositionMode_Screen: "screen",
        QPainter.CompositionMode.CompositionMode_ColorDodge: "dodge",
        QPainter.CompositionMode.CompositionMode_Plus: "addition",
        QPainter.CompositionMode.CompositionMode_Darken: "darken",
        QPainter.CompositionMode.CompositionMode_Multiply: "multiply",
        QPainter.CompositionMode.CompositionMode_ColorBurn: "burn",
        QPainter.CompositionMode.CompositionMode_Overlay: "overlay",
        QPainter.CompositionMode.CompositionMode_SoftLight: "soft_light",
        QPainter.CompositionMode.CompositionMode_HardLight: "hard_light",
        QPainter.CompositionMode.CompositionMode_Difference: "difference",
        QPainter.CompositionMode.CompositionMode_Exclusion: "subtract",
    }.get(
        blend_mode,
        "normal",  # fallback
    )
