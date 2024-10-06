class SchemaGenerator :
  def __init__ (self, **kwargs):
    self.name = ""
    self.tables = {}

    if "name" in kwargs:
      self.name = kwargs["name"]
    
    return self
  
  def addTable (self, name):
    # add table if not exists
    if not name in self.tables:
      self.tables[name] = {}
      self.tables[name]['columns'] = {}
    
    return self

  def addColumn (self, tableName, name, type, nullable = False):
    if tableName in self.tables:
      self.tables[tableName]['columns'][name] = {}
      self.tables[tableName]['columns'][name]['name'] = name
      self.tables[tableName]['columns'][name]['type'] = type
      self.tables[tableName]['columns'][name]['nullable'] = nullable
      
    return self

  def addColumns (self, tableName, columns):
    for column in columns:
      nullable = False
      
      # set nullable
      if 'nullable' in column:
        if column['nullable'] == True or column['nullable'] == 'true':
          nullable = True

      # add each entry    
      self.addColumn (tableName, column['name'], column['type'], nullable)

    return self
  
  def getColumns (self, tableName):
    if tableName in self.tables:
      return self.tables[tableName]['columns']
    
  def getColumnType (self, tableName, columnName):
    if columnName in self.tables[tableName]['columns']:
      return self.tables[tableName]['columns'][columnName]['type']
    return None

  def getColumnDetails (self, tableName, columnName):
    if columnName in self.tables[tableName]['columns']:
      return self.tables[tableName]['columns'][columnName]
    return None
  
  def isTableExists (self, tableName):
    if tableName in self.tables:
      return True
    return False

  def isColumnExists (self ,tableName, columnName):
    if columnName in self.tables[tableName]['columns']:
      return True
    return False
  
  def getDatabaseName (self):
    return self.name

  def getTables (self):
    return self.tables
  
  def info (self):
    return self