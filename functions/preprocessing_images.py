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
# from matplotlib.colors import LinearSegmentedColormap
# from matplotlib.colors import ListedColormap, BoundaryNor

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
        # datacube化
        self.images_tif = []
        self.data_cube_list = []
        self.band_height = int(tiff.imread(self.images[0]).shape[0] / 4) # 512
        i = 1
        
        # tiff形式で読み込み
        self.tif_images = []
        for img in self.images:
            self.tif_images.append(tiff.imread(img))
        
        for img in self.tif_images:
            self.bands = [img[j*self.band_height:(j+1)*self.band_height, :] for j in range(4)]
            self.data_cube_list.append(np.stack(self.bands, axis=-1))
        
        return self.data_cube_list
        
# def make_datacube_and_division():
#     path_8_files = os.path.join(path_8, '*')
#     files_8 = glob.glob(path_8_files)

#     # datacube化
#     images_tif = []
#     band_height = int(tiff.imread(files_8[0]).shape[0] / 4) # 512
#     i = 1
#     for file in files_8:
#         tif_image = tiff.imread(file)
#         bands = [tif_image[j*band_height:(j+1)*band_height, :] for j in range(4)]
        
#         img_name = os.path.basename(file)
#         # データキューブ保存
#         data_cube = np.stack(bands, axis=-1)
#         save_datacube_path = os.path.join(datacube_path, img_name)
#         tiff.imwrite(save_datacube_path, data_cube)
        
#         # 分割保存
#         tiff.imwrite(os.path.join(path_normal_division_G, img_name), bands[0])
#         tiff.imwrite(os.path.join(path_normal_division_R, img_name), bands[1])
#         tiff.imwrite(os.path.join(path_normal_division_Re, img_name), bands[2])
#         tiff.imwrite(os.path.join(path_normal_division_NIR, img_name), bands[3])


# if __name__ == '__main__':
#     make_directory()
#     bit_convert()
#     make_datacube_and_division()
#     calcula_and_save_NDVImap()
    