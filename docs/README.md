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
├── layer_0_0.shp # layer_n_mという命名規則: n=レイヤーの順序、m=シンボルの順序。辞書順で降順＝数字が大きいほど手前。
├── layer_0_0.json
├── layer_0_1.shp
├── layer_0_1.json
├── layer_1.shp
├── layer_1.json
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
    "layer_0",
    "layer_1",
    "layer_2",
    "layer_3"
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

```json
{
  "layer": "P_stations", // layer name
  "type": "point", // point | line | polygon | raster
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
          "level": 0
      }
  ],
	"usingSymbolLevels": true
}
```

### symbols

[./SYMBOLS.md](./SYMBOLS.md)