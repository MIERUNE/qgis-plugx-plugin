from PyQt5.QtGui import QPainter


def get_blend_mode_string(blend_mode: QPainter.CompositionMode) -> str:
    """translate QgsMapLayer.blendMode() to string for layer.json"""
    return {
        QPainter.CompositionMode_SourceOver: "normal",
        QPainter.CompositionMode_Lighten: "lighten",
        QPainter.CompositionMode_Screen: "screen",
        QPainter.CompositionMode_ColorDodge: "dodge",
        QPainter.CompositionMode_Plus: "addition",
        QPainter.CompositionMode_Darken: "darken",
        QPainter.CompositionMode_Multiply: "multiply",
        QPainter.CompositionMode_ColorBurn: "burn",
        QPainter.CompositionMode_Overlay: "overlay",
        QPainter.CompositionMode_SoftLight: "soft_light",
        QPainter.CompositionMode_HardLight: "hard_light",
        QPainter.CompositionMode_Difference: "difference",
        QPainter.CompositionMode_Exclusion: "subtract",
    }.get(
        blend_mode, "normal"
    )  # fallback
