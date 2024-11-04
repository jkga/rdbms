import customtkinter
import os
import sys
import threading
import math
import time
from tkinter import Tk
from PIL import Image
from dotenv import load_dotenv
from CTkTable import *

# load env variables
load_dotenv(dotenv_path=f'configs/.env')
databasePath = os.getenv('DATABASE_PATH')

# manual access to schema directory
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path,  '../../../' +  os.pardir)))
from engine.SQLQueryEngine import SQLQueryEngine
from ui.components.CTkXYFrame import *

# restore parent directory path
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

class Index:
    def __init__(self, root, engine, databaseName, tableName):
        self.engine                 =   engine
        self.databasePath           =   databasePath
        self.databaseName           =   databaseName
        self.tableName              =   tableName
        self.databases              =   {}
        self.SQLData                =   None
        self.SQL                    =   f"SELECT * FROM (SELECT * FROM {self.tableName}, STUDCOURSE WHERE STUDENT.StudNo='2007-52623' OR STUDCOURSE.AcadYear>2000 AND STUDCOURSE.CNo='COMM 10');"
        self.tabs                   =   f"       "
        self.footNote               =   "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat"
        self.projectLink            =   "https://github.com/UPLB-CMSC227/rdbms"
        self.mainFrame              =   customtkinter.CTkFrame(master=root, corner_radius=0, bg_color="transparent", fg_color="transparent")
        self.tableThread            =   None
        self.rowCount               =   0
        self.totalPages             =   0
        self.currentPage            =   1
        self.maxRowCountPerPage     =   50

        self.mainFrame = customtkinter.CTkFrame(master=root, bg_color="transparent", fg_color="transparent")
        self.mainFrame.grid_rowconfigure(2, weight=1)
        self.mainFrame.grid_columnconfigure (0, weight=1)
        self.mainFrame.grid(row=0, column=0, sticky="nsew")

        self.topFrame = customtkinter.CTkFrame(master=self.mainFrame, bg_color="blue", fg_color="transparent", height=50)
        self.topFrame.grid_rowconfigure(1, weight=1)
        self.topFrame.grid_columnconfigure (0, weight=1)
        self.topFrame.grid(row=0, column=0, sticky="nsew")

        self.midFrame = customtkinter.CTkFrame(master=self.mainFrame, bg_color="transparent", fg_color="transparent", height=750)
        self.midFrame.grid_rowconfigure(2, weight=1)
        self.midFrame.grid_columnconfigure (0, weight=1)
        self.midFrame.grid(row=1, column=0, sticky="nsew")

        self.bottomFrame = customtkinter.CTkFrame(master=self.mainFrame, bg_color="transparent", fg_color="transparent")
        self.bottomFrame.grid_rowconfigure(0, weight=0)
        self.bottomFrame.grid_columnconfigure (0, weight=0)
        self.bottomFrame.grid(row=2, column=0, sticky="nsew")

        self.__showHeader ()
        self.__showHeaderTabs ()
        self.__showBody ()
        self.__showSQLQueryTextBox ()
        #self.__showSQLQueryStatusBox ()
        self.__showTableStatusSection ()
        self.__showTableSection ()
    
    def __showProgressBar (self):
        self.progressFrame = customtkinter.CTkFrame(master=self.topFrame, bg_color="transparent", fg_color="transparent", height=2)
        self.progressFrame.grid_rowconfigure(0, weight=1)
        self.progressFrame.grid_columnconfigure (0, weight=1)
        self.progressFrame.grid(row=0, column=0, padx="0", pady="0", sticky="nsew")

        self.progressbar = customtkinter.CTkProgressBar(master=self.progressFrame, progress_color="#333333")
        self.progressbar.grid(row=0, column=0, sticky="nsew")
    
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
        self.bodyFrame = customtkinter.CTkFrame(master=self.midFrame, bg_color="transparent", fg_color="transparent")
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
        self.SQLQueryTextBoxBtnFrame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")


        self.SQLQueryTextBoxExecuteBtn = customtkinter.CTkButton(master=self.SQLQueryTextBoxBtnFrame, bg_color="transparent", fg_color="#505050", hover_color="#707070", text="Execute", corner_radius=50)
        self.SQLQueryTextBoxExecuteBtn.bind("<Button-1>", self.__executeSQLFromTextArea)
        self.SQLQueryTextBoxExecuteBtn.grid(row=0, column=1, sticky="se")

    def __showSQLQueryStatusBox (self):
        self.SQLQueryTextBoxStatusFrame = customtkinter.CTkFrame(master=self.SQLQueryTextBoxBtnFrame, bg_color="transparent", fg_color="transparent", width=850, height=30, corner_radius=50)
        self.SQLQueryTextBoxStatusFrame.grid_rowconfigure(0, weight=1)
        self.SQLQueryTextBoxStatusFrame.grid_columnconfigure (4, weight=1)
        self.SQLQueryTextBoxStatusFrame.grid(row=0, column=0, sticky="nsew")

        #self.SQLQueryTextBoxStatusBoxFrame = customtkinter.CTkLabel(master=self.SQLQueryTextBoxStatusFrame, text="", bg_color="red", fg_color="red", width=830, corner_radius=50)
        #self.SQLQueryTextBoxStatusBoxFrame.grid_rowconfigure(0, weight=1)
       # self.SQLQueryTextBoxStatusBoxFrame.grid_columnconfigure (2, weight=1)
        #self.SQLQueryTextBoxStatusBoxFrame.grid(row=0, column=0, sticky="nsew")

        self.SQLQueryStatusText = customtkinter.CTkLabel(master=self.SQLQueryTextBoxStatusFrame, text=" ", bg_color="transparent", fg_color="transparent")
        self.SQLQueryStatusText.grid(row=0, column=0, sticky="nsew")

        self.SQLQueryStatusText = customtkinter.CTkLabel(master=self.SQLQueryTextBoxStatusFrame, text=" ", bg_color="transparent", fg_color="transparent")
        self.SQLQueryStatusText.grid(row=0, column=1, sticky="nsew")

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


        self.tableText = customtkinter.CTkLabel(master=self.TableStatusFrameLeft, text=f"[{self.databaseName}/{self.tableName}]", bg_color="transparent", fg_color="transparent", font=customtkinter.CTkFont(size = 16), justify="left", anchor="w", text_color="#C3C3C3", width=500)
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

    def __showTableSection (self):
        self.tableDataFrame = CTkXYFrame(self.midFrame)
        self.tableDataFrame.configure(height=450)
        self.tableDataFrame.grid_rowconfigure(0, weight=1)
        self.tableDataFrame.grid_columnconfigure (0, weight=1)
        self.tableDataFrame.grid(row=2, column=0, padx="0", pady="0", sticky="nsew")

        # parse SQL
        self.tableThread  = threading.Thread(target=self.__executeInitialSQL, daemon=True)
        self.tableThread.start ()

    
    def showTableData (self, data):
        if data == None: return
        
        __maxRows       =   self.maxRowCountPerPage
        __startIndex    =   0 if self.currentPage == 1 else (__maxRows * self.currentPage)
        __data          =   []

        if 'rowCount' in data: self.rowCount = data['rowCount']
        if 'rows' in data:
            for rowIndex in range(__maxRows):
                if(rowIndex + __startIndex < __maxRows + __startIndex): 
                    if(rowIndex + __startIndex < self.rowCount):
                        __data.append(data['rows'][rowIndex])
                
            # add all entries
            table = CTkTable(master=self.tableDataFrame, justify="left", header_color="#3C703B", hover_color="#2E2E2E", values=__data)
            #table.edit_row(0, text_color = '#2E2E2E')
            table.grid(row=0, column=0, padx="0", pady="0", sticky="nsew")
        
        # compute total pages
        self.totalPages = math.ceil(self.rowCount / __maxRows)
        self.__showTableStatusSection ()

    def getTableThread (self):
        if self.SQLData != None:
            return self.SQLData
        elif self.tableThread and not self.tableThread.is_alive():
            return None
        else:
            return None

    def __executeInitialSQL (self):

        self.engine.useDatabase (self.databaseName)
        self.engine.parse(self.SQL)

        __rowCount = self.engine.getRowCount ()
        __headers = []
        __data = []
        
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
            
        self.SQLData = {"rowCount": __rowCount , "rows": __data, "executionTime": self.engine.getExecutionTime ()}
        return self.SQLData

    def __executeSQLFromTextArea (self, e):
        __query     =   self.SQLQueryTextBox.get("0.0", "end")
        self.SQL    =   __query.strip ()

        # parse SQL
        self.tableThread  = threading.Thread(target=self.__executeInitialSQL, daemon=True)
        self.tableThread.start ()

        while True:
            __tableThread = self.getTableThread ()

            if __tableThread is not None:
                self.showTableData(__tableThread)
                break
            elif self.tableThread.is_alive ():
                pass   
            else:
                pass
            
            time.sleep(1)
                




