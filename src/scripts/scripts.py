import csv
import json

class Import:
    def __init__ (self):
        self.results = {}
        self.__importCSV()


    def __importCSV(self):
        data = []
        integer_types = ["UnitsEarned", "NoOfUnits", "HasLab", "MaxStud"]

        jsonData = self.__loadJSON()
        filename = input("Input path to CSV file: ")

        tableName = filename.split(".")
        tableName = tableName[0]

        if tableName not in jsonData["tables"]:
            self.results = {"error" : tableName + " is not a valid table name"}

            return self.results

        with open(filename, 'r') as file:
            columns = csv.DictReader(file).fieldnames

            for column in columns:
                if column.lower() not in jsonData["tables"][tableName]["columns"]:
                    self.results = {"error": column + " not a valid column name for table " + tableName}

                    return self.results
                
            csv_reader = csv.DictReader(file)
    
            for row in csv_reader:
                for column in row:
                    if column in integer_types:
                        row[column] = int(row[column])
                data.append(dict(row))
                
            self.results = {"data": data}
            return self.results
            

    def __loadJSON(self):
        with open('../../data/databases/students.db/students.db.json') as json_file:
            data = json.load(json_file)

            return data


test = Import()
print(test.results)