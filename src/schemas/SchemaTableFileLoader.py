import sys
import os
import csv

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

class SchemaTableFileLoader :
    def __init__ (self, dbFile):
        self.headers        =   []
        self.rows           =   []
        self.results        =   {}
        self.file           =   {}
        self.tableName      =   None
        self.CSVReader      =   None
        self.renameHeader   =   True
        self.__readJSONFile (dbFile)

    def __readJSONFile (self, dbFile):
        # throw an error if file does not exists
        try:
            # get table name
            __baseFileName    =   os.path.basename(os.path.realpath(dbFile))
            if len(__baseFileName) > 0:
                __fileName = __baseFileName.split('.')
                if len(__fileName) > 0: self.tableName   =   __fileName[0]

            # open file
            self.file   =   open(dbFile, mode='r')

            # read database
            self.CSVReader  =    csv.reader(self.file)
            self.__loadTableFromCSV(self.CSVReader)

        except Exception as e:
            self.results = { "error" : f"{e}"}
        
        return self

    def __loadTableFromCSV (self, csvDB):
        self.headers    =   next(csvDB)
        self.rows       =   csvDB
        return self

    def nextRow (self):
        try:
            __nextRow = next(self.rows)
            __newNextRow    =   {}
            
            # returns data with respective CSV header
            for headerCount in range(len(self.headers)):
                if headerCount <= len(__nextRow):
                    __headerName    =   self.headers[headerCount]
                    # rename header
                    if self.renameHeader:
                        __headerName = f"{self.tableName}.{__headerName}"
                    __newNextRow[__headerName] = __nextRow[headerCount]

            # return next data
            return __newNextRow

        except Exception as e:
           return 'EOF'
    
    def reset (self):
        self.file.seek (1)

    
    def close (self):
        try:
            self.file.close()
        except Exception:
            pass

        return self
