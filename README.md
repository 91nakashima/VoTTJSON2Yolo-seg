# VoTTJSON2Yolo-seg

Vott JSONからYOLOv7でのセグメンテーションで使用できる形に変換する関数

```bash
git clone https://github.com/91nakashima/VoTTJSON2Yolo-seg.git
cd VoTTJSON2Yolo-seg
```

## 各種設定

```python
# 変換元 - Conversion source
annotated_dir_path = "/content/plane/" # **/*export.jsonをglobで取得します。
annotated_test_dir_path = "/content/plane_test/"

# 変換先 - Destination
export_default_path = '/content/data-set/'

# インデックスを取得するために設定する - set to get the index
LABEL_ARR = []
```

```bash
python main.py
```

