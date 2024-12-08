import customtkinter
import os
import sys
import threading
import math
import time
from tkinter import Tk
from cairosvg import svg2png
from PIL import Image, ImageTk
import io
from dotenv import load_dotenv
from CTkTable import *
from functools import partial
from concurrent.futures import ThreadPoolExecutor

# load env variables
load_dotenv(dotenv_path=f'configs/.env')
databasePath = os.getenv('DATABASE_PATH')

# manual access to schema directory
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path,  '../../../' +  os.pardir)))

from ui.components.CTkXYFrame import *
from ui.components.ProgressBar import Index as ProgressBar
from ui.components.ShowAllRowsConfirmationWindows import Index as ShowAllRowsConfirmationWindows

# restore parent directory path
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

fontFileCheckIcon           =   os.path.abspath(os.path.join(dir_path, '../../../assets/fonts/fontawesome/svgs/solid/circle-check.svg'))
fontFileWarningIcon         =   os.path.abspath(os.path.join(dir_path, '../../../assets/fonts/fontawesome/svgs/solid/triangle-exclamation.svg'))
fontFileTableColumnsIcon    =   os.path.abspath(os.path.join(dir_path, '../../../assets/fonts/fontawesome/svgs/solid/table-columns.svg'))
fontFileBoltIcon            =   os.path.abspath(os.path.join(dir_path, '../../../assets/fonts/fontawesome/svgs/solid/bolt.svg'))
fontFileNextIcon            =   os.path.abspath(os.path.join(dir_path, '../../../assets/fonts/fontawesome/svgs/solid/chevron-right.svg'))
fontFilePrevIcon            =   os.path.abspath(os.path.join(dir_path, '../../../assets/fonts/fontawesome/svgs/solid/chevron-left.svg'))


class Index:
    def __init__(self, root, engine, databaseName, tableName):
        self.engine                 =   engine
        self.databasePath           =   databasePath
        self.databaseName           =   databaseName
        self.tableName              =   tableName
        self.databases              =   {}
        self.SQLData                =   None
        self.SQlError               =   None
        self.SQL                    =   f"SELECT * FROM  {self.tableName};"
        self.tabs                   =   f"       "
        self.footNote               =   "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat"
        self.projectLink            =   "https://github.com/UPLB-CMSC227/rdbms"
        self.mainFrame              =   customtkinter.CTkFrame(master=root, corner_radius=0, bg_color="transparent", fg_color="transparent")
        self.tableThread            =   None
        self.dataTable              =   None
        self.rowCount               =   0
        self.totalPages             =   0
        self.currentPage            =   1
        self.maxRowCountPerPage     =   50
        self.executionTime          =   "0.00"
        self.ProgressBar            =   None
        self.maxRowCountWindow      =   None

        self.mainFrame = customtkinter.CTkFrame(master=root, bg_color="transparent", fg_color="transparent")
        self.mainFrame.grid_rowconfigure(2, weight=1)
        self.mainFrame.grid_columnconfigure (0, weight=1)
        self.mainFrame.grid(row=0, column=0, sticky="nsew")

        self.topFrame = customtkinter.CTkFrame(master=self.mainFrame, bg_color="transparent", fg_color="transparent")
        self.topFrame.grid_rowconfigure(1, weight=1)
        self.topFrame.grid_columnconfigure (0, weight=1)
        self.topFrame.grid(row=0, column=0, sticky="nsew")

        self.midFrame = customtkinter.CTkFrame(master=self.mainFrame, bg_color="transparent", fg_color="transparent", height=550)
        self.midFrame.grid_rowconfigure(2, weight=1)
        self.midFrame.grid_columnconfigure (0, weight=1)
        self.midFrame.grid(row=1, column=0, sticky="nsew")

        self.bottomFrame = customtkinter.CTkFrame(master=self.mainFrame, bg_color="transparent", fg_color="transparent")
        self.bottomFrame.grid_rowconfigure(0, weight=1)
        self.bottomFrame.grid_columnconfigure (0, weight=1)
        self.bottomFrame.grid(row=2, column=0, sticky="nsew")

        #self.__showHeader ()
        #self.__showHeaderTabs ()
        #self.__showBody ()

        
    
    def __showHeader(self):
        self.headerFrame = customtkinter.CTkFrame(master=self.topFrame, bg_color="transparent", fg_color="transparent", height=30)
        self.headerFrame.grid_rowconfigure(0, weight=1)
        self.headerFrame.grid_columnconfigure (0, weight=1)
        self.headerFrame.grid(row=1, column=0, padx="0", pady="0", sticky="nsew")
    
    def __showHeaderTabs (self):
        self.headerTabFrame = customtkinter.CTkFrame(master=self.headerFrame, bg_color="#292929", fg_color="#292929")
        self.headerTabFrame.grid_rowconfigure(0, weight=1)
        self.headerTabFrame.grid_columnconfigure (5, weight=1)
        self.headerTabFrame.grid(row=0, column=0, padx="0", pady="0", sticky="nsew")

        # SQL Query Tab
        self.headerTabQuery = customtkinter.CTkLabel(master=self.headerTabFrame, text=" ", text_color="#C3C3C3", bg_color="transparent", fg_color="transparent")
        self.headerTabQuery.grid_rowconfigure(0, weight=1)
        self.headerTabQuery.grid_columnconfigure (0, weight=1)
        self.headerTabQuery.grid(row=0, column=0, padx="5", pady="2", ipadx="10", ipady="2", sticky="nsew")

        self.headerTabQueryBtn = customtkinter.CTkButton(master=self.headerTabQuery, text="SQL Query", text_color="#C3C3C3", bg_color="transparent", fg_color="transparent", corner_radius=0, hover_color="#2E2E2E")
        self.headerTabQueryBtn.grid(row=0, column=0, sticky="nsew")

        # table sreucture tab
        self.headerTabStructure = customtkinter.CTkLabel(master=self.headerTabFrame, text=" ", bg_color="transparent", fg_color="transparent")
        self.headerTabStructure.grid_rowconfigure(0, weight=1)
        self.headerTabStructure.grid_columnconfigure (0, weight=1)
        self.headerTabStructure.grid(row=0, column=1, padx="5", pady="2", ipadx="10", ipady="2", sticky="nsew")

        self.headerTabStructureBtn = customtkinter.CTkButton(master=self.headerTabQuery, text="Table Structure", text_color="#C3C3C3", bg_color="transparent", fg_color="transparent", corner_radius=0, hover_color="#2E2E2E")
        self.headerTabStructureBtn.grid(row=0, column=1, sticky="nsew")
    
    def __showBody (self):
        self.bodyFrame = customtkinter.CTkFrame(master=self.midFrame, bg_color="transparent", fg_color="transparent", height=430)
        self.bodyFrame.grid_rowconfigure(0, weight=1)
        self.bodyFrame.grid_columnconfigure (0, weight=1)
        self.bodyFrame.grid(row=0, column=0, padx="0", pady="0", sticky="nsew")
    
    def __showSQLQueryTextBox (self):
        self.SQLQueryTextBoxFrame = customtkinter.CTkFrame(master=self.bodyFrame, bg_color="#2D2D2D", fg_color="#2D2D2D")
        self.SQLQueryTextBoxFrame.grid_rowconfigure(1, weight=1)
        self.SQLQueryTextBoxFrame.grid_columnconfigure (0, weight=1)
        self.SQLQueryTextBoxFrame.grid(row=0, column=0, padx="0", pady="0", sticky="nsew")

        self.SQLQueryTextBox = customtkinter.CTkTextbox(master=self.SQLQueryTextBoxFrame, text_color="#C3C3C3", bg_color="transparent", fg_color="transparent", height=100)
        self.SQLQueryTextBox.grid(row=0, column=0, padx="0", pady="0", sticky="nsew")

        self.SQLQueryTextBoxBtnFrame = customtkinter.CTkFrame(master=self.SQLQueryTextBoxFrame, bg_color="#2D2D2D", fg_color="transparent", height=50)
        self.SQLQueryTextBoxBtnFrame.grid_rowconfigure(0, weight=1)
        self.SQLQueryTextBoxBtnFrame.grid_columnconfigure (1, weight=1)
        self.SQLQueryTextBoxBtnFrame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # bolt icon
        with open(fontFileBoltIcon, "rb") as svg_file:
            cont = svg_file.read ()
            mod = cont.decode('utf-8').replace('<path', '<path fill="#ffffff"')
            mod.encode('utf-8')
            iconData = svg2png(bytestring=mod, output_width=20, output_height=15)
        
        # Load the PNG data into a PIL Image
        imageIcon = Image.open(io.BytesIO(iconData))
        boltIcon = ImageTk.PhotoImage(imageIcon)


        self.SQLQueryTextBoxExecuteBtn = customtkinter.CTkButton(master=self.SQLQueryTextBoxBtnFrame, bg_color="transparent", fg_color="#505050", hover_color="#707070", text="Execute", corner_radius=20, image=boltIcon)
        self.SQLQueryTextBoxExecuteBtn.bind("<Button-1>", self.__executeSQLFromTextArea)
        self.SQLQueryTextBoxExecuteBtn.grid(row=0, column=1, sticky="se")

    def __showSQLQueryStatusBox (self):
        self.SQLQueryTextBoxStatusFrame = customtkinter.CTkFrame(master=self.SQLQueryTextBoxBtnFrame, bg_color="transparent", fg_color="transparent")
        self.SQLQueryTextBoxStatusFrame.grid_rowconfigure(0, weight=1)
        self.SQLQueryTextBoxStatusFrame.grid_columnconfigure (0, weight=1)
        self.SQLQueryTextBoxStatusFrame.grid(row=0, column=0, sticky="nsew")

        self.SQLQueryTextBoxStatusBoxFrame = customtkinter.CTkFrame(master=self.SQLQueryTextBoxStatusFrame,  bg_color="transparent", fg_color="transparent", width=830, corner_radius=30)
        self.SQLQueryTextBoxStatusBoxFrame.grid_rowconfigure(0, weight=1)
        self.SQLQueryTextBoxStatusBoxFrame.grid_columnconfigure (1, weight=1)
        self.SQLQueryTextBoxStatusBoxFrame.grid(row=0, column=0, sticky="new")


        if self.SQlError == None:
            with open(fontFileCheckIcon, "rb") as svg_file:
                cont = svg_file.read ()
                mod = cont.decode('utf-8').replace('<path', '<path fill="#78D576"')
                mod.encode('utf-8')
                iconData = svg2png(bytestring=mod, output_width=20, output_height=15)

            # Load the PNG data into a PIL Image
            imageIcon = Image.open(io.BytesIO(iconData))
            checkIcon = ImageTk.PhotoImage(imageIcon)

            self.SQLQueryStatusText = customtkinter.CTkLabel(master=self.SQLQueryTextBoxStatusBoxFrame, text=f"EXECUTE COMMAND: {self.SQL}", bg_color="transparent", fg_color="#424242", text_color="#C3C3C3", width=700, corner_radius=30, compound='left', anchor='w', justify='left', image=checkIcon, wraplength=700)
            self.SQLQueryStatusText.grid(row=0, column=0, sticky="w", padx=5, ipady=2, pady=5)
        else:
            with open(fontFileWarningIcon, "rb") as svg_file:
                cont = svg_file.read ()
                mod = cont.decode('utf-8').replace('<path', '<path fill="#ffffff"')
                mod.encode('utf-8')
                iconData = svg2png(bytestring=mod, output_width=20, output_height=15)

            # Load the PNG data into a PIL Image
            imageIcon = Image.open(io.BytesIO(iconData))
            checkIcon = ImageTk.PhotoImage(imageIcon)

            self.SQLQueryStatusText = customtkinter.CTkLabel(master=self.SQLQueryTextBoxStatusBoxFrame, text=f"WARNING: {self.SQlError}", bg_color="transparent", fg_color="#E5A14D", text_color="#ffffff", width=700, corner_radius=30, compound='left', anchor='w', justify='left', image=checkIcon, wraplength=700, font=customtkinter.CTkFont(size = 12))
            self.SQLQueryStatusText.grid(row=0, column=0, sticky="w", padx=5, ipady=2)    
                                                         
        self.SQLQueryStatusTextTime = customtkinter.CTkLabel(master=self.SQLQueryTextBoxStatusBoxFrame, text=f"TOOK: {self.executionTime}", bg_color="transparent", fg_color="transparent", corner_radius=0, compound='left', anchor='w')
        self.SQLQueryStatusTextTime.grid(row=0, column=1, sticky="w", padx=5)

    def __showTableStatusSection (self):
        self.TableStatusFrame = customtkinter.CTkFrame(master=self.midFrame, bg_color="transparent", fg_color="transparent")
        self.TableStatusFrame.grid_rowconfigure(0, weight=1)
        self.TableStatusFrame.grid_columnconfigure (1, weight=1)
        self.TableStatusFrame.grid(row=1, column=0, padx="0", pady="20", sticky="nsew")

        self.TableStatusFrameLeft = customtkinter.CTkFrame(master=self.TableStatusFrame, bg_color="transparent", fg_color="transparent", width=500, height=120)
        self.TableStatusFrameLeft.grid_rowconfigure(1, weight=1)
        self.TableStatusFrameLeft.grid_columnconfigure (0, weight=1)
        self.TableStatusFrameLeft.grid(row=0, column=0, padx="0", pady="0", sticky="nsew")

        self.TableStatusFrameRight = customtkinter.CTkFrame(master=self.TableStatusFrame, bg_color="transparent", fg_color="transparent", height=120)
        self.TableStatusFrameRight.grid_rowconfigure(1, weight=1)
        self.TableStatusFrameRight.grid_columnconfigure (0, weight=1)
        self.TableStatusFrameRight.grid(row=0, column=1, padx="0", pady="0", sticky="nsew")

        # column icon
        with open(fontFileTableColumnsIcon, "rb") as svg_file:
            cont = svg_file.read ()
            mod = cont.decode('utf-8').replace('<path', '<path fill="#78D576"')
            mod.encode('utf-8')
            iconData = svg2png(bytestring=mod, output_width=20, output_height=15)

        # Load the PNG data into a PIL Image
        imageIcon = Image.open(io.BytesIO(iconData))
        columnIcon = ImageTk.PhotoImage(imageIcon)

        self.tableText = customtkinter.CTkLabel(master=self.TableStatusFrameLeft, text=f"[{self.databaseName}/{self.tableName}]", bg_color="transparent", fg_color="transparent", font=customtkinter.CTkFont(size = 16), compound='left', justify="left", anchor="w", text_color="#C3C3C3", image=columnIcon, width=500)
        self.tableText.grid(row=0, column=0, padx="10", sticky="nw")
        self.tableText = customtkinter.CTkLabel(master=self.TableStatusFrameLeft, text="active table", bg_color="transparent", fg_color="transparent", justify="left", anchor="w", text_color="#656565", width=500)
        self.tableText.grid(row=1, column=0, padx="10", sticky="nw")

        self.TableStatusFrameRightFirstRow = customtkinter.CTkFrame(master=self.TableStatusFrameRight, bg_color="transparent", fg_color="transparent", height=40)
        self.TableStatusFrameRightFirstRow.grid_rowconfigure(0, weight=1)
        self.TableStatusFrameRightFirstRow.grid_columnconfigure (1, weight=1)
        self.TableStatusFrameRightFirstRow.grid(row=0, column=0, padx="0", pady="0", sticky="nsew")

        self.TableStatusFrameRightSecondRow = customtkinter.CTkFrame(master=self.TableStatusFrameRight, bg_color="transparent", fg_color="transparent", height=40)
        self.TableStatusFrameRightSecondRow.grid_rowconfigure(0, weight=1)
        self.TableStatusFrameRightSecondRow.grid_columnconfigure (1, weight=1)
        self.TableStatusFrameRightSecondRow.grid(row=1, column=0, padx="0", pady="0", sticky="nsew")

        # num rows
        self.numRowsText = customtkinter.CTkLabel(master=self.TableStatusFrameRightFirstRow, text=f"Total Number of Rows: ({self.rowCount})", bg_color="transparent", fg_color="transparent", justify="left", anchor="w", text_color="#C3C3C3", width=250)
        self.numRowsText.grid(row=0, column=0, sticky="nw")
        self.numRowsCountText = customtkinter.CTkLabel(master=self.TableStatusFrameRightFirstRow, text=f"Maximum Rows Per Page ({self.maxRowCountPerPage})", bg_color="transparent", fg_color="transparent", justify="left", anchor="w", text_color="#C3C3C3", width=250)
        self.numRowsCountText.grid(row=0, column=1, sticky="nw")

        # returning results
        self.returningResultsText = customtkinter.CTkLabel(master=self.TableStatusFrameRightSecondRow, text=f"Returning Pages ({self.currentPage}/{self.totalPages}) ", bg_color="transparent", fg_color="transparent", justify="left", anchor="w", text_color="#C3C3C3", width=250)
        self.returningResultsText.grid(row=0, column=0, sticky="nw")
    
    def __showPaginationSection (self):
        self.paginationFrame = customtkinter.CTkFrame(master=self.bottomFrame, bg_color="transparent", fg_color="transparent")
        self.paginationFrame.grid_rowconfigure(0, weight=1)
        self.paginationFrame.grid_columnconfigure (1, weight=1)
        self.paginationFrame.grid(row=0, column=0, sticky="nsew")

        self.paginationFrameLeft = customtkinter.CTkFrame(master=self.paginationFrame, bg_color="transparent", fg_color="transparent")
        self.paginationFrameLeft.grid_rowconfigure(1, weight=1)
        self.paginationFrameLeft.grid_columnconfigure (0, weight=1)
        self.paginationFrameLeft.grid(row=0, column=0, sticky="nsew")

        self.paginationFrameRight = customtkinter.CTkFrame(master=self.paginationFrame, bg_color="transparent", fg_color="transparent")
        self.paginationFrameRight.grid_rowconfigure(1, weight=0)
        self.paginationFrameRight.grid_columnconfigure (0, weight=1)
        self.paginationFrameRight.grid(row=0, column=1, sticky="nsew")

        # empty top space on navigation
        self.paginationEmpty = customtkinter.CTkFrame(master=self.paginationFrameRight, bg_color="transparent", fg_color="transparent", height=10)
        self.paginationEmpty.grid(row=0, column=0, sticky="new")

        self.paginationBtnSection = customtkinter.CTkFrame(master=self.paginationFrameRight, bg_color="transparent", fg_color="transparent")
        self.paginationBtnSection.grid_rowconfigure(0, weight=1)
        self.paginationBtnSection.grid_columnconfigure (4, weight=1)
        self.paginationBtnSection.grid(row=1, column=0, sticky="nsew")

        self.paginationFirstBtn = customtkinter.CTkButton(master=self.paginationBtnSection, bg_color="transparent", fg_color="transparent", text="First", width=50)
        self.paginationFirstBtn.bind("<Button-1>", partial(self.__paginateFirst, self.paginationFirstBtn))
        self.paginationFirstBtn.grid(row=0, column=0, sticky="nsew")

        self.paginationLastBtn = customtkinter.CTkButton(master=self.paginationBtnSection, bg_color="transparent", fg_color="transparent", text="Last", width=50)
        self.paginationLastBtn.bind("<Button-1>", partial(self.__paginateLast, self.paginationLastBtn))
        self.paginationLastBtn.grid(row=0, column=1, sticky="nsew")

        # previcon
        with open(fontFilePrevIcon, "rb") as svg_file:
            cont = svg_file.read ()
            mod = cont.decode('utf-8').replace('<path', '<path fill="#ffffff"')
            mod.encode('utf-8')
            iconData = svg2png(bytestring=mod, output_width=20, output_height=15)

        # Load the PNG data into a PIL Image
        imageIcon = Image.open(io.BytesIO(iconData))
        prevIcon = ImageTk.PhotoImage(imageIcon)

        self.paginationPrevBtn = customtkinter.CTkButton(master=self.paginationBtnSection, bg_color="transparent", fg_color="transparent", text="Prev", width=50, image=prevIcon)
        self.paginationPrevBtn.bind("<Button-1>", partial(self.__paginatePrev, self.paginationPrevBtn))
        self.paginationPrevBtn.grid(row=0, column=2, sticky="nsew")

        # next icon
        with open(fontFileNextIcon, "rb") as svg_file:
            cont = svg_file.read ()
            mod = cont.decode('utf-8').replace('<path', '<path fill="#ffffff"')
            mod.encode('utf-8')
            iconData = svg2png(bytestring=mod, output_width=20, output_height=15)

        # Load the PNG data into a PIL Image
        imageIcon = Image.open(io.BytesIO(iconData))
        nextIcon = ImageTk.PhotoImage(imageIcon)

        self.paginationNextBtn = customtkinter.CTkButton(master=self.paginationBtnSection, bg_color="transparent", fg_color="green", text="Next", corner_radius=20, width=50, image=nextIcon, compound='right')
        self.paginationNextBtn.bind("<Button-1>", partial(self.__paginateNext, self.paginationNextBtn))
        self.paginationNextBtn.grid(row=0, column=3, sticky="nsew")


        self.paginationEmpty = customtkinter.CTkFrame(master=self.paginationFrameLeft, bg_color="transparent", fg_color="transparent", height=10, width=750)
        self.paginationEmpty.grid(row=0, column=0, sticky="new")

        self.paginationRowCountSection = customtkinter.CTkFrame(master=self.paginationFrameLeft, bg_color="transparent", fg_color="transparent", width=750)
        self.paginationRowCountSection.grid_rowconfigure(0, weight=1)
        self.paginationRowCountSection.grid_columnconfigure (0, weight=1)
        self.paginationRowCountSection.grid(row=1, column=0, sticky="nsew")

        self.paginationRowCountFirstBtn = customtkinter.CTkOptionMenu(master=self.paginationRowCountSection, fg_color="#2E2E2E", button_color="#2E2E2E",values=['50 rows', '100 rows', '200 rows', '500 rows', '1000 rows', 'show all rows'], command=self.__changeDisplayRowCount)
        self.paginationRowCountFirstBtn.set(f"{self.maxRowCountPerPage} rows")
        self.paginationRowCountFirstBtn.grid(row=0, column=0, sticky="ne")

    def __changeDisplayRowCount (self, choice):
        if choice != "show all rows":
            option = choice.split(' ')
            self.maxRowCountPerPage = int(option[0])
        else:
            self.maxRowCountPerPage = self.rowCount
            return self.__openMaxRowCountWindow ()
        
        self.__removeTableSection ()
        self.__showTableSection ()
        # update data
        self.showTableData(self.SQLData)
    
    def __openMaxRowCountWindow (self):
        if self.maxRowCountWindow is None or not self.maxRowCountWindow.winfo_exists():
            self.maxRowCountWindow = ShowAllRowsConfirmationWindows.Index ()
            self.maxRowCountWindow.setCallback(self.__openMaxRowCountWindowCallback)
        else:
            self.maxRowCountWindow.focus()  # if window exists focus it

    def __openMaxRowCountWindowCallback (self, topWindow, results = None):
        topWindow.destroy ()
        self.__changeDisplayRowCount (f"{self.rowCount} rows")

    def __removeTableStatusSection (self):
        self.TableStatusFrame.destroy ()

    def __removeTableSection(self):
        try:
            self.tableDataFrame.destroy ()
        except Exception:
            pass

        return self

    def __showTableSection (self):
        self.tableDataFrame = CTkXYFrame(self.midFrame)
        self.tableDataFrame.configure(height=470)
        self.tableDataFrame.grid_rowconfigure(0, weight=1)
        self.tableDataFrame.grid_columnconfigure (0, weight=1)
        self.tableDataFrame.grid(row=2, column=0, padx="0", pady="0", sticky="nsew")

    def __startTableThread (self):
        # load progress
        self.ProgressBar = ProgressBar.Index ()
        self.ProgressBar.setTargetComponent (self.topFrame).start ()

        # parse SQL
        self.tableThreadEvent   = threading.Event()
        self.tableThread        = threading.Thread(target=self.__executeInitialSQL, daemon=True)
        self.tableThread.start ()

    def __paginateFirst (self, target, e):
        if(target.cget("state") == "normal"):
            self.currentPage = 1
            target.configure(state="disabled")
            self.showTableData(self.SQLData)
    
    def __paginateLast (self, target, e):
        if(target.cget("state") == "normal"):
            self.currentPage = self.totalPages
            target.configure(state="disabled")
            self.showTableData(self.SQLData)

    def __paginateNext (self, target, e):
        if(target.cget("state") == "normal"):
            self.currentPage += 1
            target.configure(state="disabled")
            self.showTableData(self.SQLData)
    
    def __paginatePrev (self, target, e):
        if(target.cget("state") == "normal") and self.currentPage > 1:
            self.currentPage -= 1
            target.configure(state="disabled")
            self.showTableData(self.SQLData)
    
    def showTableData (self, data):
        if data == None: return
        __maxRows       =   self.maxRowCountPerPage
        __startIndex    =   0 if self.currentPage == 1 else (__maxRows * (self.currentPage-1))
        __data          =   []

        if 'executionTime' in data: self.executionTime  =   data['executionTime']
        if 'rowCount' in data: self.rowCount = data['rowCount']
        if 'rows' in data:
            for rowIndex in range(__maxRows):
                if((rowIndex + __startIndex) < (__maxRows + __startIndex)): 
                    if((rowIndex + __startIndex) < self.rowCount + 1):
                        try:
                            __data.append(data['rows'][__startIndex+rowIndex])
                        except:
                            pass

        if self.rowCount < 1 : __data = [[]]

        # prevent old data from showing
        if self.dataTable: self.dataTable.destroy ()
        
        self.dataTable = CTkTable(master=self.tableDataFrame, justify="left", header_color="#3C703B", hover_color="#2E2E2E", values=__data)
        #table.edit_row(0, text_color = '#2E2E2E')
        self.dataTable.grid(row=0, column=0, padx="0", pady="0", sticky="new")
 
        # compute total pages
        self.totalPages = math.ceil(self.rowCount / __maxRows)
        self.__removeTableStatusSection ()
        self.__showTableStatusSection ()
        self.__showPaginationSection ()
        self.ProgressBar.stop ()


    def getTableThread (self):
        if self.SQLData != None:
            return self.SQLData
        elif self.tableThread and not self.tableThread.is_alive():
            return None
        else:
            return None

    def __executeInitialSQL (self):
        #self.__showProgressBar ().start ()
        self.engine.useDatabase (self.databaseName)
        self.engine.parse(self.SQL)

        self.rowCount   =   self.engine.getRowCount ()
        __rowCount      =   self.rowCount
        self.SQLData    =   None
        __headers       =   []
        __data          =   []
  
        if __rowCount > 0:
            __rows = self.engine.getRows ()

            for rowIndex in range(__rowCount):
                __currentData = []
                for name in __rows[rowIndex]:
                    # get header once
                    if rowIndex == 0:
                        __headers.append(name)
                        __currentData.append(__rows[rowIndex][name])
                    else:
                        __currentData.append(__rows[rowIndex][name])
                
                if rowIndex == 0: __data.append(__headers)
                # add to data
                __data.append(__currentData)
        print(self.rowCount)    
        self.SQLData = {"rowCount": __rowCount , "rows": __data, "executionTime": self.engine.getExecutionTime ()}
        return self.SQLData

    def __executeSQLFromTextArea (self, e):
        __query             =   self.SQLQueryTextBox.get("0.0", "end")
        self.SQLError       =   None
        self.tableThread    =   None
        self.currentPage    =   1
        
        # prevent empty command
        if not __query: return self
        if len(__query.strip ()) < 1: return self

        # clear other threads
        self.tableThreadEvent.clear()
        self.tableThreadEvent.set()

         # load progress
        self.ProgressBar = ProgressBar.Index ()
        self.ProgressBar.setTargetComponent (self.topFrame).start ()

       
        #self.tableThread    =   None
        self.SQL            =   __query.strip ()
        self.mustContinue   =   False
  
        self.engine.useDatabase (self.databaseName)
        
        try:
            self.engine.parse(self.SQL)
            if self.engine.error == None:
                self.mustContinue   =   True
                self.SQlError       =   None

        except Exception as e:
            self.mustContinue   =   False
        

        if not self.mustContinue:
            self.ProgressBar.stop ()
            self.SQL        =   None
            self.SQlError   =   self.engine.error['error']
            self.__showSQLQueryStatusBox ()
            return
        

        if self.mustContinue:
            self.rowCount           =   self.engine.getRowCount ()
            self.maxRowCountPerPage =   50
            __rowCount              =   self.rowCount
            self.SQLData            =   None
            __headers               =   []
            __data                  =   []
    
            if __rowCount > 0:
                __rows = self.engine.getRows ()
    
                for rowIndex in range(__rowCount):
                    __currentData = []
                    for name in __rows[rowIndex]:
                        # get header once
                        if rowIndex == 0:
                            __headers.append(name)
                            __currentData.append(__rows[rowIndex][name])
                        else:
                            __currentData.append(__rows[rowIndex][name])
                    
                    if rowIndex == 0: __data.append(__headers)
                    # add to data
                    __data.append(__currentData)
            

            if self.engine.getOperation () == 'select':
                self.SQLData    =   {"rowCount": __rowCount , "rows": __data, "executionTime": self.engine.getExecutionTime ()}

                # show table
                self.showTableData (self.SQLData)
                self.SQLQueryTextBoxStatusFrame.destroy ()
                self.__showSQLQueryStatusBox ()
            else:
                time.sleep(1)
                # do a refresh
                self.__executeInitialSQL ()
                self.ProgressBar.stop ()


        return self
        




