import sys
import os
import pandas as pd

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

class SchemaTableFileWriter :
    def __init__ (self, tableFullPath):
        self.headers        =   []
        self.rows           =   []
        self.results        =   {}
        self.file           =   {}
        self.rowIndexes     =   []
        self.fileExists     =   False
        self.tableName      =   None
        self.CSVReader      =   None
        self.renameHeader   =   True
        self.__readCSVFile (tableFullPath)

    def __readCSVFile (self, tableFullPath):
        # throw an error if file does not exists
        try:
            self.fileExists = os.path.exists(tableFullPath)

            if self.fileExists :
                self.file = tableFullPath
            else:
                self.results = { "error" : f"{e}"}

        except Exception as e:
            self.results = { "error" : f"{e}"}
        
        return self
    

    def isFileExists (self):
        return self.fileExists
    
    def addRowIndex (self, rowIndex):
        self.rowIndexes.append(rowIndex)
        
    def removeRow (self, rowNumbers = None):
        if "error" in self.results: return self

        docs    = pd.read_csv(self.file)
        
        if not rowNumbers == None:
            if len(rowNumbers)  > 0:
                for rowNumber in rowNumbers:
                    docs    = docs.drop(docs.index[rowNumber])
        else:
            docs    = docs.drop(self.rowIndexes)


        docs.to_csv(self.file, index=False)  