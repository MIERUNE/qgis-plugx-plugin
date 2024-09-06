# QGIS Plugin for PlugX - Design Documents

## 概要 / Overview

日本語
- 出力ファイルの形式
  - ベクター：ESRI Shapefile
  - ラスター：PNG
- 全てのレイヤーは、プロジェクトCRSに変換されて、出力される
- 全てのベクターレイヤーは、シンボルの数だけ出力される
- JSONの全ての座標は、プロジェクトCRSの座標である
- JSONの全てのサイズは、ポイント単位である

English
- Output File Formats:
  - Vector: ESRI Shapefile
  - Raster: PNG
- All layers are converted to the project CRS before being exported.
- Each vector layer is exported for every symbol it contains.
- All coordinates in the exported JSON files are in the project CRS.
- All sizes in the exported JSON files are in points.

## 出力フォルダの構成 / Output folder structure

```planetext
.
├── project.json
├── assets
│   ├── someicon.svg
│   ├── somepic.png
│   ├── someanimation.gif
├── layer_0_0.shp *1
├── layer_0_0.json
├── layer_0_1.shp *2
├── layer_0_1.json
├── layer_2.shp *3
├── layer_2.json
├── layer_5.png
├── layer_5.json
├── layer_n.shp
├── layer_n.json
├── label_1.json
├── label_2.json
└── label_n.json

*1: 
- layer_n_mという命名規則: n=レイヤーの順序、m=シンボルの順序。辞書順で降順＝数字が大きいほど手前。mは省略可能。
- naming convention: layer_n_m, where n is the layer order and m is the symbol order. Sorted in descending order (higher numbers appear in front). m can be omitted.

*2: 
- ベクターレイヤーの場合、シンボルの数だけ出力される.
- *2: For vector layers, the output is generated for each symbol.

*3: 
- データが空のレイヤーはスキップされる（必ずしも連番ではない）
- Layers with no data are skipped (not necessarily sequential numbers).
```


### project.json

```json
{
  "project_name": "tochigi_25k.qgz",
  "crs": "EPSG:32654", // project crs
  "crs_type": "projected", // whether project src is geodestic or not
  "extent": [
    416199.1493,
    4033968.903,
    423674.26,
    4040631.5017
  ],
  "scale": 23031.837306501773,
  "layers": [
    "layer_0", // 出力されたレイヤー一覧: layer_n_mに対応する. List of exported layers corresponds to: layer_n_m.
    "layer_2",
    "layer_5",
    "layer_n"
  ],
  "assets_path": "assets"
}
```

### label_{n}.json

```json
{
  "layer": "P_cities", // layer name
  "labels": [
    {
      "x": 400383.82499371853,
      "y": 4050629.8626693194,
      "rotation": 0.0,
      "text": "サンプルテキスト",
      "font": "Arial",
      "size": 10.0,
      "bold": true,
      "underline": false,
      "text:color": "#323232ff",
      "text:opacity": 100.0,
      "buffer:width": 2.834645669291339, // buffer=縁取り
      "buffer:color": "#fafafaff",
      "buffer:opacity": 100.0
    }
  ]
}
```

### layer_{n}_{m}.json

#### vector layer

```json
{
  "layer": "P_stations", // layer name
  "type": "point", // point | line | polygon
  "opacity": 0.7, // 透過度: 0.0 ~ 1.0
  "blend_mode": "normal", // normal | lighten | screen | dogde | addition | darken | multiply | burn | overlay | soft_light | hard_light | difference | subtract
  "symbols": [
      // symbol typeに応じた辞書からなる配列。別ページにて仕様を定義
      // Array of dictionaries corresponding to the symbol type. Specifications are defined on a separate page.
      {
          "type": "svg",
          "width": 10,
          "height": 5,
          "color": "#ff0000ff",
          "outline_color": "#ff0000ff",
          "outline_width": 2,
          "asset_name": "some.svg",
          "offset": [0.0, 0.0],
          "anchor_x": "center", // 配置のX原点: left | center | right
          "anchor_y": "middle", // 配置のY原点: top | middle | bottom 
          "rotation": 0.0, // degrees, 時計回り
          "level": 0,
          "opacity": 0.5 // 透過度: 0.0 ~ 1.0
      }
  ],
  "usingSymbolLevels": true,
  "legend": "1 - 20000", // 凡例名 (categoricalかグラデーションの場合のみ). Legend name (only for categorical or gradient symbolization)
}
```

#### raster layer

```json
{
  "layer": "imagery",
  "type": "raster",
  "opacity": 0.7,
  "blend_mode": "multiply", // normal | lighten | screen | dogde | addition | darken | multiply | burn | overlay | soft_light | hard_light | difference | subtract
  "extent": [414139.4988, 4033518.258, 421614.6096, 4040087.8327],
}
```

### symbols

[./SYMBOLS.md](./SYMBOLS.md)