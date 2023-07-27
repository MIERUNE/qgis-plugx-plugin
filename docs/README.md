# QGIS Plugin for PlugX - Design Documents

## 概要

- 出力ファイルの形式
  - ベクター：ESRI Shapefile
  - ラスター：PNG
- 全てのレイヤーは、プロジェクトCRSに変換されて、出力される
- 全てのベクターレイヤーは、シンボルの数だけ出力される
- JSONの全ての座標は、プロジェクトCRSの座標である
- JSONの全てのサイズは、ポイント単位である

## 出力フォルダの構成

```planetext
.
├── project.json
├── assets
│   ├── svg
│   │   ├── 0.svg
│   │   ├── 1.svg
│   │   └── n.svg
│   └── raster
│       ├── 0.png
│       ├── 1.gif
│       └── n.jpg
├── layer_0_0.shp # layer_n_mという命名規則: n=レイヤーの順序、m=シンボルの順序。辞書順で降順＝数字が大きいほど手前。mは省略可能。
├── layer_0_0.json
├── layer_0_1.shp # ベクターレイヤーの場合、シンボルの数だけ出力される
├── layer_0_1.json
├── layer_2.shp # データが空のレイヤーはスキップされる（必ずしも連番ではない）
├── layer_2.json
├── layer_5.png
├── layer_5.json
├── layer_n.shp
├── layer_n.json
├── label_1.json
├── label_2.json
└── label_n.json
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
    "layer_0", // 出力されたレイヤー一覧: layer_n_mに対応する
    "layer_2",
    "layer_5",
    "layer_n"
  ]
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
      {
          "type": "svg",
          "size": 10,
          "color": "#ff0000ff",
          "outline_color": "#ff0000ff",
          "outline_width": 2,
          "asset_path": "assets/svg/some.svg",
          "offset": [0.0, 0.0],
          "rotation": 0.0, // degrees, 時計回り
          "level": 0,
          "opacity": 0.5 // 透過度: 0.0 ~ 1.0
      }
  ],
  "usingSymbolLevels": true,
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