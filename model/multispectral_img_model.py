from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

class MultispectralImgModel:
    
    def __init__(self, imgs):
        # 初期化：画像リストとインデックスのリストを定義
        self.image_tmp_list = imgs
        self.image_8bit_list = []
        self.ndvi_list = []
        self.gndvi_list = []
        self.ndre_list = []
        self.cigreen_list = []
        
        # 各種処理を順に実行
        self.convert_to_8bit()
        self.create_datacube()
        self.calculate_indices()
        
        # カラーマップ表示の初期設定
        self.init_figure()
    
    
    def convert_to_8bit(self):
        """画像を8ビットに変換して保存"""
        self.image_8bit_list = [img.convert('L') for img in self.image_tmp_list]
    
    
    def create_datacube(self):
        """データキューブ（4つのバンドを持つ3次元配列）を作成"""
        band_height = int(self.image_8bit_list[0].size[1] / 4)
        self.datacube_list = []
        
        for img in self.image_8bit_list:
            img_array = np.array(img)
            # 4つのバンドに分割
            bands = [img_array[j * band_height:(j + 1) * band_height, :] for j in range(4)]
            datacube = np.stack(bands, axis=-1).astype(np.float32)
            # データクレンジング
            datacube[np.isnan(datacube)] = 0
            datacube[datacube < 1.] = 1.
            self.datacube_list.append(datacube)
        return self.datacube_list
    
    
    def calculate_indices(self):
        """植生指数を各バンドで計算"""
        # NDVI, CIgreen, GNDVI, NDREを計算
        self.ndvi_list = [(dc[:, :, 3] - dc[:, :, 1]) / (dc[:, :, 3] + dc[:, :, 1]) for dc in self.datacube_list]
        self.cigreen_list = [(dc[:, :, 3] / dc[:, :, 0]) - 1 for dc in self.datacube_list]
        self.gndvi_list = [(dc[:, :, 3] - dc[:, :, 0]) / (dc[:, :, 3] + dc[:, :, 0]) for dc in self.datacube_list]
        self.ndre_list = [(dc[:, :, 3] - dc[:, :, 2]) / (dc[:, :, 3] + dc[:, :, 2]) for dc in self.datacube_list]
    
    
    def init_figure(self):
        """初期カラーマップ表示を設定"""
        self.fig, self.ax = plt.subplots(figsize=(7, 7), dpi=100)
        # 初期表示はNDVIの最初の画像を表示
        self.im = self.ax.imshow(self.ndvi_list[0], cmap='viridis', vmin=-1, vmax=1)
        self.ax.set_aspect('equal', adjustable='box')
        self.cbar = self.fig.colorbar(self.im, ax=self.ax, shrink=1)
        self.cbar.set_ticks(np.arange(-1, 1.1, 0.2))
    
    
    def make_colormap(self, slider_value, vegindex_num):
        """選択された植生指数とスライダーの値に基づいてカラーマップを更新"""
        # 植生指数とカラーマップの辞書
        vegindex_dict = {1: self.ndvi_list, 2: self.cigreen_list, 3: self.gndvi_list, 4: self.ndre_list}
        cmap_dict = {1: 'viridis', 2: 'viridis', 3: 'YlGn', 4: 'seismic'}
        
        # 選択された植生指数に応じてデータとカラーマップを更新
        selected_index = vegindex_dict.get(vegindex_num)
        cmap = cmap_dict.get(vegindex_num)
        
        # 表示する画像とカラーマップを設定
        self.im.set_data(selected_index[slider_value])
        self.im.set_cmap(cmap)
        
        # CIgreenの場合、範囲を-1から10に設定
        if vegindex_num == 2:
            self.set_colorbar_range(-1, 10, tick_interval=1)
        else:
            self.set_colorbar_range(-1, 1, tick_interval=0.2)
        
        return self.fig
    
    
    def set_colorbar_range(self, vmin, vmax, tick_interval):
        """カラーバーの範囲と目盛りを設定"""
        self.im.set_clim(vmin, vmax)
        self.cbar.set_ticks(np.arange(vmin, vmax + tick_interval, tick_interval))
