import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import glob
import numpy as np
from model.multispectral_img_model import MultispectralImgModel
from model.multispectral_img_model import VegetationIndexVisualizer
from view.home_screen import ApplicationView

INIT_DIR = 'C:/project/multispectral-app'

class ApplicationController:
    def __init__(self):
        self.view = ApplicationView(self)
        self.view.set_frames()
        self.datacube_list = []
        self.ndvi_list = []
        self.image_tmp_list = []
        self.select_dir_path = None
        self.slider_value = 0
        self.display_band = 5
        
    
    def run(self):
        self.view.mainloop()

    def select_dir_callback(self):
        init_dir = INIT_DIR if os.path.exists(INIT_DIR) else os.path.expanduser('~')
        self.select_dir_path = filedialog.askdirectory(initialdir=init_dir)
        
        if self.select_dir_path:
            folder_name = os.path.basename(self.select_dir_path)
            self.view.menu_frame.label_dir_name.configure(text=f"フォルダ名: {folder_name}")

    def start_processing_callback(self):
        '''本番環境では以下のコメントアウトをする。開発中は入力フォルダを以下で定義する'''
        self.select_dir_path = INIT_DIR + '/test'
        self.dir_path = os.path.join(self.select_dir_path, 'frames', '*')
        self.images = glob.glob(self.dir_path)
        self.image_tmp_list = list()
        self.image_tmp_list = [Image.open(img) for img in self.images]
        
        mul_img_model = MultispectralImgModel(self.image_tmp_list)
        image_8bit_list = mul_img_model.bit_convert()
        self.datacube_list = mul_img_model.make_datacube()
        
        self.img_len = len(self.datacube_list)
        self.view.spectral_img_frame.create_widget_slider(self.img_len)

        self.ndvi_list = mul_img_model.calc_NDVI()
        self.veg_index_colormap = VegetationIndexVisualizer(self.ndvi_list)
        
        self.update_display()    
    
    
    def slider_event(self, value):
        new_value = int(value)
        if new_value != self.slider_value:  # スライダー値が変更された場合のみ更新
            self.slider_value = new_value
            self.view.spectral_img_frame.value_label.configure(text=f"スライダー値: {self.slider_value}")
            self.update_display()
    
    
    def increment_slider(self):
        if self.slider_value < self.img_len - 1:
            self.slider_value += 1
            self.view.spectral_img_frame.slider.set(self.slider_value)
            self.view.spectral_img_frame.value_label.configure(text=f"スライダー値: {self.slider_value}")
            self.update_display()
        
            
    def decrement_slider(self):
        if self.slider_value > 0:
            self.slider_value -= 1
            self.view.spectral_img_frame.slider.set(self.slider_value)
            self.view.spectral_img_frame.value_label.configure(text=f"スライダー値: {self.slider_value}")
            self.update_display()


    def radbutton_event_select_band(self):
        self.display_band = self.view.menu_frame.radio_var_band.get()
        self.update_display()


    def radbutton_event_select_vegindex(self):
        self.update_display()
        
    
    def update_display(self):
        self.view.spectral_img_frame.display_spectral(self.datacube_list, self.display_band, self.slider_value)
        fig = self.veg_index_colormap.make_colormap(self.slider_value)
        self.view.veg_index_frame.display_veg_index(fig)
        