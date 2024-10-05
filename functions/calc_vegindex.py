from PIL import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt
import tifffile as tiff
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import ListedColormap, BoundaryNorm

class CalcVegIndex():
    def __init__(self, datacube_list):
        if datacube_list is None:
            self.datacube_list = []
        else:
            self.datacube_list = datacube_list
        self.ndvi_list = []
        
        
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
            
            


# def calcula_and_save_NDVImap():
#     datacube_files = os.path.join(datacube_path, '*')
#     datacubes = glob.glob(datacube_files)
    
#     colors = [
#         "white", "#C0C0FF", "#A0A0FF", "#8080FF", "blue",
#         "#0080FF", "#00A0FF", "#00C0FF", "yellow", "#80FF00",
#         "#C0FF00", "green", "#00FF80", "orangered", "red", "darkred"
#         ]
#     bounds = [0.01, 
#             0.06, 0.11, 0.16, 0.21, 
#             0.26, 0.31, 0.36, 0.41,
#             0.46, 0.51, 0.56, 0.61,
#             0.66, 0.71, 1.00]
#     cmap = ListedColormap(colors)
#     norm = BoundaryNorm(bounds, cmap.N)
    
#     for datacube in datacubes:
#         img = tiff.imread(datacube)
#         img = img.astype(np.float32)
#         # NaNの値を0に変換
#         img[np.isnan(img)] = 0
#         # 非負値に変換
#         img[img < 1.] = 1.
#         ndvi = (img[:, :, 3] - img[:, :, 1]) / (img[:, :, 3] + img[:, :, 1])
        
#         plt.imshow(ndvi, cmap='viridis')
#         plt.colorbar(shrink=0.5)

#         # グラフをファイルに保存
#         filename = os.path.splitext(os.path.basename(datacube))[0] + '_ndvi.png'
#         save_path = os.path.join(save_ndvi_path, filename)
#         plt.savefig(save_path)
#         plt.close()  # メモリの使用量を抑えるためにグラフを閉じる

#         plt.imshow(ndvi, cmap=cmap, norm=norm)
#         plt.colorbar(ticks=bounds, shrink=0.5)
        
#         # グラフをファイルに保存
#         save_path = os.path.join(save_ndvi_path2, filename)
#         plt.savefig(save_path)
#         plt.close()  # メモリの使用量を抑えるためにグラフを閉じる
