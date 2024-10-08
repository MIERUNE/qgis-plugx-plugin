# シンボル仕様 / Symbol Specification
日本語
- QGIS Symbol -> JSON への変換仕様を定義します
- QGISの1レイヤーには1個以上のSymbolLayerが含まれます
- 通常は1SymbolLayer=1Symbolですが、一部特殊なSymbolLayerは複数のSymbolを含むことがあります（例：FilledMarker）
- ひとつのSymbolLayerは、ひとつのシェープファイルに対応します

English
- Defines the conversion rules from QGIS Symbols to JSON.
- Each QGIS layer contains one or more SymbolLayers.
- Usually, 1 SymbolLayer = 1 Symbol, but some special SymbolLayers may include multiple Symbols (e.g., FilledMarker).
- Each SymbolLayer corresponds to one shapefile.

## Point

### simple (SimpleMarker)

![](./imgs/marker_simple.png)

```json
{
  "type": "simple",
  "size": 10,
  "color": "#ff0000ff",
  "outline_color": "#ff0000ff",
  "outline_width": 2,
  "outline_penstyle": {
    "stroke": "solid", // nopen | solid | dash | dot | dashdot | dashdotdot | customdash
    "join": "bevel", // miter | bevel | round
    "cap": "square" // flat | square | round
  },
  "shape": "circle", //square | diamond | pentagon | hexagon | triangle | equilateraltriangle | star | arrow | circle | cross | crossfill | cross2 | line | arrowhead | arrowheadfilled | semicircle | thirdcircle | quartercircle | quartersquare | halfsquare | diagonalhalfsquare | righthalftriangle | lefthalftriangle | trapezoid | parallelogramleft | parallelogramright | shield | octagon | decagon | squarecorners | squarerounded | diamondstar | heart | halfarc | thirdarc | quarterarc | asteriskfill
  "offset": [0.0, 0.0],
  "anchor_x": "center", // 配置のX原点: left | center | right
  "anchor_y": "middle", // 配置のY原点: top | middle | bottom 
  "rotation": 0.0, //degrees, clockwise 時計回り
  "level": 0,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### svg (SvgMarker)

![](./imgs/marker_svg.png)

```json
{
  "type": "svg",
  "width": 10,
  "height": 5,
  "color": "#ff0000ff", // nullable
  "outline_color": "#ff0000ff", // nullable
  "outline_width": 2, // nullable
  "asset_name": "some.svg",
  "offset": [0.0, 0.0],
  "anchor_x": "center", // 配置のX原点: left | center | right
  "anchor_y": "middle", // 配置のY原点: top | middle | bottom 
  "rotation": 180.0, //degrees, clockwise 時計回り
  "level": 0,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### raster (RasterMarker)

![](./imgs/marker_raster.png)

```json
{
  "type": "raster",
  "width": 10,
  "height": 5,
  "asset_name": "some.png",
  "offset": [0.0, 0.0],
  "anchor_x": "center", // 配置のX原点: left | center | right
  "anchor_y": "middle", // 配置のY原点: top | middle | bottom 
  "rotation": 0.0, // degrees, clockwise 時計回り
  "level": 1,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### font (FontMarker)

![](./imgs/marker_font.png)

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "font",
  "size": 10,
  "color": "#ff0000ff",
  "level": 0,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### animated (AnimatedMarker)

![](./imgs/marker_animated.gif)

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "animated",
  "size": 10,
  "level": 0,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### filled (FilledMarker)

![](./imgs/marker_filled.png) 

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "filled",
  "size": 10,
  "level": 0,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### ellipse (Ellipse)

![](./imgs/marker_ellipse.png)

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "ellipse",
  "size": 10,
  "color": "#ff0000ff",
  "level": 0,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### mask (MaskMarker)

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "unsupported",
  "size": 10,
  "color": "#ff0000ff",
  "level": 0,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```


## Line

### simple (SimpleLine)

![](./imgs/penstyle.png)

```json
{
  "type": "simple",
  "color": "#ff0000ff",
  "penstyle": {
    "stroke": "solid", // nopen | solid | dash
    "cap": "square", // flat | square | round
    "join": "bevel", // miter | bevel | round
    "dash_pattern": [2.0, 1.0, 4.0, 1.0], 
    // stroke=dashのときのみ [実線(長さ), 間隔、実線、間隔...]
    // For stroke=dash only: [solid line length, gap, solid line, gap...]
    // 例 / e.g.:
    // [2, 1]       -> --  --  --  -- ...
    // [4, 2]       -> ----  ----  ---- ...
    // [2, 1, 4, 2] -> -- ----  -- ----  -- ...
  },
  "width": 2,
  "level": 1,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### marker (MarkerLine)

![](./imgs/line_marker.png)

```json
{
  "type": "marker",
  "interval": 2, // 点間の距離
  "level": 1,
  "opacity": 1.0,
  "markers": [
    // 任意の個数・種別のtype=markerの配列。これらが重なってひとつのシンボルになりライン上に表示される（後が上）。
    // A list of markers (type=marker) that can be of any number and type. 
    // These markers stack on top of each other to create one symbol on the line (the last one is on top).
    {
      "type": "svg",
      "size": 10,
      "color": "#ff0000ff",
      "outline_color": "#ff0000ff",
      "outline_width": 2,
      "asset_name": "some.svg",
      "level": 0,
      "opacity": 1.0
    },
    {
      "type": "simple",
      "size": 10,
      "color": "#ff0000ff",
      "outline_color": "#ff0000ff",
      "outline_width": 2,
      "outline_penstyle": {
        "stroke": "solid",
        "join": "bevel",
        "cap": "square"
      },
      "shape": "circle",
      "offset": [0.0, 0.0],
      "anchor_x": "center",
      "anchor_y": "middle",
      "rotation": 0.0,
      "level": 0,
      "opacity": 1.0
    }
  ]
}
```

### interpolated (InterpolatedLine)

![](./imgs/line_interpolated.png)

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "interpolated",
  "color": "#ff0000ff",
  "width": 2,
  "level": 1,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### hashed (HashLine)

![](./imgs/line_hashed.png)

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "hash",
  "level": 1,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### raster (RasterLine)

![](./imgs/line_raster.png)

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "raster",
  "width": 2,
  "level": 1,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### arrow (ArrowLine)

![](./imgs/line_arrow.png)

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "arrow",
  "width": 2,
  "level": 1,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### lineburst (Lineburst)

![](./imgs/lineburst.png)

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "lineburst",
  "width": 2,
  "level": 1,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

## Polygon

### simple (SimpleFill)

![](./imgs/fill_simple.png)

```json
{
  "type": "simple",
  "color": "#ff0000ff",
  "brushstyle": "solid", // nobrush | solid | dense1 | dense2 | dense3 | dense4 | dense5 | dense6 | dense7 | horizontal | vertical | cross | backwarddiagonal | forwarddiagonal | crossingdiagonal
  "outline_color": "#ff0000ff",
  "outline_width": 2,
  "outline_penstyle": {
    "stroke": "solid", // nopen | solid | dash | dot | dashdot | dashdotdot | customdash
    "join": "bevel" // miter | bevel | round
  },
  "level": 1,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### centroid (CentroidFill)

![](./imgs/fill_centroid.png)

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "centroid",
  "level": 1,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### pointpattern (PointPattern)

![](./imgs/fill_pointpattern.png)

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "pointpattern",
  "level": 1,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### randommarker (RandomMarker)’

![](./imgs/fill_randommarker.png)

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "randommarker",
  "level": 1,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### linepattern (LinePattern)

![](./imgs/fill_linepattern.png)

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "linepattern",
  "level": 1,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### svg (SVGFill)

![](./imgs/fill_svg.png)

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "svg",
  "color": "#ff0000ff",
  "outline_color": "#ff0000ff",
  "outline_width": 2,
  "level": 1,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### raster (RasterFill)

![](./imgs/fill_raster.png)

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "raster",
  "color": "#ff0000ff",
  "outline_color": "#ff0000ff",
  "outline_width": 2,
  "level": 1,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### gradient (GradientFill)

![](./imgs/fill_gradient.png)

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "gradient",
  "level": 1,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

### shapeburst (ShapeburstFill)

![](./imgs/fill_shapeburst.png)

```json
# Not implemented / 未実装: basic attributes only
{
  "type": "shapeburst",
  "level": 1,
  "opacity": 1.0 // 透過度: 0.0 ~ 1.0
}
```

## 未実装のシンボル / Not supported symbols

### Polygon

- outline
  - Arrow
  - Hashed
  - Interpolated
  - Lineburst
  - Marker
  - Raster
  - Simple

## 対応予定のないシンボル / Symbols that are not planned to be supported

以下のシンボルは、対応予定がありません。`type=unsupported`として出力されます。

The following symbols are not planned to be implemented and are exported as `type=unsupported`.

```json
{
  "type": "unsupported",
  "color": "#000000",
  "level": 0,
  "opacity": 1.0
}
```

### Point

- Mask Marker
- Vector Field Marker
- Geometry Generator

### Line

- Geometry Generator

### Polygon

- GeometryGenerator
