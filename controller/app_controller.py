import os
import tkinter as tk
from tkinter import filedialog
import customtkinter
from PIL import Image, ImageTk
import glob
import numpy as np
from model.multispectral_img_model import MultispectralImgModel
from model.multispectral_img_model import Visualizer
from view.home_screen import ApplicationView
from view.home_screen import PanelWindowView


# 初期ディレクトリ設定
INIT_DIR = 'C:/project/multispectral-app'

class ApplicationController:
    def __init__(self):
        """コントローラの初期化"""
        # Viewのインスタンス生成と初期設定
        self.view = ApplicationView(self)
        
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
        self.visualizer = Visualizer(self.mul_img_model)
        
        # スライダーと表示の設定
        self.img_len = self.mul_img_model.get_datacube_len()
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
        self.view.spectral_img_frame.display_spectral(self.mul_img_model.datacube_list, self.display_band, self.slider_value)
        
        # 選択された植生指数のカラーマップ更新
        fig = self.visualizer.make_colormap(self.slider_value, self.display_vegindex)
        self.view.veg_index_frame.display_veg_index(fig)
    
    
    def reflectance_event(self):
        """パネルウィンドウの生成とモデルの渡し"""
        if self.mul_img_model:
            PanelWindowController(self)
        else:
            print("Error: モデルが生成されていません。最初に画像を処理してください。")


class PanelWindowController:
    def __init__(self, master):
        # サブwindowインスタンス生成
        self.panel_view = PanelWindowView(master.view, self)
        self.mul_img_model = master.mul_img_model
        self.app_controller = master
        
        """以下テスト用"""
        self.select_panelfile_path = INIT_DIR + "/test/frames/e0001_frame_ms_00113_.tif"
        self.open_panel_img()
        
        
    # 標準化パネル画像を選択
    def select_file_callback(self):
        """ファイル選択ダイアログを開き、選択されたファイルを表示"""
        init_dir = INIT_DIR if os.path.exists(INIT_DIR) else os.path.expanduser('~')
        self.select_panelfile_path = filedialog.askopenfilename(initialdir=init_dir)
        
        if self.select_panelfile_path:
            self.panelfile_name = os.path.basename(self.select_panelfile_path)
            self.panel_view.label_panelfile_name.configure(text=f"ファイル名: {self.panelfile_name}")
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
                self.panel_img_crop = self.panel_img.crop((0, 0, 512, 512))
            
            self.imgtk = ImageTk.PhotoImage(self.panel_img_crop)
            
            # パネルビューに画像を表示
            self.panel_view.display_canvas_panel(self.imgtk)
            
        except Exception as e:
            print(f"An unexpected error occurred while opening the image: {e}")
            

    def rect_drawing(self, event):
        """ マウスクリックで四角形の開始点を指定、ドラッグで拡大描画 """
        # もし開始点が未設定の場合（最初のクリック）に設定
        if not hasattr(self, 'start_x') or not hasattr(self, 'start_y'):
            self.start_x, self.start_y = event.x, event.y

        # 現在のカーソル位置に基づいて終了点の座標を取得（領域外チェック付き）
        end_x = max(0, min(self.panel_img_crop.width, event.x))
        end_y = max(0, min(self.panel_img_crop.height, event.y))

        # 矩形がまだ存在しなければ描画
        if not self.panel_view.canvas_panel.find_withtag("rect1"):
            self.panel_view.canvas_panel.create_rectangle(
                self.start_x, self.start_y, end_x, end_y,
                outline="red", tag="rect1"
            )
        else:
            # 既存の矩形の右下隅を更新
            self.panel_view.canvas_panel.coords("rect1", self.start_x, self.start_y, end_x, end_y)

    def release_action(self, event):
        """ マウスボタンを離したときに最終的な座標を取得 """
        start_x, start_y, end_x, end_y = self.panel_view.canvas_panel.coords("rect1")
        self.rectangle_area = [start_x, start_y, end_x, end_y]

        # パネルの各バンドの放射輝度を受け取る
        self.panel_brightness_list = self.mul_img_model.get_panel_brightness(self.panel_img, self.rectangle_area)
        # 放射輝度ラベル更新
        bands = ["Green", "Red", "RedEdge", "NIR"]
        for i, value in enumerate(self.panel_brightness_list):
            self.panel_view.update_brightness_label(i, value)
            
        
        # 開始点をリセット
        del self.start_x
        del self.start_y
        
    def confirm_rect(self):
        if self.panel_brightness_list:
            self.panel_view.destroy()
            self.mul_img_model.convert_to_reflectance()
            self.app_controller.update_display()
            tk.messagebox.showinfo('メッセージ', '反射率に変換しました  ')
