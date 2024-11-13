import os
import tkinter as tk
from tkinter import filedialog
import customtkinter
from PIL import Image, ImageTk
import glob
import numpy as np
from model.multispectral_img_model import MultispectralImgModel
from view.home_screen import ApplicationView
from view.home_screen import PanelSubView

# 初期ディレクトリ設定
INIT_DIR = 'C:/project/multispectral-app'

class ApplicationController:
    def __init__(self):
        """コントローラの初期化"""
        # Viewのインスタンス生成と初期設定
        self.view = ApplicationView(self)
        self.view.set_frames()
        
        # 属性の初期化
        self.datacube_list = []
        self.image_tmp_list = []
        self.select_dir_path = None
        self.slider_value = 0
        self.display_band = 5  # デフォルトの表示バンド
        self.display_vegindex = 1  # デフォルトの植生指数
        self.img_len = 0  # 画像の枚数を保持

    def run(self):
        """アプリケーションを起動"""
        self.view.mainloop()


    # 前処理時に実行
    def select_dir_callback(self):
        """フォルダ選択ダイアログを開き、選択されたフォルダを表示"""
        init_dir = INIT_DIR if os.path.exists(INIT_DIR) else os.path.expanduser('~')
        self.select_dir_path = filedialog.askdirectory(initialdir=init_dir)
        
        if self.select_dir_path:
            folder_name = os.path.basename(self.select_dir_path)
            self.view.menu_frame.label_dir_name.configure(text=f"フォルダ名: {folder_name}")


    def start_processing_callback(self):
        """画像処理を開始するコールバック"""
        # 本番環境用にフォルダパスを取得
        self.select_dir_path = self.select_dir_path or INIT_DIR + '/test'
        
        # フォルダ内の画像をロード
        self.load_images()
        
        # モデルの作成とデータキューブ生成
        self.mul_img_model = MultispectralImgModel(self.image_tmp_list)
        self.datacube_list = self.mul_img_model.create_datacube()
        
        # スライダーと表示の設定
        self.img_len = len(self.datacube_list)
        self.view.spectral_img_frame.create_widget_slider(self.img_len)
        self.update_display()

    def load_images(self):
        """指定ディレクトリ内の画像を読み込む"""
        dir_path = os.path.join(self.select_dir_path, 'frames', '*')
        self.images = glob.glob(dir_path)
        self.image_tmp_list = [Image.open(img) for img in self.images]

    def slider_event(self, value):
        """スライダーの値が変更されたときのイベントハンドラ"""
        new_value = int(value)
        if new_value != self.slider_value:  # スライダーの値が変更された場合のみ更新
            self.slider_value = new_value
            self.view.spectral_img_frame.value_label.configure(text=f"スライダー値: {self.slider_value}")
            self.update_display()

    def increment_slider(self):
        """スライダーの値を1増加させて表示を更新"""
        if self.slider_value < self.img_len - 1:
            self.slider_value += 1
            self.update_slider_display()

    def decrement_slider(self):
        """スライダーの値を1減少させて表示を更新"""
        if self.slider_value > 0:
            self.slider_value -= 1
            self.update_slider_display()

    def update_slider_display(self):
        """スライダーの値とラベルを更新し、表示を更新"""
        self.view.spectral_img_frame.slider.set(self.slider_value)
        self.view.spectral_img_frame.value_label.configure(text=f"スライダー値: {self.slider_value}")
        self.update_display()

    def radbutton_event_select_band(self):
        """ラジオボタンで選択されたバンドを更新し、表示を更新"""
        self.display_band = self.view.menu_frame.radio_var_band.get()
        self.update_display()

    def radbutton_event_select_vegindex(self):
        """ラジオボタンで選択された植生指数を更新し、表示を更新"""
        self.display_vegindex = self.view.menu_frame.radio_var_vegindex.get()
        self.update_display()

    def update_display(self):
        """現在の設定に基づいて画像とカラーマップを更新"""
        # バンド画像の表示更新
        self.view.spectral_img_frame.display_spectral(self.datacube_list, self.display_band, self.slider_value)
        
        # 選択された植生指数のカラーマップ更新
        fig = self.mul_img_model.make_colormap(self.slider_value, self.display_vegindex)
        self.view.veg_index_frame.display_veg_index(fig)


    def reflectance_conversion(self):
        # サブwindowインスタンス生成
        self.sub_view = PanelSubView(self.view, self)
        self.sub_view.set_frame()
        
        
    # 標準化パネル画像を選択
    def select_file_callback(self):
        """ファイル選択ダイアログを開き、選択されたファイルを表示"""
        init_dir = INIT_DIR if os.path.exists(INIT_DIR) else os.path.expanduser('~')
        self.select_panelfile_path = filedialog.askopenfilename(initialdir=init_dir)
        
        if self.select_panelfile_path:
            self.panelfile_name = os.path.basename(self.select_panelfile_path)
            self.sub_view.label_panelfile_name.configure(text=f"ファイル名: {self.panelfile_name}")
            self.open_panel_img()
    
    def open_panel_img(self):
        try:
            # ファイルパスが正しいかチェック
            if not hasattr(self, 'select_panelfile_path') or not self.select_panelfile_path:
                print("Error: No file path specified.")
                return

            # 画像の読み込み
            if not os.path.exists(self.select_panelfile_path):
                print(f"Error: The file {self.select_panelfile_path} does not exist.")
                return

            # 画像の読み込み
            self.panel_img = Image.open(self.select_panelfile_path)
            panel_size = self.panel_img.size

            if panel_size == (512, 2048):
                self.panel_img = self.panel_img.crop((0, 0, 512, 512))
            print(f"Image loaded successfully with size: {self.panel_img.size}")
            
            # ImageをCTkImageに変換
            # self.imgtk = customtkinter.CTkImage(self.panel_img, size=self.panel_img.size)
            
            self.imgtk = ImageTk.PhotoImage(self.panel_img)
            
            # パネルビューに画像を表示
            self.sub_view.display_canvas_panel(self.imgtk)
            
        except Exception as e:
            print(f"An unexpected error occurred while opening the image: {e}")
            
