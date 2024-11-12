import customtkinter
import os
import sys
from tkinter import Tk


dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

class Index (customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("500x200")
        self.resizable (False, False)
        self.title("Confirmation")
        self.callback = None

        self.label = customtkinter.CTkLabel(self, text="Are you sure you want to display all the results in the table? \r\n The studio might crash if you proceed.")
        self.label.pack(padx=20, pady=20)

        self.btn = customtkinter.CTkButton(master=self, text="PROCEED", fg_color="#C15252", bg_color="transparent", hover_color="#F26B6B", corner_radius=20)
        self.btn.bind("<Button-1>", self.__runCallback)
        self.btn.pack(fill="both", padx=20)

        self.centerWindow(self)
        self.attributes('-topmost', True)
        self.focus ()
    
    def setCallback(self, callback = None, param = None):
        if not callback == None:
            self.callback       =   callback
            self.callbackParam  =   param

        return self

    def __runCallback (self, e):
        if not self.callback == None:
            if not self.callbackParam == None:
                self.callback (self.callbackParam, self)
            else:
                self.callback (self)
        return self
    
    def centerWindow(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

  