from PIL import Image
import numpy as np
import cv2
import numpy as np
import matplotlib.pyplot as plt
import tifffile as tiff
import glob
import os

class MultispectralImgModel():
    
    def __init__(self, imgs):
        self.image_8bit_list = []
        self.ndvi_list = []
        self.image_tmp_list = imgs
    
    
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
    
    
    def calc_NDVI(self):
        for self.datacube in self.datacube_list:
            img = self.datacube.astype(np.float32)
            # NaNの値を0に変換
            img[np.isnan(img)] = 0
            # 非負値に変換
            img[img < 1.] = 1.
            img_ndvi = (img[:, :, 3] - img[:, :, 1]) / (img[:, :, 3] + img[:, :, 1])
            
            # 0～255にスケーリング。cv2のカラーマップに対応させるために
            img_ndvi = np.clip(img_ndvi, 0, 1)
            img_ndvi = (img_ndvi * 255).astype(np.uint8)
            
            self.ndvi_list.append(cv2.applyColorMap(img_ndvi, cv2.COLORMAP_RAINBOW))
        return self.ndvi_list
