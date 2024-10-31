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
        self.CSVReader      =   None
        self.__readJSONFile (dbFile)

    def __readJSONFile (self, dbFile):
        # throw an error if file does not exists
        try:
            # open file
            self.file  =   open(dbFile, mode='r')

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
                    __newNextRow[self.headers[headerCount]] = __nextRow[headerCount]

            # return next data
            return __newNextRow

        except Exception as e:
           return None

    
    def close (self):
        try:
            self.file.close()
        except Exception:
            pass

        return self
