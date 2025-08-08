import customtkinter
import os
import sys
from tkinter import Tk
from PIL import Image
from dotenv import load_dotenv


# manual access to schema directory
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path,  '../../' +  os.pardir)))

# restore parent directory path
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

from ui.pages.MainPage.Index import Index as MainPage

# load env variables
# PyInstaller temp folder
# https://pyinstaller.org/en/stable/runtime-information.html
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    load_dotenv(dotenv_path=os.path.join(sys._MEIPASS, os.path.join("configs", ".env")))
else:
    load_dotenv(dotenv_path=f'configs/.env')

databasePath = os.getenv('DATABASE_PATH')

# remove ./ from path to be able to load by pyinstaller correctly
__arrayDBPath = databasePath.split('./')
if __arrayDBPath[1]:
    databasePath = __arrayDBPath[1]

class Index(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.databasePath = databasePath
        self.geometry("1280x832")
        self.title("RDBMS Studio")
        self._set_appearance_mode('dark')
        self.resizable(False, False)
        self.description = "This is a project requirement for the course `CMSC 227 - Advanced Database Systems`. It must not be used in production, reproduced, or distributed to fulfill the same course requirements. You may only use this as a reference for future work."
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)

        self.mainFrame = customtkinter.CTkFrame(master=self, corner_radius=0, bg_color="transparent", fg_color="transparent")
        self.mainFrame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.mainFrame.grid_rowconfigure(7, weight=0)
        self.mainFrame.grid_columnconfigure (0, weight=1)

        # empty row
        self.welcomeMessage = customtkinter.CTkLabel(master=self.mainFrame, text="  ", bg_color="transparent", fg_color="transparent")
        self.welcomeMessage.grid(row=0, column=0, pady="45", sticky="nsew")

        self.uplbLogo = customtkinter.CTkImage(dark_image=Image.open(os.path.join(os.path.dirname(__file__),"./assets/img/uplbLogo.png")),size=(235, 210))
        self.uplbLogoBtn = customtkinter.CTkButton(master=self.mainFrame, image=self.uplbLogo, anchor="center", text="", fg_color="transparent", bg_color="transparent", hover_color="#242424")
        self.uplbLogoBtn.grid(row=1, column=0, pady="10",  sticky="nsew")

        self.welcomeMessage = customtkinter.CTkLabel(master=self.mainFrame, text="RDBMS", text_color="#F3F3F3", bg_color="transparent", fg_color="transparent", font=customtkinter.CTkFont(size = 36))
        self.welcomeMessage.grid(row=2, column=0, pady="0", sticky="nsew")

        self.welcomeMessage = customtkinter.CTkLabel(master=self.mainFrame, text="Relational Database Management System", text_color="#F3F3F3", bg_color="transparent", fg_color="transparent", font=customtkinter.CTkFont(size = 12))
        self.welcomeMessage.grid(row=3, column=0, pady="0", sticky="nsew")

        self.welcomeMessage = customtkinter.CTkLabel(master=self.mainFrame, text=f"{self.description}", text_color="#F3F3F3", bg_color="transparent", fg_color="transparent", font=customtkinter.CTkFont(size = 12), wraplength=700)
        self.welcomeMessage.grid(row=4, column=0, pady="10", sticky="nsew")

        self.welcomeMessage = customtkinter.CTkLabel(master=self.mainFrame, text=f"Database Path: {self.databasePath}", text_color="#ABABAB", bg_color="#2A2A2A", fg_color="transparent", font=customtkinter.CTkFont(size = 12), wraplength=700)
        self.welcomeMessage.grid(row=5, column=0, pady="20", padx="250", ipady="2", sticky="nsew")

        self.proceedBtn = customtkinter.CTkButton(master=self.mainFrame, anchor="center", text="PROCEED", fg_color="#178015", bg_color="transparent", corner_radius=10, text_color_disabled="#eee", hover_color="#3E913C")
        self.proceedBtn.bind('<Button-1>', self.proceed)
        self.proceedBtn.grid(row=6, column=0, pady="10", padx=500, ipady="5",  sticky="nsew")


    # https://www.geeksforgeeks.org/how-to-center-a-window-on-the-screen-in-tkinter/
    def centerWindow(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    def proceed (self, e):
        self.proceedBtn.configure(state="disabled", text="Loading database ...")
        __pathDetails = self.__checkPath (self.databasePath)

        if not __pathDetails['exists']:
            self.showError (f"Database path \"{__pathDetails['path']}\" is unreadable")
            self.resetProceedBtn ()
        else:
            self.showError (None)
            self.__openMainPage ()
    
    def resetProceedBtn (self):
        self.proceedBtn.configure(state="normal", text="PROCEED")
    
    def showError (self, message = None):
        __error = f"ERROR: {message}" if message != None else ''
 
        self.errorMessage = customtkinter.CTkLabel(master=self.mainFrame, text=f"{__error}", text_color="#FE8E8E", bg_color="transparent", fg_color="transparent", font=customtkinter.CTkFont(size = 12), wraplength=700)
        self.errorMessage.grid(row=7, column=0, pady="10", padx="250", ipady="2", sticky="nsew")

        return self

    def __checkPath (self, path):
        __realPath = os.path.realpath(path)
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # test
            __resource_path = os.path.abspath(os.path.join(sys._MEIPASS, "..", "Resources"))
            __realPath = os.path.join(__resource_path, path)
        else:
            # test
            print ('e')


        return {"path" : __realPath, "exists" : os.path.exists(__realPath)}

    def __openMainPage (self):
        # replace the page entirely
        MainPage (self)

    def open (self):
        self.centerWindow(self)
        self.attributes('-topmost', True)
        self.update()
        self.focus ()
        self.mainloop ()
    
    def close (self):
        self.destroy ()

if __name__ == '__main__':
    index = Index ()
    index.centerWindow(index)
    index.open ()
