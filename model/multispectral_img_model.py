from PIL import Image
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
            # ndvi = np.array(ndvi)
            self.ndvi_list.append(ndvi)
            
        return self.ndvi_list    
    
        

class VegetationIndexVisualizer:
    def __init__(self, vegindex_list):
        self.vegindex_list = np.array(vegindex_list)
        self.fig, self.ax = plt.subplots(figsize=(7, 7), dpi=100)
        
        # 初期表示のカラーマップ
        self.im = self.ax.imshow(self.vegindex_list[0], cmap='viridis', vmin=-1, vmax=1)
        self.ax.set_aspect('equal', adjustable='box')  # アスペクト比を維持

        # カラーバーを一度だけ追加
        self.cbar = self.fig.colorbar(self.im, ax=self.ax, shrink=1)
        self.cbar.set_ticks(np.arange(-1, 1.1, 0.2))


    def make_colormap(self, slider_value):
        self.im.set_data(self.vegindex_list[slider_value])
        return self.fig