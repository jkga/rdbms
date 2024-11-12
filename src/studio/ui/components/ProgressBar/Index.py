import customtkinter
import os
import sys
import threading
from tkinter import Tk


dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

class Index:
    def __init__(self):
        self.progressbar        =   None
        self.componentThread    =   None
        self.targetComponent    =   None
        self.progressbar        =   None

    def start (self):
        self.progressFrame = customtkinter.CTkFrame(master=self.targetComponent, bg_color="transparent", fg_color="transparent", height=2)
        self.progressFrame.grid_rowconfigure(0, weight=1)
        self.progressFrame.grid_columnconfigure (0, weight=1)
        self.progressFrame.grid(row=0, column=0, padx="0", pady="0", sticky="nsew")

        self.progressbar = customtkinter.CTkProgressBar(master=self.progressFrame, progress_color="#333333")
        self.progressbar.grid(row=0, column=0, sticky="nsew")
        self.progressbar.start ()
        return self
    
    def stop (self):
        try:
            self.progressFrame.destroy ()
        except Exception as e:
            print(e)

        return self
    
    def setTargetComponent (self, target):
        self.targetComponent = target
        return self

    def getThread (self):
        if self.progressbar != None:
            return self.progressbar
        elif self.componentThread and not self.componentThread.is_alive():
            return None
        else:
            return None
    
    def startThread (self):
        # parse SQL
        self.componentThread        = threading.Thread(target=self.start, daemon=True)
        self.componentThread.start ()