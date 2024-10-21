import os
import tkinter as tk
from tkinter import filedialog
from model.preprocessing_images import PreprocessingImages
from model.calc_vegindex import CalcVegIndex
from view.home_screen import ApplicationView

INIT_DIR = 'C:/project/multispectral-app'

class ApplicationController:
    def __init__(self):
        self.view = ApplicationView(self)
        self.view.set_frames()
        self.datacube_list = []
        self.ndvi_list = []
        self.select_dir_path = None
    
    def run(self):
        self.view.mainloop()

    def select_dir_callback(self):
        init_dir = INIT_DIR if os.path.exists(INIT_DIR) else os.path.expanduser('~')
        self.select_dir_path = filedialog.askdirectory(initialdir=init_dir)
        
        if self.select_dir_path:
            folder_name = os.path.basename(self.select_dir_path)
            self.view.menu_frame.label_dir_name.configure(text=f"フォルダ名: {folder_name}")

    def start_processing_callback(self):
        preprocessor = PreprocessingImages(self.select_dir_path)
        image_8bit_list = preprocessor.bit_convert()
        self.datacube_list = preprocessor.make_datacube()

        vegindex_processor = CalcVegIndex(self.datacube_list)
        self.ndvi_list = vegindex_processor.calc_NDVI()

    def radbutton_event_select_band(self):
        display_band_index = self.view.menu_frame.radio_var_band.get()
        self.view.spectral_img_frame.display_spectral(self.datacube_list, display_band_index)

    def radbutton_event_select_vegindex(self):
        self.view.veg_index_frame.display_vegIndex(self.ndvi_list)