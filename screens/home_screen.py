import tkinter as tk
from tkinter import filedialog
import customtkinter
import os
import numpy as np
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import tifffile as tiff
# 作成モジュール
from functions.preprocessing_images import PreprocessingImages

FONT_TYPE = "meiryo"
WINDOW_SIZE = "1270x750"
INIT_DIR = 'C:/project/multispectral-app'

class Application(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        self.title('マルチスペクトル画像処理')
        self.geometry(WINDOW_SIZE)
        self.fonts = (FONT_TYPE, 15)
        customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green
        
        # MenuFrameの設定
        self.menu_frame = MenuFrame(self, width=70, height=700)
        self.menu_frame.grid(row=0, column=0, padx=20, pady=0, sticky="n")
        
        # SpectralImgFrameの設定
        self.spectral_img_frame = SpectralImgFrame(self, width=550, height=750)
        self.spectral_img_frame.grid(row=0, column=1, padx=40, pady=0, sticky="n")
        self.spectral_img_frame.grid_propagate(False)   # フレームを固定


class MenuFrame(customtkinter.CTkFrame):
    def __init__(self, window=None, width=None, height=None):
        super().__init__(window, width=width, height=height)
        self.create_widgets()
    
    def create_widgets(self):
        # フォルダ選択ボタンの配置
        self.button_select_dir = customtkinter.CTkButton(self, text='フォルダ選択',
                                                            command=self.select_dir_callback)
        self.button_select_dir.grid(row=0, padx=10, pady=(15,0), sticky="w")
        
        # フォルダ名表示ラベル
        self.label_dir_name = customtkinter.CTkLabel(self, text='フォルダ名: なし')
        self.label_dir_name.grid(row=1, padx=10, pady=(10,0), sticky="w")
        
        # 前処理開始ボタン
        self.button_start_proccesing = customtkinter.CTkButton(self, text='前処理開始', fg_color="#696969",
                                                            command=self.start_processing_callback)
        self.button_start_proccesing.grid(row=2, padx=10, pady=(15,0), sticky="w")
        
        # 表示バンド - ラジオボタン
        self.label_select_band = customtkinter.CTkLabel(self, text='表示するバンドを選択')
        self.label_select_band.grid(row=3, padx=10, pady=(50,0), sticky="w")
        
        self.radio_var = tk.IntVar(value=0)
        self.radiobutton_select_band1 = customtkinter.CTkRadioButton(self,
                                        text='DataCube', command=self.radiobutton_event,
                                        variable= self.radio_var, value=5)
        self.radiobutton_select_band1.grid(row=4, padx=10, pady=(10,0), sticky="w")
        
        self.radiobutton_select_band2 = customtkinter.CTkRadioButton(self,
                                        text='Green', command=self.radiobutton_event,
                                        variable= self.radio_var, value=1)
        self.radiobutton_select_band2.grid(row=5, padx=10, pady=(10,0), sticky="w")
        
        self.radiobutton_select_band3 = customtkinter.CTkRadioButton(self,
                                        text='Red', command=self.radiobutton_event,
                                        variable= self.radio_var, value=2)
        self.radiobutton_select_band3.grid(row=6, padx=10, pady=(10,0), sticky="w")
        
        self.radiobutton_select_band4 = customtkinter.CTkRadioButton(self,
                                        text='Red-Edge', command=self.radiobutton_event,
                                        variable= self.radio_var, value=3)
        self.radiobutton_select_band4.grid(row=7, padx=10, pady=(10,0), sticky="w")
        
        self.radiobutton_select_band5 = customtkinter.CTkRadioButton(self,
                                        text='NIR', command=self.radiobutton_event,
                                        variable= self.radio_var, value=4)
        self.radiobutton_select_band5.grid(row=8, padx=10, pady=(10,0), sticky="w")
    
    
    # フォルダ選択のコールバック
    def select_dir_callback(self):
        init_dir = INIT_DIR if os.path.exists(INIT_DIR) else os.path.expanduser('~')
        # フォルダ選択のダイアログを開く
        self.select_dir_path = tk.filedialog.askdirectory(initialdir=init_dir)
        
        if self.select_dir_path:
            folder_name = os.path.basename(self.select_dir_path)
            self.label_dir_name.configure(text=f"フォルダ名: {folder_name}")
    
    # 前処理開始のコールバック
    def start_processing_callback(self):        
        preprocessor = PreprocessingImages(self.select_dir_path)
        image_8bit_list = preprocessor.bit_convert()
        self.datacube_list = preprocessor.make_datacube()

        
    # ラジオボタンのイベント
    def radiobutton_event(self):
        self.display_band_index = self.radio_var.get()
        self.master.spectral_img_frame.display_spectral(self.datacube_list, self.display_band_index)
        
        
        
class SpectralImgFrame(customtkinter.CTkFrame):
    def __init__(self, window=None, width=None, height=None):
        super().__init__(window, width=width, height=height)
        self.image_label = customtkinter.CTkLabel(self, width=512, height=512, text="スペクトル画像", fg_color="transparent")
        self.image_label.grid()
        
    def display_spectral(self, datacube_list, display_band_index):
        datacube = datacube_list[5]
        if display_band_index != 5:
            display_image = datacube[:, :, display_band_index - 1]
        else:
            display_image = datacube
                
        img = Image.fromarray(np.uint8(display_image))
        imgtk = customtkinter.CTkImage(light_image=img, dark_image=img, size=(512, 512))

        self.image_label.configure(image=imgtk, text="")
        self.image_label.image = imgtk
        
        