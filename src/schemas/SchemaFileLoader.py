import sys
import os
import json

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

from schemas.SchemaGenerator import SchemaGenerator

class SchemaFileLoader :
    def __init__ (self, dbFile):
        self.results = {}
        self.__readJSONFile (dbFile)

    def __readJSONFile (self, dbFile):

        # throw an error if file does not exists
        try:
            with open(dbFile) as file:
                # read database
                db = json.load(file)
                self.__loadSchemaFromJSON (db)
        except Exception as e:
            self.results = { "error" : f"{e}"}
        
        return self

    def __loadSchemaFromJSON (self, jsonDB):
        
        if 'schema' in jsonDB:
            self.schema =   SchemaGenerator (name = jsonDB['schema'])

            # add tables
            if 'tables' in jsonDB:
                for table in jsonDB['tables']:
                    # add table and other properties
                    self.schema.addTable (jsonDB['tables'][table]['name'])
                    if 'info' in jsonDB['tables'][table] : self.schema.updateRowCount (jsonDB['tables'][table]['name'], jsonDB['tables'][table]['info']['rowCount'])

                    # add columns
                    if 'columns' in jsonDB['tables'][table]:
                        for column in jsonDB['tables'][table]['columns']:
                            self.schema.addColumns (jsonDB['tables'][table]['name'], [jsonDB['tables'][table]['columns'][column]])

        self.results = {'schema' : self.schema}

        return self

    def getResults (self):
        return self.results
