import tkinter as tk
import customtkinter
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from model.multispectral_img_model import MultispectralImgModel

# 定数設定
FONT_TYPE = "meiryo"
WINDOW_SIZE = "1350x750"

class ApplicationView(customtkinter.CTk):
    def __init__(self, controller):
        """アプリケーションのメインウィンドウの初期化"""
        super().__init__()
        self.controller = controller
        self.title('マルチスペクトル画像処理')
        self.geometry(WINDOW_SIZE)
        self.fonts = (FONT_TYPE, 17)
        
        # テーマ設定
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("dark-blue")
        
        self.set_frames()
    
    def set_frames(self):
        """各フレーム（Menu、SpectralImg、VegIndex）の設定と配置"""
        self.menu_frame = MenuFrame(self, width=70, height=700)
        self.menu_frame.grid(row=0, column=0, padx=15, pady=0, sticky="n")
        
        self.spectral_img_frame = SpectralImgFrame(self, width=530, height=750)
        self.spectral_img_frame.grid(row=0, column=1, padx=15, pady=0, sticky="n")
        self.spectral_img_frame.grid_propagate(False)   # フレームを固定サイズに設定
        
        self.veg_index_frame = VegIndexFrame(self, width=530, height=750)
        self.veg_index_frame.grid(row=0, column=2, padx=15, pady=0, sticky="n")
        self.veg_index_frame.grid_propagate(False)   # フレームを固定サイズに設定
    

class MenuFrame(customtkinter.CTkFrame):
    def __init__(self, window, width=None, height=None):
        """メニュー用フレームの初期化とウィジェットの配置"""
        super().__init__(window, width=width, height=height)
        self.controller = window.controller
        self.create_widgets()
    
    def create_widgets(self):
        """フォルダ選択、処理開始、ラジオボタンなどのウィジェットを作成"""
        self.create_button('フォルダ選択', 0, self.controller.select_dir_callback)
        self.label_dir_name = self.create_label('フォルダ名: なし', 1)
        self.create_button('前処理開始', 2, self.controller.start_processing_callback, "#696969")

        # バンド選択ラジオボタン
        self.create_label('表示するバンドを選択', 3, pady=(50, 0))
        self.radio_var_band = tk.IntVar(value=5)
        bands = [("DataCube", 5), ("Green", 1), ("Red", 2), ("Red-Edge", 3), ("NIR", 4)]
        self.create_radio_buttons(bands, self.radio_var_band, 4, self.controller.radbutton_event_select_band)

        # 植生指数選択ラジオボタン
        self.create_label('表示する植生指数を選択', 9, pady=(50, 0))
        self.radio_var_vegindex = tk.IntVar(value=1)
        vegindexs = [("NDVI", 1), ("CI green", 2), ("GNDVI", 3), ("NDRE", 4)]
        self.create_radio_buttons(vegindexs, self.radio_var_vegindex, 10, self.controller.radbutton_event_select_vegindex)

        # 反射率変換実行ボタン
        self.create_button("反射率変換", 14, self.controller.reflectance_event)
        
        
    def create_button(self, text, row, command, color=None):
        """ボタンウィジェットを作成"""
        customtkinter.CTkButton(self, text=text, command=command, fg_color=color).grid(row=row, padx=10, pady=(30, 0), sticky="w")

    def create_label(self, text, row, pady=(10, 0)):
        """ラベルウィジェットを作成"""
        label = customtkinter.CTkLabel(self, text=text)
        label.grid(row=row, padx=10, pady=pady, sticky="w")
        return label
    
    def create_radio_buttons(self, options, variable, start_row, command):
        """ラジオボタンウィジェットを一括で作成"""
        for idx, (text, value) in enumerate(options, start=start_row):
            customtkinter.CTkRadioButton(
                self, text=text, variable=variable, value=value, command=command
            ).grid(row=idx, padx=10, pady=(10, 0), sticky="w")


class SpectralImgFrame(customtkinter.CTkFrame):
    def __init__(self, window=None, width=None, height=None):
        """スペクトル画像表示用フレームの初期化"""
        super().__init__(window, width=width, height=height)
        self.controller = window.controller
        self.canvas = None
        self.image_label = customtkinter.CTkLabel(self, width=512, height=512, text="スペクトル画像",
                                                  fg_color="transparent", font=window.fonts)
        self.image_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 20), sticky="n")
    
    def create_widget_slider(self, img_len):
        """スライダーウィジェットを作成し、スライダーおよびボタンを配置"""
        self.img_len = img_len - 1
        self.slider = customtkinter.CTkSlider(
            self, width=400, from_=0, to=self.img_len, number_of_steps=self.img_len, command=self.controller.slider_event
        )
        self.slider.grid(row=1, column=0, columnspan=3, padx=15, pady=(10, 10), sticky="ew")
        self.slider.set(0)
        
        # 戻るボタンと次へボタンを配置
        self.decrement_button = customtkinter.CTkButton(self, text='back', command=self.controller.decrement_slider, width=100)
        self.decrement_button.grid(row=2, column=0, padx=10, pady=(10, 20), sticky="e")

        self.value_label = customtkinter.CTkLabel(self, text=f"スライダー値:{self.slider.get()}")
        self.value_label.grid(row=2, column=1, padx=5, pady=(10, 20), sticky="ew")

        self.increment_button = customtkinter.CTkButton(self, text='next', command=self.controller.increment_slider, width=100)
        self.increment_button.grid(row=2, column=2, padx=10, pady=(10, 20), sticky="w")
    
    
    
    def display_spectral(self, datacube_list, display_band, slider_value):
        """指定されたバンドのスペクトル画像を表示"""
        datacube = datacube_list[slider_value]
        display_image = datacube if display_band == 5 else datacube[:, :, display_band - 1]
        
        if MultispectralImgModel.is_refconvert == 0:    # 反射率変換前
            img = Image.fromarray(np.uint8(display_image))
        else:                                           # 反射率変換後
            img = (display_image - np.min(display_image)) / (np.max(display_image) - np.min(display_image))
            img = (img * 255).astype(np.uint8)
            img = Image.fromarray(img)
        # display_image = display_image * 255
        # img = Image.fromarray(np.uint8(display_image))
        
        # 画像を表示
        imgtk = customtkinter.CTkImage(light_image=img, dark_image=img, size=(512, 512))
        self.image_label.configure(image=imgtk, text="")
        self.image_label.image = imgtk


class VegIndexFrame(customtkinter.CTkFrame):
    def __init__(self, window=None, width=None, height=None):
        """植生指数表示用フレームの初期化"""
        super().__init__(window, width=width, height=height)
        self.canvas = None
        self.image_label = customtkinter.CTkLabel(self, width=512, height=512, text="植生指数",
                                                  fg_color="transparent", font=window.fonts)
        self.image_label.grid()

    def display_veg_index(self, fig):
        """植生指数のカラーマップを表示"""
        # 既存のラベルやキャンバスを削除して再描画
        if self.image_label:
            self.image_label.destroy()
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid()


'''
ファイル選択ボタン
パネル画像を表示
座標指定
バンドごとの輝度を表示
'''    
# サブウィンドウ
class PanelWindowView(customtkinter.CTkToplevel):
    def __init__(self, master, controller):
        super().__init__()
        self.panel_controller = controller
        self.title('標準化パネルの座標指定')
        self.geometry("650x800")
        self.fonts = (FONT_TYPE, 17)
        
        # 配置設定
        # self.grid_columnconfigure(2, weight=1)  # 下部に余白
        self.set_frame()


    def set_frame(self):
        # パネル画像ファイル選択
        self.select_file_button = self.create_button('ファイル選択', 0, self.panel_controller.select_file_callback)
        self.label_panelfile_name = self.create_label('ファイル名: なし', 1)
        
        self.text_label = self.create_label("パネル部分をドラッグして選択してください", row=2, text_color="orangered")

        # Canvas準備
        self.canvas_panel = tk.Canvas(self, width=512, height=512)
        self.canvas_panel.create_rectangle(0, 0, 513, 513, fill="")
        self.canvas_panel.create_text(250, 250, text="標準化パネル画像", font=self.fonts)
        self.canvas_panel.grid(row=3, column=0, padx=(150,0), pady=(40, 0), sticky='nsew')
        
        # 標準化パネルの放射輝度を表示
        self.bands = ["Green", "Red", "RedEdge", "NIR"]
        self.label_brightness = []
        for row, band in enumerate(self.bands, start=4):
            self.var_name = f"{band}_brightness"
            label = customtkinter.CTkLabel(self, text=f"{band}: None")
            label.grid(row=row, column=0, padx=10, pady=5, sticky='w')
            self.label_brightness.append(label)
            
        # 事後処理
        customtkinter.CTkButton(self, text='パネル範囲決定', command=self.panel_controller.confirm_rect).place(x=280, y=680)
        

    def display_canvas_panel(self, panel_img):
        """Canvasでパネル画像を表示"""
        self.panel_img = panel_img
        # canvasの設定
        self.canvas_panel.create_image(0, 0, image=self.panel_img, anchor=tk.NW)
        self.canvas_panel.image = self.panel_img # 参照を保持
        
        # canvas内のイベントを設定
        self.canvas_panel.bind("<Button1-Motion>", self.panel_controller.rect_drawing)
        self.canvas_panel.bind("<ButtonRelease-1>", self.panel_controller.release_action)
        
        
    def update_brightness_label(self, i, brightness):
        # self.var_name = f"{band}_brightness"
        self.label_brightness[i].configure(text=f"{self.bands[i]}: {brightness}")
        

    def create_button(self, text, row, command, padx=10, pady=(30, 0), column=None, columnspan=None, color=None, rowspan=None, sticky="w"):
        button = customtkinter.CTkButton(self, text=text, command=command, fg_color=color)
        button.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, padx=padx, pady=pady, sticky=sticky)
        return button

    def create_label(self, text, row, pady=(10, 0), sticky="w", width=None, height=None, fg_color=None, text_color=None):
        label = customtkinter.CTkLabel(self, text=text, fg_color=fg_color, text_color=text_color)
        label.grid(row=row, padx=10, pady=pady, sticky=sticky)
        return label

