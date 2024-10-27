from PIL import Image
import numpy as np
import cv2
import matplotlib.pyplot as plt

class MultispectralImgModel:
    
    def __init__(self, imgs):
        self.image_tmp_list = imgs
        self.image_8bit_list = []
        self.ndvi_list = []
    
    def bit_convert(self):
        # 8ビット画像に変換
        self.image_8bit_list = [img.convert('L') for img in self.image_tmp_list]
        return self.image_8bit_list
    
    def make_datacube(self):
        # データキューブの作成
        band_height = int(self.image_8bit_list[0].size[1] / 4)
        self.datacube_list = []
        
        for img in self.image_8bit_list:
            img_array = np.array(img)  # 画像をnumpy配列に変換
            bands = [img_array[j * band_height:(j + 1) * band_height, :] for j in range(4)]
            self.datacube_list.append(np.stack(bands, axis=-1))

        return self.datacube_list
    
    def calc_NDVI(self):
        # NDVIを計算
        for datacube in self.datacube_list:
            img = datacube.astype(np.float32)
            img[np.isnan(img)] = 0  # NaNを0に置換
            img[img < 1.] = 1.  # 非負値に変換
            ndvi = (img[:, :, 3] - img[:, :, 1]) / (img[:, :, 3] + img[:, :, 1])
            self.ndvi_list.append(ndvi)
            
            return self.ndvi_list    
    
        
# class VegetationIndexVisualizer:
#     def __init__(self, vegindex_list):
#         self.vegindex_list = vegindex_list
    
    