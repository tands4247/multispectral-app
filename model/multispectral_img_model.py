from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

class MultispectralImgModel:
    
    def __init__(self, imgs):
        self.image_tmp_list = imgs
        self.image_8bit_list = []
        self.ndvi_list = []
        self.gndvi_list = []
        self.ndre_list = []
        
        self.bit_convert()
        self.make_datacube()
        self.calc_NDVI()
        self.calc_GNDVI()
        self.calc_NDRE()
        
        # 初期表示のカラーマップ
        self.fig, self.ax = plt.subplots(figsize=(7, 7), dpi=100)
        self.im = self.ax.imshow(self.ndvi_list[0], cmap='viridis', vmin=-1, vmax=1)
        self.ax.set_aspect('equal', adjustable='box')  # アスペクト比を維持
        self.cbar = self.fig.colorbar(self.im, ax=self.ax, shrink=1)
        self.cbar.set_ticks(np.arange(-1, 1.1, 0.2))
    
    
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
            datacube = np.stack(bands, axis=-1).astype(np.float32)
            datacube[np.isnan(datacube)] = 0  # NaNを0に置換
            datacube[datacube < 1.] = 1.  # 非負値に変換
            self.datacube_list.append(datacube)

        return self.datacube_list
    
    
    def calc_NDVI(self):
        # NDVIを計算
        for datacube in self.datacube_list:
            ndvi = np.array((datacube[:, :, 3] - datacube[:, :, 1]) / (datacube[:, :, 3] + datacube[:, :, 1]))
            self.ndvi_list.append(ndvi)
        return self.ndvi_list
    
    
    def calc_GNDVI(self):
        for datacube in self.datacube_list:
            gndvi = np.array((datacube[:, :, 3] - datacube[:, :, 0]) / (datacube[:, :, 3] + datacube[:, :, 0]))
            self.gndvi_list.append(gndvi)
        return self.gndvi_list
    
    
    def calc_NDRE(self):
        for datacube in self.datacube_list:
            ndre = np.array((datacube[:, :, 3] - datacube[:, :, 2]) / (datacube[:, :, 3] + datacube[:, :, 2]))
            self.ndre_list.append(ndre)
        return self.ndre_list
            
    
    def make_colormap(self, slider_value, vegindex_num):
        vegindex_dict = {
            1: self.ndvi_list,
            2: self.gndvi_list,
            3: self.ndre_list
        }
        cmap_dict = { 
            1: 'viridis',
            2: 'YlGn',
            3: 'seismic'
        }
        self.vegindex = vegindex_dict.get(vegindex_num)
        self.im.set_data(self.vegindex[slider_value])
        self.im.set_cmap(cmap=cmap_dict.get(vegindex_num))
        return self.fig
    