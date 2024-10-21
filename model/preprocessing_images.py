'''
要件
    受け取った分析対象のフォルダパスを読み込む
    8bit変換とデータキューブへ変換したものをそれぞれリスト化


処理内容
    make_directory : 格納するフォルダ作成
    bit_convert : 8bitへ変換. metadataを削除して表示できるように
    make_datacube_and_division : 4つのバンドを分割し保存、重ね合わせてデータキューブ化して保存
    calcula_and_save_NDVImap : NDVIを計算し、NDVIマップを保存
'''

'''
例外処理について検討
'''

from PIL import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt
import tifffile as tiff
import glob
import os

class PreprocessingImages():
    def __init__(self, dir_path):
        self.dir_path = os.path.join(dir_path, 'frames', '*')
        self.images = glob.glob(self.dir_path)
        self.image_tmp_list = []
        self.image_8bit_list = []
        for img in self.images:
            self.image_tmp_list.append(Image.open(img))
    
    def bit_convert(self):
        for img in self.image_tmp_list:
            self.image_8bit_list.append(img.convert('L'))
            
        return self.image_8bit_list
            
    def make_datacube(self):
        
        self.images_tif = []
        self.datacube_list = []
        self.band_height = int(self.image_8bit_list[0].size[1] / 4)
        i = 1

        # PILを使用してtiff形式で読み込み
        self.tif_images = []
        for img in self.image_8bit_list:
            self.tif_images.append(np.array(img))  # 画像をnumpy配列に変換

        for img in self.tif_images:
            self.bands = [img[j*self.band_height:(j+1)*self.band_height, :] for j in range(4)]
            self.datacube_list.append(np.stack(self.bands, axis=-1))

        return self.datacube_list
