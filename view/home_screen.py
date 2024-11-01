import tkinter as tk
import customtkinter
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        self.create_button('フォルダ選択', 0, self.controller.select_dir_callback)
        self.label_dir_name = self.create_label('フォルダ名: なし', 1)
        self.create_button('前処理開始', 2, self.controller.start_processing_callback, "#696969")

        # バンド選択ラジオボタン
        self.create_label('表示するバンドを選択', 3, pady=(50,0))
        self.radio_var_band = tk.IntVar(value=5)
        bands = [("DataCube", 5), ("Green", 1), ("Red", 2), ("Red-Edge", 3), ("NIR", 4)]
        for idx, (text, value) in enumerate(bands, start=4):
            customtkinter.CTkRadioButton(self, text=text, variable=self.radio_var_band,
                                         value=value, command=self.controller.radbutton_event_select_band).grid(row=idx, padx=10, pady=(10, 0), sticky="w")

        # 植生指数ラジオボタン
        self.create_label('表示する植生指数を選択', 9, pady=(50,0))
        self.radio_var_vegindex = tk.IntVar(value=1)
        customtkinter.CTkRadioButton(self, text='NDVI', variable=self.radio_var_vegindex,
                                     value=1, command=self.controller.radbutton_event_select_vegindex).grid(row=10, padx=10, pady=(10,0), sticky="w")

    def create_button(self, text, row, command, color=None):
        customtkinter.CTkButton(self, text=text, command=command, fg_color=color).grid(row=row, padx=10, pady=(15,0), sticky="w")

    def create_label(self, text, row, pady=(10, 0)):
        label = customtkinter.CTkLabel(self, text=text)
        label.grid(row=row, padx=10, pady=pady, sticky="w")
        return label

        

class SpectralImgFrame(customtkinter.CTkFrame):
    def __init__(self, window=None, width=None, height=None):
        super().__init__(window, width=width, height=height)
        self.image_label = customtkinter.CTkLabel(self, width=512, height=512, text="スペクトル画像", fg_color="transparent")
        self.image_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 20), sticky="n")
        self.controller = window.controller
    
        
    # スライダーの追加
    def create_widget_slider(self, img_len):
        self.img_len = img_len - 1
        self.slider = customtkinter.CTkSlider(self, width=400, from_=0, to=self.img_len, 
                                              number_of_steps=self.img_len, command=self.controller.slider_event)
        self.slider.grid(row=1, column=0, columnspan=3, padx=15, pady=(10, 10), sticky="ew")
        self.slider.set(0)
        
        # 戻るボタンと次へボタン
        self.decrement_button = customtkinter.CTkButton(self, text='back', command=self.controller.decrement_slider, width=100)
        self.decrement_button.grid(row=2, column=0, padx=10, pady=(10, 20), sticky="e")

        self.value_label = customtkinter.CTkLabel(self, text=f"スライダー値:{self.slider.get()}")
        self.value_label.grid(row=2, column=1, padx=5, pady=(10, 20), sticky="ew")

        self.increment_button = customtkinter.CTkButton(self, text='next', command=self.controller.increment_slider, width=100)
        self.increment_button.grid(row=2, column=2, padx=10, pady=(10, 20), sticky="w")
        
        
    def increment_slider(self):
        current_value = self.slider.get()
        if current_value < self.img_len:  # スライダーの最大値を超えないようにする
            self.slider.set(current_value + 1)
        self.value_label.configure(text=f"スライダー値: {self.slider_value}")
            
    def decrement_slider(self):
        current_value = self.slider.get()
        if current_value > 0:  # スライダーの最大値を超えないようにする
            self.slider.set(current_value - 1)
        self.value_label.configure(text=f"スライダー値: {self.slider_value}")


    
    def display_spectral(self, datacube_list, display_band, slider_value):
        datacube = datacube_list[slider_value]
        display_image = datacube if display_band == 5 else datacube[:, :, display_band - 1]
        img = Image.fromarray(np.uint8(display_image))
        imgtk = customtkinter.CTkImage(light_image=img, dark_image=img, size=(512, 512))
        self.image_label.configure(image=imgtk, text="")
        self.image_label.image = imgtk
        
        

class VegIndexFrame(customtkinter.CTkFrame):
    def __init__(self, window=None, width=None, height=None):
        super().__init__(window, width=width, height=height)
        self.canvas = None
        self.image_label = customtkinter.CTkLabel(self, width=512, height=512, text="植生指数", fg_color="transparent")
        self.image_label.grid()
    
    
    def display_veg_index(self, fig):
        if self.image_label:
            self.image_label.destroy()
        
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid()