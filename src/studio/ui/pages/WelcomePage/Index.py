import customtkinter
import os
import sys
import webbrowser
from tkinter import Tk
from PIL import Image
from dotenv import load_dotenv
from functools import partial

# load env variables
load_dotenv(dotenv_path=f'configs/.env')
databasePath = os.getenv('DATABASE_PATH')

# manual access to schema directory
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path,  '../../../' +  os.pardir)))
from engine.SQLQueryEngine import SQLQueryEngine

# restore parent directory path
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

class Index:
    def __init__(self, root):
        self.databasePath   =   databasePath
        self.databases      =   {}
        self.tabs           =   f"       "
        self.footNote       =   "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat"
        self.projectLink    =   "https://github.com/UPLB-CMSC227/rdbms"
        self.mainFrame      =   customtkinter.CTkFrame(master=root, corner_radius=0, bg_color="transparent", fg_color="transparent")

        self.mainFrame.grid_rowconfigure(1, weight=0)
        self.mainFrame.grid_columnconfigure (0, weight=1)
        self.mainFrame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.mainTopFrame = customtkinter.CTkFrame(master=self.mainFrame, bg_color="transparent", fg_color="transparent")
        self.mainTopFrame.grid_rowconfigure(0, weight=1)
        self.mainTopFrame.grid_columnconfigure (1, weight=1)
        self.mainTopFrame.grid(row=0, column=0, sticky="nsew", padx="320")


        self.uplbLogo = customtkinter.CTkImage(dark_image=Image.open(os.path.join(os.path.dirname(__file__),"./assets/img/uplbLogo.png")),size=(90, 80))
        self.uplbLogoBtn = customtkinter.CTkButton(master=self.mainTopFrame, image=self.uplbLogo, anchor="center", text="", fg_color="transparent", bg_color="transparent", hover_color="#242424")
        self.uplbLogoBtn.grid(row=0, column=0,  sticky="nsew")

        self.welcomeMessageFrame = customtkinter.CTkFrame(master=self.mainTopFrame, bg_color="transparent", fg_color="transparent")
        self.welcomeMessageFrame.grid_rowconfigure(2, weight=0)
        self.welcomeMessageFrame.grid_columnconfigure (0, weight=0)
        self.welcomeMessageFrame.grid(row=0, column=1, sticky="nsew", pady="300")

        self.welcomeMessage = customtkinter.CTkLabel(master=self.welcomeMessageFrame, text=f"WELCOME", bg_color="transparent", fg_color="transparent", font=customtkinter.CTkFont(size = 26))
        self.welcomeMessage.grid(row=0, column=0, sticky="w")

        self.welcomeMessage = customtkinter.CTkLabel(master=self.welcomeMessageFrame, text="Relational Database Management System", text_color="#C3C3C3", bg_color="transparent", fg_color="transparent", font=customtkinter.CTkFont(size = 12))
        self.welcomeMessage.grid(row=1, column=0, sticky="w")

        self.welcomeMessage = customtkinter.CTkLabel(master=self.welcomeMessageFrame, text=f"{self.projectLink}", text_color="#2689E4", bg_color="transparent", fg_color="transparent", font=customtkinter.CTkFont(size = 12))
        self.welcomeMessage.bind("<Button-1>", lambda e: self.__openLink(self.projectLink))
        self.welcomeMessage.grid(row=2, column=0, sticky="nw")

        self.welcomeMessage = customtkinter.CTkLabel(master=self.mainFrame, text=f"{self.footNote}", text_color="#434343", bg_color="transparent", fg_color="transparent", wraplength=800, justify="left", font=customtkinter.CTkFont(size = 10))
        self.welcomeMessage.grid(row=1, column=0, sticky="sw", ipadx="10", ipady="90")

    def __openLink (self, link):
        webbrowser.open_new(link)