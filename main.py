import shutil
import cv2
from lxml import etree
from xml.etree import ElementTree
import os
from glob import glob
from tqdm import tqdm
import random
import string
import re
import json
from concurrent.futures import ThreadPoolExecutor




# 変換元 - Conversion source
annotated_dir_path = "/content/plane/" # **/*export.jsonをglobで取得します。
annotated_test_dir_path = "/content/plane_test/"

# 変換先 - Destination
export_default_path = '/content/data-set/'

# インデックスを取得するために設定する - set to get the index
LABEL_ARR = []




def set_anntation_dir():
    if not os.path.exists(export_default_path):
        os.mkdir(export_default_path)

    if not os.path.exists(f"{export_default_path}images/"):
        os.mkdir(f"{export_default_path}images/")
    if not os.path.exists(f"{export_default_path}labels/"):
        os.mkdir(f"{export_default_path}labels/")
        
    if not os.path.exists(export_default_path + 'test/'):
        os.mkdir(export_default_path + 'test/')
    if not os.path.exists(export_default_path + 'test/images/'):
        os.mkdir(export_default_path + 'test/images/')
    if not os.path.exists(export_default_path + 'test/labels/'):
        os.mkdir(export_default_path + 'test/labels/')
        

def create_random_name(n=30):
    """
    ランダムな英数字を作成 - Create random alphanumeric characters
    """
    randlst = [random.choice(string.ascii_letters + string.digits)
               for i in range(n)]
    return ''.join(randlst)


def data_padding():
    """
    情報を追加する - add info
    """
    json_paths = glob(
            f"{annotated_dir_path}**/*export.json", recursive=True)
    json_paths += glob(f"{annotated_test_dir_path}**/*export.json",
                       recursive=True)
    print('グレースケール/ネガポジを追加')

    # ランダムでグレースケール・ネガポジの画像を生成する
    for json_path in json_paths:
        tmp_dir_path = os.path.dirname(json_path)

        with open(json_path, 'r') as f:
            json_data = json.load(f)

        tmp_assets_dict = json_data['assets'].copy()

        for asset_val in list(tmp_assets_dict.values()):
            img_name = asset_val['asset']['name']
            created_id = create_random_name()
            ram_img = random.randint(0, 2)
            plane_img_path = f'{tmp_dir_path}/{img_name}'

            try:
                if ram_img == 1:  # グレースケール
                    addimg = cv2.imread(
                        plane_img_path, cv2.IMREAD_GRAYSCALE)
                    create_img_name = f'gray_{img_name}'
                elif ram_img == 2:  # ネガポジ
                    im = cv2.imread(plane_img_path)
                    addimg = cv2.bitwise_not(im)
                    create_img_name = f'ng_{img_name}'
                else:
                    continue
                cv2.imwrite(f'{tmp_dir_path}/{create_img_name}', addimg)

                json_data['assets'][created_id] = dict(asset_val)
                json_data['assets'][created_id]['asset'] = dict(asset_val['asset'])
                json_data['assets'][created_id]['asset']['name'] = create_img_name
                json_data['assets'][created_id]['asset']['id'] = created_id

            except BaseException as e:
                print('エラー', e)

        with open(json_path, 'w', encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
            print('json write success', json_path)


def vottJson_to_yolo():
    set_anntation_dir()
    json_paths = glob(f"{annotated_dir_path}**/*export.json", recursive=True)
    for json_path in json_paths:
        tmp_dir_path = os.path.dirname(json_path)
        with open(json_path, 'r') as f:
            json_data = json.load(f)

        for index, asset_val in enumerate(list(json_data['assets'].values())):
            img_name = asset_val['asset']['name']
            img_name_without_ext = os.path.splitext(img_name)[0]

            if index % 8 == 0:  # テストデータを追加する
                shutil.copyfile(
                    f'{tmp_dir_path}/{img_name}', f'{export_default_path}test/images/{img_name}'
                )
                with open(f'{export_default_path}test/labels/{img_name_without_ext}.txt', mode='w') as f:
                    """
                    TODO 下に同じコードが記載してあります。
                    """
                    size_x = asset_val['asset']['size']['width']
                    size_y = asset_val['asset']['size']['height']
                    save_text = ''
                    for region in asset_val['regions']:
                        for tag in region['tags']:
                            label_index = LABEL_ARR.index(tag)
                            save_text += f'{label_index}'
                            for point in region['points']:
                                x = point['x'] / size_x
                                y = point['y'] / size_y
                                save_text += f' {x} {y}'
                            save_text += '\n'
                    f.write(save_text)
                continue

            shutil.copyfile(
                f'{tmp_dir_path}/{img_name}', f'{export_default_path}images/{img_name}'
            )

            with open(f'{export_default_path}labels/{img_name_without_ext}.txt', mode='w') as f:
                """
                TODO 全く同じコードが記載してあります。
                """
                size_x = asset_val['asset']['size']['width']
                size_y = asset_val['asset']['size']['height']
                save_text = ''
                for region in asset_val['regions']:
                    for tag in region['tags']:
                        label_index = LABEL_ARR.index(tag)
                        save_text += f'{label_index}'
                        for point in region['points']:
                            x = point['x'] / size_x
                            y = point['y'] / size_y
                            save_text += f' {x} {y}'
                        save_text += '\n'
                f.write(save_text)
