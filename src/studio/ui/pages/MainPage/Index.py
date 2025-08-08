import customtkinter
import os
import sys
import time
import threading
from tkinter import Tk
from dotenv import load_dotenv
from functools import partial
from tkinter.font import Font

from cairosvg import svg2png
from PIL import Image, ImageTk
import io

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

# correctly load database using pyinstaller
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # test
    __resource_path = os.path.abspath(os.path.join(sys._MEIPASS, "..", "Resources"))
    __realPath = os.path.join(__resource_path, databasePath)
    databasePath = __realPath


# manual access to schema directory
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path,  '../../../' +  os.pardir)))
from engine.SQLQueryEngine import SQLQueryEngine

# restore parent directory path
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))
from ui.pages.WelcomePage.Index import Index as WelcomePage
from ui.pages.TablePage.Index import Index as TablePage

# Load the Font Awesome OTF font
fontFile    =   os.path.abspath(os.path.join(dir_path, '../../../assets/fonts/fontawesome/svgs/solid/database.svg'))


class Index:
    def __init__(self, root):
        self.databasePath = databasePath
        self.tabs = f"       "
        self.databases = {}
        self.mainFrame = customtkinter.CTkFrame(master=root, corner_radius=0, bg_color="transparent", fg_color="transparent")
        self.mainFrame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.mainFrame.grid_rowconfigure(0, weight=1)
        self.mainFrame.grid_columnconfigure (1, weight=1)

        self.mainContentFrame = customtkinter.CTkFrame(master=self.mainFrame, corner_radius=0, bg_color="transparent", fg_color="transparent")
        self.mainContentFrame.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")
        self.mainContentFrame.grid_rowconfigure(0, weight=1)
        self.mainContentFrame.grid_columnconfigure (0, weight=1)

        self.sidebar = customtkinter.CTkScrollableFrame(self.mainFrame, width=200, height=200, bg_color="#262626", fg_color="transparent")
        self.sidebar.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(1, weight=1)
        self.sidebar.grid_columnconfigure (0, weight=1)

        self.sidebarTitleFrame = customtkinter.CTkFrame(self.sidebar, width=200, height=200, bg_color="transparent", fg_color="#178015", corner_radius=0)
        self.sidebarTitleFrame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(0, weight=1)
        self.sidebar.grid_columnconfigure (0, weight=1)

        self.sidebarTitle = customtkinter.CTkLabel(master=self.sidebarTitleFrame, text=f"Databases ({self.databasePath})", text_color="#F3F3F3", bg_color="transparent", fg_color="transparent", font=customtkinter.CTkFont(size = 12), justify="left")
        self.sidebarTitle.grid(row=0, column=0, ipady="2", ipadx="10", sticky="ew")

        self.sidebarContentFrame = customtkinter.CTkFrame(self.sidebar, width=200, height=780, bg_color="transparent", fg_color="transparent", corner_radius=0)
        self.sidebarContentFrame.grid_rowconfigure(0, weight=1)
        self.sidebarContentFrame.grid_columnconfigure (0, weight=1)
        self.sidebarContentFrame.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")

        # run database sengine
        self.__initializeEngine ()

    def __initializeEngine (self):
        self.engine = SQLQueryEngine ()
        self.engine.setDatabasePath (self.databasePath)
        #self.engine.useDatabase (databaseName)
        
        self.__addDatabaseSection ()

    def __addDatabaseSection (self):

        for __databaseName in self.engine.showDatabases ():

            itemFrame = customtkinter.CTkFrame(self.sidebarContentFrame,  bg_color="#333333", fg_color="#333333", corner_radius=0)
            itemFrame.grid_rowconfigure(0, weight=1)
            itemFrame.grid_columnconfigure (0, weight=1)
            itemFrame.pack(fill="both", expand=True)

            # get database details
            self.engine.useDatabase (__databaseName)
            __tables = self.engine.showTables ()
            if not __databaseName in self.databases: self.databases[__databaseName] = {}

            for table in __tables:
                self.databases[__databaseName][table] = False

            itemHeader = customtkinter.CTkLabel(master=itemFrame, text=f"{__databaseName}", text_color="#F3F3F3", bg_color="transparent", fg_color="transparent", font=customtkinter.CTkFont(size = 12), justify="left")
            itemHeader.grid(row=0, column=0, ipady="5", ipadx="30", sticky="w")

            with open(fontFile, "rb") as svg_file:
                cont = svg_file.read ()
                mod = cont.decode('utf-8').replace('<path', '<path fill="#ffffff"')
                mod.encode('utf-8')
                png_data = svg2png(bytestring=mod, output_width=20, output_height=15)

            # Load the PNG data into a PIL Image
            image = Image.open(io.BytesIO(png_data))
            photo_image = ImageTk.PhotoImage(image)

            # Create a label and display the image
            image_label = customtkinter.CTkLabel(master = itemHeader, text="", image=photo_image)
            image_label.image = photo_image  # Keep a reference to avoid garbage collection
            image_label.grid(row=0, column=0, padx=5, sticky="w")

            
            # tables
            for __table in self.databases[__databaseName]:
                item = customtkinter.CTkButton(master=self.sidebarContentFrame, text=f"{self.tabs}{__table}", text_color="#C3C3C3", bg_color="transparent", fg_color="transparent", corner_radius=0, anchor="w", hover_color="#178015")
                item.pack(fill="both", expand=True)
                item.bind("<Button-1>", partial(self.__selectTable, __databaseName, __table, self.databases[__databaseName], item))
            
            # load welcome page
            self.__loadWelcomePage ()

    def __selectTable (self, databaseName, tableName, tables, target, e):
        for table in tables:
            self.databases[databaseName][table] = True if tableName == table else False

        # udpate UI
        self.__updateDatabaseList ()

        threading.Thread(target = partial(self.__loadTablePage, databaseName, tableName), daemon=True).start ()
        #self.__loadTablePage (databaseName, tableName)

        return self

    def __updateDatabaseList (self):
        self.sidebarContentFrame = customtkinter.CTkFrame(self.sidebar, width=200, height=780, bg_color="transparent", fg_color="transparent", corner_radius=0)
        self.sidebarContentFrame.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")


        # load from cache
        for __databaseName in self.databases: 
            itemFrame = customtkinter.CTkFrame(self.sidebarContentFrame,  bg_color="#333333", fg_color="#333333", corner_radius=0)
            itemFrame.grid_rowconfigure(0, weight=1)
            itemFrame.grid_columnconfigure (0, weight=1)
            itemFrame.pack(fill="both", expand=True)
        
            itemHeader = customtkinter.CTkLabel(master=itemFrame, text=f"{__databaseName}", text_color="#F3F3F3", bg_color="transparent", fg_color="transparent", font=customtkinter.CTkFont(size = 12), justify="left")
            itemHeader.grid(row=0, column=0, ipady="5", ipadx="30", sticky="w")

            with open(fontFile, "rb") as svg_file:
                cont = svg_file.read ()
                mod = cont.decode('utf-8').replace('<path', '<path fill="#ffffff"')
                mod.encode('utf-8')
                png_data = svg2png(bytestring=mod, output_width=20, output_height=15)

            # Load the PNG data into a PIL Image
            image = Image.open(io.BytesIO(png_data))
            photo_image = ImageTk.PhotoImage(image)

            # Create a label and display the image
            image_label = customtkinter.CTkLabel(master = itemHeader, text="", image=photo_image)
            image_label.image = photo_image  # Keep a reference to avoid garbage collection
            image_label.grid(row=0, column=0, padx=5, sticky="w")

            
            # tables
            for __table in self.databases[__databaseName]:
                item = customtkinter.CTkButton(master=self.sidebarContentFrame, text=f"{self.tabs}{__table}", text_color="#C3C3C3", bg_color="transparent", fg_color="transparent", corner_radius=0, anchor="w", hover_color="#178015")
                if self.databases[__databaseName][__table] == True: item.configure(bg_color = "#178015")
                item.pack(fill="both", expand=True)
                item.bind("<Button-1>", partial(self.__selectTable, __databaseName, __table, self.databases[__databaseName], item))

            
        return self
            
    def __loadWelcomePage (self):
        WelcomePage (self.mainContentFrame)
        return self
    
    def __loadTablePage (self, databaseName, tableName):
        tablePage = TablePage (self.mainContentFrame, self.engine, databaseName, tableName)
        tablePage.__showHeader ()
        tablePage.__showHeaderTabs ()
        tablePage.__showBody ()
        tablePage.__startTableThread ()

        def __showSQLSection (tableThread):
            tablePage.currentPage = 1
            tablePage.bodyFrame.destroy ()
            tablePage.__removeTableSection ()
            tablePage.__showBody ()
            tablePage.__showSQLQueryTextBox ()
            tablePage.__showTableStatusSection ()
            tablePage.__removeTableSection ()
            tablePage.__showTableSection ()
            tablePage.showTableData(__tableThread)
            tablePage.__showSQLQueryStatusBox ()
            tablePage.paginationFrame.destroy ()
            tablePage.__showPaginationSection ()
        
        def __showTableStructureSection ():
            tablePage.bodyFrame.destroy ()
            tablePage.__removeTableStatusSection ()
            tablePage.__removeTableSection ()
            tablePage.__removeSQLQueryStatusBox ()
            tablePage.__showBody ()
            tablePage.__showTableStructureSection ()
            tablePage.__removePaginationSection ()
            tablePage.__removeTableStatusSection ()
            tablePage.paginationFrame.destroy ()
            tablePage.__showTableSection ()
            tablePage.__showTableStructureData ()
            

        while True:
            __tableThread = tablePage.getTableThread ()

            if __tableThread is not None:
                __showSQLSection (__tableThread)

                tablePage.headerTabQueryBtn.configure (command=partial(__showSQLSection, __tableThread))
                tablePage.headerTabStructureBtn.configure (command=__showTableStructureSection)
                break
            elif tablePage.tableThread.is_alive ():
                pass   
            else:
                pass
            
            time.sleep(1)

        return self