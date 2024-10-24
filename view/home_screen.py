import tkinter as tk
import customtkinter
from PIL import Image, ImageTk
# from controller.app_controller import ApplicationController

FONT_TYPE = "meiryo"
WINDOW_SIZE = "1350x750"

class ApplicationView(customtkinter.CTk):
    def __init__(self, controller):
        super().__init__()
        
        self.controller = controller
        self.title('マルチスペクトル画像処理')
        self.geometry(WINDOW_SIZE)
        self.fonts = (FONT_TYPE, 15)
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")
        
    def set_frames(self):
        # MenuFrameの設定
        self.menu_frame = MenuFrame(self, width=70, height=700)
        self.menu_frame.grid(row=0, column=0, padx=15, pady=0, sticky="n")
        
        # SpectralImgFrameの設定
        self.spectral_img_frame = SpectralImgFrame(self, width=530, height=750)
        self.spectral_img_frame.grid(row=0, column=1, padx=15, pady=0, sticky="n")
        self.spectral_img_frame.grid_propagate(False)   # フレームを固定
        
        # VegIndexFrameの設定
        self.veg_index_frame = VegIndexFrame(self, width=530, height=750)
        self.veg_index_frame.grid(row=0, column=2, padx=15, pady=0, sticky="n")
        self.veg_index_frame.grid_propagate(False)   # フレームを固定
    

class MenuFrame(customtkinter.CTkFrame):
    def __init__(self, window, width=None, height=None):
        super().__init__(window, width=width, height=height)
        self.controller = window.controller
        self.create_widgets()
    
    def create_widgets(self):
        # フォルダ選択ボタンの配置
        self.button_select_dir = customtkinter.CTkButton(self, text='フォルダ選択',
                                                            command=self.controller.select_dir_callback)
        self.button_select_dir.grid(row=0, padx=10, pady=(15,0), sticky="w")
        
        # フォルダ名表示ラベル
        self.label_dir_name = customtkinter.CTkLabel(self, text='フォルダ名: なし')
        self.label_dir_name.grid(row=1, padx=10, pady=(10,0), sticky="w")
        
        # 前処理開始ボタン
        self.button_start_proccesing = customtkinter.CTkButton(self, text='前処理開始', fg_color="#696969",
                                                            command=self.controller.start_processing_callback)
        self.button_start_proccesing.grid(row=2, padx=10, pady=(15,0), sticky="w")
        
        # 表示バンド - ラジオボタン
        self.label_select_band = customtkinter.CTkLabel(self, text='表示するバンドを選択')
        self.label_select_band.grid(row=3, padx=10, pady=(50,0), sticky="w")

        self.radio_var_band = tk.IntVar(value=0)

        bands = [("DataCube", 5), ("Green", 1), ("Red", 2), ("Red-Edge", 3), ("NIR", 4)]

        for idx, (text, value) in enumerate(bands, start=4):
            radiobutton = customtkinter.CTkRadioButton(
                self,
                text=text,
                command=self.controller.radbutton_event_select_band,
                variable=self.radio_var_band,
                value=value
            )
            radiobutton.grid(row=idx, padx=10, pady=(10, 0), sticky="w")

        
        # 表示 植生指数 - ラジオボタン
        self.label_select_vegindex = customtkinter.CTkLabel(self, text='表示する植生指数を選択')
        self.label_select_vegindex.grid(row=9, padx=10, pady=(50,0), sticky="w")
        
        self.radio_var_vegindex = tk.IntVar(value=0)
        self.radiobutton_select_ndvi = customtkinter.CTkRadioButton(self,
                                        text='NDVI', command=self.controller.radbutton_event_select_vegindex,
                                        variable= self.radio_var_vegindex, value=1)
        self.radiobutton_select_ndvi.grid(row=10, padx=10, pady=(10,0), sticky="w")
        
import numpy as np
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
        
        

class VegIndexFrame(customtkinter.CTkFrame):
    def __init__(self, window=None, width=None, height=None):
        super().__init__(window, width=width, height=height)
        self.image_label = customtkinter.CTkLabel(self, width=512, height=512, text="植生指数", fg_color="transparent")
        self.image_label.grid()
        
    def display_vegIndex(self, ndvi_list):   
        img = Image.fromarray(np.uint8(ndvi_list[5]))
        imgtk = customtkinter.CTkImage(light_image=img, dark_image=img, size=(512, 512))

        self.image_label.configure(image=imgtk, text="")
        self.image_label.image = imgtk