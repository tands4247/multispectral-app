from view.home_screen import ApplicationView
from controller.app_controller import ApplicationController
import customtkinter

if __name__ == '__main__':
    # root = customtkinter.CTk()
    
    controller = ApplicationController()
    # view = ApplicationView(controller)
    # view.grid(row=0, column=0, sticky="nsew")
    # view.set_frames()

    # アプリケーションの実行
    controller.run()
    