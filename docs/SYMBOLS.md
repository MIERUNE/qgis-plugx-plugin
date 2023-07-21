# Symbol Specification

- QGIS Symbol -> JSON への変換仕様を定義します
- QGISの1レイヤーには1個以上のSymbolLayerが含まれます
- 通常は1SymbolLayer=1Symbolですが、一部特殊なSymbolLayerは複数のSymbolを含むことがあります（例：FilledMarker）
- ひとつのSymbolLayerは、ひとつのシェープファイルに対応します

## Point

### simple (SimpleMarker)

![](./imgs/simplemarker.png)

```json
{
  "type": "simple",
  "size": 10,
  "color": "#ff0000ff",
  "outline_color": "#ff0000ff",
  "outline_width": 2,
  "shape": "circle", //square | diamond | pentagon | hexagon | triangle | equilateraltriangle | star | arrow | circle | cross | crossfill | cross2 | line | arrowhead | arrowheadfilled | semicircle | thirdcircle | quartercircle | quartersquare | halfsquare | diagonalhalfsquare | righthalftriangle | lefthalftriangle | trapezoid | parallelogramleft | parallelogramright | shield | octagon | decagon | squarecorners | squarerounded | diamondstar | heart | halfarc | thirdarc | quarterarc | asteriskfill
  "offset": [
                0.0,
                0.0
            ],
  "rotation": 0.0, //degrees
  "level": 0
}
```

### svg (SvgMarker)

```json
{
  "type": "svg",
  "size": 10,
  "color": "#ff0000ff",
  "outline_color": "#ff0000ff",
  "outline_width": 2,
  "asset_path": "assets/symbol_svg/some.svg",
  "offset": [
                0.0,
                0.0
            ],
  "rotation": 180.0, //degrees
  "level": 0
}
```

### raster (RasterMarker)

```json
{
  "type": "raster",
  "size": 10,
  "asset_path": "assets/symbol_raster/some.png",
  "offset": [
                0.0,
                0.0
            ],
  "rotation": 0.0, // degrees
  "level": 1
}
```

### font (FontMarker)

```json
未実装: type=simpleと同様
```

### animated (AnimatedMarker)

```json
未実装: type=simpleと同様
```

### filled (FilledMarker)

```json
未実装: type=simpleと同様
```

### mask (MaskMarker)

```json
未実装: type=simpleと同様
```

### ellipse(Ellipse)

```json
未実装: type=simpleと同様
```

## Line

### simple (SimpleLine)

![](./imgs/penstyle.png)

```json
{
  "type": "simple",
  "color": "#ff0000ff",
  "penstyle": {
    "stroke": "solid", // nopen | solid | dash | dot | dashdot | dashdotdot | customdash
    "cap": "square", // flat | square | round
    "join": "bevel" // miter | bevel | round
  },
  "width": 2,
  "level": 1
}
```

### marker (MarkerLine)

```json
{
  "type": "marker",
  "markers" [
    // point-svg の配列
    {
      "type": "svg",
      "size": 10,
      "color": "#ff0000ff",
      "outline_color": "#ff0000ff",
      "outline_width": 2,
      "asset_path": "assets/svg/some.svg",
      "level": 0
    }
  ]
  "interval": 2,
  "level": 1
}
```

### interpolated (InterpolatedLine)

```json
未実装: type=simpleと同様
```

### hashed (HashLine)

```json
未実装: type=simpleと同様
```

### raster (RasterLine)

```json
未実装: type=simpleと同様
```

### arrow(ArrowLine)

```json
未実装: type=simpleと同様
```

### lineburst(Lineburst)

```json
未実装: type=simpleと同様
```

## Polygon

### simple (SimpleFill)

![](./imgs/simplefill.png)

```json
{
  "type": "simple",
  "color": "#ff0000ff",
  "brushstyle": "solid", // nobrush | solid | dense1 | dense2 | dense3 | dense4 | dense5 | dense6 | dense7 | horizontal | vertical | cross | backwarddiagonal | forwarddiagonal | crossingdiagonal
  "outline_color": "#ff0000ff",
  "outline_width": 2,
  "level": 1
}
```

### centroid (CentroidFill)

```json
未実装: type=simpleと同様
```

### pointpattern (PointPattern)

```json
未実装: type=simpleと同様
```

### randommarker (RandomMarker)’

```json
未実装: type=simpleと同様
```

### linepattern (LinePattern)

```json
未実装: type=simpleと同様
```

### svg (SVGFill)

```json
未実装: type=simpleと同様
```

### gradient (GradientFill)

```json
未実装: type=simpleと同様
```

### shapeburst (ShapeburstFill)

```json
未実装: type=simpleと同様
```

## Hybrid

undefined

## 未分類のシンボル

```
💡 VectorField, Geometry Generatorは対応しない
Outlineは未定
```

### Point

- Vector Field Marker
- Geometry Generator

### Line

- Geometry Generator

### Polygon

- GeometryGenerator
- outline
  - Arrow
  - Hashed
  - Interpolated
  - Lineburst
  - Marker
  - Raster
  - Simple