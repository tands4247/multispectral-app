from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import copy

class MultispectralImgModel:
    is_refconvert = 0
    def __init__(self, imgs):
        # 初期化：画像リストとインデックスのリストを定義
        self.image_tmp_list = imgs
        self.image_8bit_list = self.convert_to_8bit()
        self.datacube_list = self.create_datacube()
        self.datacube_list_copy = copy.deepcopy(self.datacube_list)
        self.batch_process()        
    
    def batch_process(self):
        '''一括処理 - 放射輝度値と反射率とで2回実行'''
        
        # 植生指数の計算
        self.ndvi_list = self.calculate_ndvi()
        self.gndvi_list = self.calculate_gndvi()
        self.ndre_list = self.calculate_ndre()
        self.cigreen_list = self.calculate_cigreen()
    
    
    def convert_to_8bit(self):
        """画像を8ビットに変換して保存"""
        return [img.convert('L') for img in self.image_tmp_list]
    
    
    def create_datacube(self):
        """データキューブ（4つのバンドを持つ3次元配列）を作成"""
        band_height = int(self.image_8bit_list[0].size[1] / 4)
        datacube_list = []
        
        for img in self.image_8bit_list:
            img_array = np.array(img)
            # 4つのバンドに分割
            bands = [img_array[j * band_height:(j + 1) * band_height, :] for j in range(4)]
            datacube = np.stack(bands, axis=-1).astype(np.float32)
            # データクレンジング
            datacube[np.isnan(datacube)] = 0
            datacube[datacube < 1.] = 1.
            datacube_list.append(datacube)
        return datacube_list
    
    
    def calculate_ndvi(self):
        '''NDVI計算'''
        return [(dc[:, :, 3] - dc[:, :, 1]) / (dc[:, :, 3] + dc[:, :, 1]) for dc in self.datacube_list]
    
    def calculate_gndvi(self):
        '''GNDVI計算'''
        return [(dc[:, :, 3] - dc[:, :, 0]) / (dc[:, :, 3] + dc[:, :, 0]) for dc in self.datacube_list]
    
    def calculate_ndre(self):
        '''NDRE計算'''
        return [(dc[:, :, 3] - dc[:, :, 2]) / (dc[:, :, 3] + dc[:, :, 2]) for dc in self.datacube_list]
    
    def calculate_cigreen(self):
        '''CIgreen計算'''
        return [(dc[:, :, 3] / dc[:, :, 0]) - 1 for dc in self.datacube_list]
    
    def get_datacube_len(self):
        return len(self.datacube_list)
    
    def get_panel_brightness(self, panel_img, rectangle_area):
        self.panel_img = panel_img
        self.rectangle_area = rectangle_area
        self.panel_brightness = []
        
        # 原点座標と高さ、幅を取得
        self.start_x = self.rectangle_area[0]
        self.start_y = self.rectangle_area[1]
        self.end_x = self.rectangle_area[2]
        self.end_y = self.rectangle_area[3]
        
        for i in range(4):
            self.panel_band = self.panel_img.crop((self.start_x, self.start_y+(i*512), self.end_x, self.end_y+(i*512)))
            self.panel_brightness.append(round(np.mean(self.panel_band), 2))
        return self.panel_brightness
    
    
    def convert_to_reflectance(self):
        '''全てのdatacube画像を放射輝度から反射率へ変換する'''
        self.datacube_list = copy.deepcopy(self.datacube_list_copy)
        ref_list = []   # 反射率変換されたdatacube画像を一時的に格納するリスト
        for dc in self.datacube_list:
            for i, value in enumerate(self.panel_brightness):
                dc[:,:,i] = np.array((dc[:,:,i] / value) * 0.18)
            ref_list.append(dc)
        MultispectralImgModel.is_refconvert = 1 # 反射率変換フラグを1に
        self.datacube_list = ref_list   # 上書き
        
        # 植生指数の再算出
        self.batch_process()


class Visualizer:
    def __init__(self, mul_img_model):
        self.mul_img_model = mul_img_model
        self.cmap_init_figure()
        
        
    def cmap_init_figure(self):
        """初期カラーマップ表示を設定"""
        self.cmap_fig, self.cmap_ax = plt.subplots(figsize=(7, 7), dpi=100)
        # 初期表示はNDVIの最初の画像を表示
        self.im = self.cmap_ax.imshow(self.mul_img_model.ndvi_list[0], cmap='jet', vmin=-1, vmax=1)
        self.cmap_ax.set_aspect('equal', adjustable='box')
        self.cbar = self.cmap_fig.colorbar(self.im, ax=self.cmap_ax, shrink=1)
        self.cbar.set_ticks(np.arange(-1, 1.1, 0.2))
        
    
    def make_colormap(self, slider_value, vegindex_num):
        """選択された植生指数とスライダーの値に基づいてカラーマップを更新"""
        # 植生指数とカラーマップの辞書
        vegindex_dict = {1: self.mul_img_model.ndvi_list,
                         2: self.mul_img_model.cigreen_list,
                         3: self.mul_img_model.gndvi_list,
                         4: self.mul_img_model.ndre_list}
        cmap_dict = {1: 'jet', 2: 'viridis', 3: 'YlGn', 4: 'seismic'}
        
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
        
        return self.cmap_fig
    
    
    def set_colorbar_range(self, vmin, vmax, tick_interval):
        """カラーバーの範囲と目盛りを設定"""
        self.im.set_clim(vmin, vmax)
        self.cbar.set_ticks(np.arange(vmin, vmax + tick_interval, tick_interval))
