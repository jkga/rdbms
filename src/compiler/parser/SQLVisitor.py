# Generated from ./src/parser/SQL.g4 by ANTLR 4.13.2
from antlr4 import *
import pprint

if "." in __name__:
    from .SQLParser import SQLParser
else:
    from SQLParser import SQLParser

# This class defines a complete generic visitor for a parse tree produced by SQLParser.

class SQLVisitor(ParseTreeVisitor):

    def __init__(self):
        super().__init__()
        self.schema = None
        self.errors = []
        self.annotations = {}
        self.debug = False

    def loadSchema (self, Schema):
        if Schema != None:
            self.schema = Schema() if callable(Schema) else Schema
    
    def debugData (self, data, query = ''):
        if data and self.debug:
            print("\r\n---------ORIGINAL QUERY--------------------")
            print(f"({query})")
            print("-------------------------------------------\r\n")
            print("---------DEBUG START-----------------------")
            pprint.PrettyPrinter(indent=1).pprint(data)
            print('---------DEBUG END-------------------------')
    
    def setDebug (self, allowDebug = False):
        if allowDebug:
            self.debug = True
        else:
            self.debug = False
        
        return self

    # Visit a parse tree produced by SQLParser#sql_statement.
    def visitSql_statement(self, ctx:SQLParser.Sql_statementContext):
        select_statement = ctx.select_statement ()
        delete_statement = ctx.delete_statement()
        insert_statement = ctx.insert_statement()

        select_list_nodes = []
        delete_list_nodes = []
        insert_list_nodes = []

        # select statement
        if isinstance(select_statement, list):
            for select in select_statement:
                select_list_nodes.append(self.visit(select))
        else:
            select_list_nodes.append(self.visit(select_statement))
        
        # delete statement
        if isinstance(delete_statement, list):
            for delete in delete_statement:
                delete_list_nodes.append(self.visit(delete))
        else:
            delete_list_nodes.append(self.visit(delete_statement))

        # insert statement
        if isinstance(insert_statement, list):
            for insert in insert_statement:
                insert_list_nodes.append(self.visit(insert))
        else:
            insert_list_nodes.append(self.visit(insert_statement))
                        
        return {
            'select_statement'  :   select_list_nodes,
            'delete_statement'  :   delete_list_nodes,
            'insert_statement'  :   insert_list_nodes,
        }


    # Visit a parse tree produced by SQLParser#select_statement.
    def visitSelect_statement(self, ctx:SQLParser.Select_statementContext):
        select_tables = ctx.table_list()
        select_columns = ctx.column_list ()
        where_clause = ctx.where_clause ()

        table_list_nodes = []
        column_list_nodes = []
        select_list_nodes = []
        where_list_nodes = []

        table_list_name = []
   
        
        # list tables
        if isinstance(select_tables, list):
            for select in select_tables:
                table_list_nodes.append(self.visit(select))
        else:
            table_list_nodes.append(self.visit(select_tables))


        # list of columns
        if isinstance(select_columns, list):
            
            for columns in select_columns:
                column_list_nodes.append(self.visit(columns))
        else:
            column_list_nodes.append(self.visit(select_columns))
        
        # get all VALID table names in string and push to list        
        for tb in table_list_nodes:
            for name in tb:
                if tb[name]['valid']:
                    table_list_name.append(name)

        # get all columns
        for cl in column_list_nodes:
            for name in cl:       
                # use cl[name]["name"] instead of name since the namee field might contain different
                # format such as table.column
                if cl[name]["type"] == "string":
                    cl[name]["error"] = None
                    cl[name]["valid"] = True

                if cl[name]["type"] == "table":
                    if ("tableName" and "columnName") in cl[name]:
                        tableName = cl[name]["tableName"]
                        columnName = cl[name]["columnName"]
                        
                        if self.schema.isTableExists (tableName):
                            if self.schema.isColumnExists (tableName, columnName):
                               if tableName in table_list_name:
                                    #cl[name]["error"] = f"Column name [{name}] does not exist in [{tableName}]"
                                    #cl[name]["valid"] = False   
                                    cl[name]["error"] = None
                                    cl[name]["valid"] = True
   
                if cl[name]["type"] == "column":
                    # get all fields in database if * is given
                    if not cl[name]['name'] == '*':
                        existsInTables = []
                        
                        for tl in table_list_name:
                            if self.schema.isColumnExists (tl, name):
                                # convert regular columName to table.columnName format to allow
                                # matching of parent columns to the columns of its subquery
                                cl[name]["name"] = f"{tl}.{name}"
                                cl[name]["tableName"] = f"{tl}"
                                cl[name]["columnName"] = f"{name}"
                                cl[name]["error"] = None
                                cl[name]["valid"] = True
                                existsInTables.append(tl)
                            else:
                                cl[name]["error"] = f"Column name [{name}] does not exist in table [{tl}]"
                                cl[name]["valid"] = False
                        
                        # if the column name exists in multiple tables, it is considered ambigous
                        # unless the tableName is explicitely specified
                        # SELECT id FROM student_info, enrollment
                        if len (existsInTables) > 1:
                            cl[name]["error"] = f"Column name [{name}] is ambigous"
                            cl[name]["valid"] = False
                    
                    else:
                        # get all fields from the database
                        # SELECT * from database
                        newColumnList = []

                        for table in table_list_nodes:
                            for name in table:
                                if table[name]['valid']:
                                    cols = self.schema.getColumns (name)
                                    
                                    for colName in cols:
                                        col = {}
                                        col[colName] = {}
                                        col[colName]['name'] = f"{name}.{colName}"
                                        col[colName]['valid'] = True
                                        col[colName]['error'] = None
                                        col[colName]['type'] = 'table'
                                        col[colName]['columnName'] = colName
                                        col[colName]['tableName'] = name
                                        newColumnList.append(col)

                        # replace * with all columns
                        if len(newColumnList) > 0:
                            column_list_nodes = newColumnList
                       

        # where clause
        if isinstance(where_clause, list):
            for where in where_clause:
                if where != None:
                    where_list_nodes.append(self.visit(where))
        else:
            if where_clause == None:
                pass
            else:
                where_list_nodes.append(self.visit(where_clause))
        
        # check if column exists in table
        existsInTables = []
        for where_list in where_list_nodes:
            for condition_list in where_list["condition_list"]:
                for expression_list in condition_list["expression_list"]:
                    for name in expression_list['column']:
                        for tl in table_list_name:

                            # compare where clause to [name] with columns:[table.name, table.age]
                            if expression_list['column'][name]['type'] == 'table':
                                tableColumn = expression_list['column'][name]['name'].split('.')

                                if len (tableColumn) >=2:
                                    if self.schema.isColumnExists (tl, tableColumn[1]):
                                        expression_list['column'][name]["error"] = None
                                        expression_list['column'][name]["valid"] = True
                            else:
                                if self.schema.isColumnExists (tl, name):
                                    # this ensures that the column name in WHERE clause will not be ambigous
                                    if name in existsInTables:
                                        expression_list['column'][name]["error"] = f"Column [{name}] is ambigous"
                                        expression_list['column'][name]["valid"] = False
                                    else:
                                        expression_list['column'][name]["error"] = None
                                        expression_list['column'][name]["valid"] = True
                                        existsInTables.append(name)

                                        #convert to table type
                                        expression_list['column'][name]['name'] =   f"{tl}.{name}"
                                        expression_list['column'][name]['type'] =   "table"
                                        expression_list['column'][name]['tableName']    =   tl
                                        expression_list['column'][name]['columnName']   =   name
        # get subqueries
        select_statements_nodes = ctx.select_statement()
        for select_statement in select_statements_nodes:
            if isinstance(select_statement, list):
                pass
            else:
               select_list_nodes.append(self.visit(select_statement))
        
        
        # ensure that column exists in subquery
        # for instance, the select statement below will produce an empty table_list
        # since it has been replaced with subquery
        # SELECT a, b, name, 'test' FROM (SELECT name from student_info);

        subquery_column_name = []
        for subquery_select_node in select_list_nodes:
            for column in subquery_select_node['column_list']:
                for name in column:
                    # if column[name]['valid'] == True:
                    # use the property ["name"] instead of name since the name field might contain different
                    # format such as table.column
                    subquery_column_name.append(column[name])

        # get all columns from parent query and match to subquery if there is no table
        if(len(table_list_name) <= 0):
            for col in column_list_nodes:
                for name in col:

                    if col[name]['type'] == 'string':
                        # do nothing since string by default in column_list  is valid
                        col[name]["error"] = None
                        col[name]["valid"] = True
                    else:
                        existsInTables = []
                        
                        for query in subquery_column_name:
                            if query['type'] == 'string':
                                # string column_list must always be valid
                                col[name]["error"] = None
                                col[name]["valid"] = True
                            else:

                                if name == '*':
                                    #col[name]["error"] = None
                                    #col[name]["valid"] = True
                                    newColumnList = []

                                    if len(subquery_column_name) > 0:
                                        for sq in subquery_column_name:
                                            col = {}
                                            col[sq['name']] = sq
                                            newColumnList.append(col)

                                        # replace * with all columns
                                        column_list_nodes = newColumnList
                                else:

                                # column type = table
                                    if col[name]['type'] == 'table':
                                        if col[name]['name'] == query['name']:
                                            col[name]["error"] = None
                                            col[name]["valid"] = True
                                            existsInTables.append (query['name'])

                                    else:
                                        # get column name in the table.column to match columnName
                                        # columnName = name
                                        # student.name
                                        tableColumn = query['name'].split('.')
                                        if len (tableColumn) >=2:
                                            if col[name]['name'] == tableColumn[1]:
                                                col[name]["error"] = None
                                                col[name]["valid"] = True
                                                existsInTables.append (query['name'])
                            
    
                            
                        # this ensures that the column name will not be ambigous
                        # columnName = name
                        # ['student_enrollment.name', 'student_info.name']                
                        if len(existsInTables) > 1:
                            col[name]["error"] = f"Column [{col[name]['name']}] is ambigous"
                            col[name]["valid"] = False

        if len(select_list_nodes) > 0:
            # verify clause if column exists
            for where_nodes in where_list_nodes:
                for condition_list in where_nodes['condition_list']:
                    for expression in condition_list['expression_list']:
                        for expressionName in expression['column']:
                            existsInColumns = []
                            # read all columns and compare to conditions
                            for col in column_list_nodes:
                                for name in col:

                                    # for an expression of col = value
                                    # ensure that it will match all the columns in the list 
                                    # example: name in [table1.name, table2.name]
                                    if expression['column'][expressionName]['type'] == 'column':
                                        # compare where clause to [name] with columns:[table.name, table.age]
                                        if col[name]['type'] == 'table':
                                            tableColumn = col[name]['name'].split('.')

                                            if len (tableColumn) >=2:
                                                if expression['column'][expressionName]['name'] == tableColumn[1]:
                                                    # put it the the list of matched column
                                                    existsInColumns.append(col[name]['name'])
                                                    #convert where clause column to table type
                                                    expression['column'][expressionName]['name']         =   f"{tableColumn[0]}.{tableColumn[1]}"
                                                    expression['column'][expressionName]['type']         =   "table"
                                                    expression['column'][expressionName]['tableName']    =   tableColumn[0]
                                                    expression['column'][expressionName]['columnName']   =   tableColumn[1]
                                        else:
                                            # if column is not a table, match the whole name
                                            if col[name]['name'] == expression['column'][expressionName]['name']:
                                                existsInColumns.append(col[name]['name'])
                                        
                                    else:
                                        # for wehere clause with table.column format
                                        # where student_info.name='test'
                                        if col[name]['name'] == expression['column'][expressionName]['name']:
                                            existsInColumns.append(col[name]['name'])
                                        

                            
                            # this ensure that column will not be ambigous
                            # columnName = name
                            # ['student_enrollment.name', 'student_info.name']    
                            if len(existsInColumns) == 0 :
                                expression['column'][expressionName]["error"] = f"Column name [{expressionName}] does not exist"
                                expression['column'][expressionName]["valid"] = False

                            elif len(existsInColumns) == 1 :
                                
                                expression['column'][expressionName]["error"] = None
                                expression['column'][expressionName]["valid"] = True
                            else:
                                expression['column'][expressionName]["error"] = f"Column name [{expressionName}] is ambigous"
                                expression['column'][expressionName]["valid"] = False
                                

        # return data
        data = {
            'table_list'    :   table_list_nodes,
            'column_list'   :   column_list_nodes,
            'where_clause'  :   where_list_nodes,
            'subquery'      :   select_list_nodes,
        }
        
        self.debugData (data, ctx.getText())

        return data

    # Visit a parse tree produced by SQLParser#delete_statement.
    def visitDelete_statement(self, ctx:SQLParser.Delete_statementContext):
        delete_tables = ctx.table_list ()
        where_clause = ctx.where_clause ()

        table_list_nodes = []
        where_list_nodes = []
        table_list_name = []

        # list tables
        if isinstance(delete_tables, list):
            for select in delete_tables:
                table_list_nodes.append(self.visit(select))
        else:
            table_list_nodes.append(self.visit(delete_tables))

        
        # get all VALID table names in string and push to list        
        for tb in table_list_nodes:
            for name in tb:
                if tb[name]['valid']:
                    table_list_name.append(name)  

        # where clause
        if isinstance(where_clause, list):
            for where in where_clause:
                if where != None:
                    where_list_nodes.append(self.visit(where))
        else:
            if where_clause == None:
                pass
            else:
                where_list_nodes.append(self.visit(where_clause))
        
        # verify clause if column exists
        for where_nodes in where_list_nodes:
            for condition_list in where_nodes['condition_list']:
                for expression in condition_list['expression_list']:
                    for expressionName in expression['column']:
                        for tb in table_list_name:
                                # for an expression of col = value
                                # ensure that it belongs to the table
                                # example: table.name in [table1, table2]
                                if expression['column'][expressionName]['type'] == 'table':
                                    
                                    tableColumn = expression['column'][expressionName]['name'].split('.')

                                    if len (tableColumn) >=2:
                                        if self.schema.isColumnExists(tb, tableColumn[1]):
                                            expression['column'][expressionName]['error'] = None
                                            expression['column'][expressionName]['valid'] = True
                                else:
                                    # column name does not contain a table information
                                    # thus, just confirm its existence
                                    if self.schema.isColumnExists(tb, expression['column'][expressionName]['name']):
                                        expression['column'][expressionName]['error'] = None
                                        expression['column'][expressionName]['valid'] = True

        data = {
            'table_list'    :   table_list_nodes,
            'where_clause'  :   where_list_nodes,
        }

        self.debugData (data)

        return data


    # Visit a parse tree produced by SQLParser#insert_statement.
    def visitInsert_statement(self, ctx:SQLParser.Insert_statementContext):
        insert_table = ctx.table_list()
        insert_column_list = ctx.insert_column_list()
        insert_value_list = ctx.values_list()

        table_list_nodes = []
        column_list_nodes = []
        value_list_nodes = []
        table_names = []
        

        # list tables
        if isinstance(insert_table, list):
            for table in insert_table:
                table_list_nodes.append(self.visit(table))
        else:
            table_list_nodes.append(self.visit(insert_table))

        # value list
        if isinstance(insert_value_list, list):
            for value in insert_value_list:
                value_list_nodes.append(self.visit(value))
        else:
            value_list_nodes = self.visit(insert_value_list)


        # get all names of tables
        for tables in table_list_nodes:
            for name in tables:
                table_names.append(name)
        
        # columns
        if isinstance(insert_column_list, list):
            for column in insert_column_list:
                column_list_nodes.append(self.visit(column))
        else:
            # do not traverse if column does not exist
            # note: column is optional in insert statement
            if not insert_column_list == None:
                column_list_nodes = self.visit(insert_column_list)

        # check column details if column list is given in the insert statement
        for column in column_list_nodes:
            for col in column:
                # check if it exists in all the tables
                for tableName in table_names:
                    # ensure that the colum name has no duplicate entry
                    if not column[col]['duplicate']:
                        columnDetails = self.schema.getColumnDetails (tableName, col)
                        if not columnDetails == None:
                            column[col]['error'] = None
                            column[col]['valid'] = True

        # if no column list is given, get all the columns from the schema
        if len(column_list_nodes) < 1:
            if len(table_names) >= 1:
                table_columns = self.schema.getColumns (table_names[0])
                table_total_count = 0
                
                for name in table_columns:
                    try:
                        # compare data types of the table and the values
                        for valName in value_list_nodes[table_total_count]:
                           dataType = table_columns[name]['type']

                           if not dataType == value_list_nodes[table_total_count][valName]['type']:
                            # show errors
                            value_list_nodes[table_total_count][valName]['error'] = f"Value [{valName}] must have a data type of [{dataType}][{name}]"
                            value_list_nodes[table_total_count][valName]['valid'] = False 


                    except IndexError:
                        # there are more columns in the table but the value specified is not equal to its length
                        # However, do not throw an error if the column is nullable
                        if table_columns[name]['nullable']:
                            pass
                        else:
                            # add to column list but put some errors
                            col = {
                                'name'  :   name,
                                'error' :   f"Column name [{name}] must not be empty",
                                'valid' :   False
                            }

                            column_list_nodes.append(col)

                    table_total_count += 1
            else:
                # returns an empty node if the table list is empty
                return {}
        else:
            # for insert statement with columns
            # INSERT INTO table (col1,col2, ...)
            # check column details and compare to values
            for column in column_list_nodes:

                table_column_total_count = 0

                for col in column:
                    if len(table_names) >= 1:
                        table_columns = self.schema.getColumnDetails (table_names[0], col)
                        try:
                            # compare data types and values
                            for valName in value_list_nodes[table_column_total_count]:
                                dataType = table_columns['type']
                                if not dataType == value_list_nodes[table_column_total_count][valName]['type']:
                                    # show errors
                                    value_list_nodes[table_column_total_count][valName]['error'] = f"Value [{valName}] must have a data type of [{dataType}][{col}]"
                                    value_list_nodes[table_column_total_count][valName]['valid'] = False 

                        except IndexError:
                            pass
                
                    table_column_total_count += 1
        
        # return data
        data = {
            'table_list'    :   table_list_nodes,
            'column_list'   :   column_list_nodes,
            'value_list'    :   value_list_nodes,
        }
        
        self.debugData (data, ctx.getText())

        return data


    # Visit a parse tree produced by SQLParser#table_list.
    def visitTable_list(self, ctx:SQLParser.Table_listContext):
        
        # check if table exists in the database
        self.annotations = {}

        for child in ctx.getChildren():
               # skp semicolon for multiple tables
               if not child.getText() == ',':
                    self.annotations[child.getText()] =  {
                        "name"  :  child.getText(),
                        "error" :  None,
                        "valid" :  True,
                    }

                    if not self.schema.isTableExists(child.getText()):
                        self.annotations[child.getText()] =  {
                            "name"  : child.getText(),
                            "error" : f"Table {child.getText()} not found",
                            "valid" : False,
                        }

        return self.annotations


    # Visit a parse tree produced by SQLParser#column_list.
    def visitColumn_list(self, ctx:SQLParser.Column_listContext):

        self.annotation = {}

        for column in ctx.getChildren():

                columns = column.getText().split(',')
                for columnName in columns:
                    self.annotation[columnName] =  {
                        "name"  : columnName,
                        "error" : f"Column name [{columnName}] does not exist",
                        "valid" : False,
                        "type"  : "column"
                    }

                    # if the columName is a string 
                    # example statement: SELECT "a"
                    if columnName[0] == "'" or columnName[0] == '"':
                        self.annotation[columnName]["type"] = "string"
                    else:
                        
                        # detect if the columName contains dot
                        # table.column
                        tableColumnName = columnName.split('.')
  
                        if len(tableColumnName) >= 2:
                            # check if column exists
                            self.annotation[columnName]["type"] = "table"
                            self.annotation[columnName]["tableName"] = tableColumnName[0]
                            self.annotation[columnName]["columnName"] = tableColumnName[1]

        return self.annotation


    # Visit a parse tree produced by SQLParser#values_list.
    def visitValues_list(self, ctx:SQLParser.Values_listContext):
        value_list = ctx.value ()
        value_list_nodes = []

        # list tables
        if isinstance(value_list, list):
            for value in value_list:
                value_list_nodes.append(self.visit(value))
        else:
            value_list_nodes.append(self.visit(value_list))

        return value_list_nodes


    # Visit a parse tree produced by SQLParser#insert_column_list.
    def visitInsert_column_list(self, ctx:SQLParser.Insert_column_listContext):
        column_list = ctx.column()
        column_list_nodes = []
        
        if isinstance(column_list, list):
            for column in column_list:
                column_list_nodes.append(self.visit(column))
        else:
            column_list_nodes.append(self.visit(column_list))

        # return data
        data = column_list_nodes
        
        self.debugData (data, ctx.getText())

        return data


    # Visit a parse tree produced by SQLParser#where_clause.
    def visitWhere_clause(self, ctx:SQLParser.Where_clauseContext):

        condition_list = ctx.condition_list()
        condition_list_nodes = []
        condition_logic_nodes = []

        for c in ctx.getChildren():
            if (str(type(c)).startswith("<class")):
                for x in range(c.getChildCount()):
                    if (c.getChild(x).getText().lower() == 'and') or (c.getChild(x).getText().lower() == 'or'):
                        condition_logic_nodes.append({
                            c.getChild(x).getText().upper(): { 
                                'name'  :   c.getChild(x).getText().upper(),
                                'valid' :   True,
                                'type'  :   'logic'
                            }
                       })

        if isinstance (condition_list, list):
            for conditions in condition_list:
                condition_list_nodes.append(self.visit(conditions))
        else:
            condition_list_nodes.append(self.visit(condition_list))
        
        return {
            "condition_list"    :   condition_list_nodes,
            "logic_list"        :   condition_logic_nodes
        }
            
    # Visit a parse tree produced by SQLParser#condition_list.
    def visitCondition_list(self, ctx:SQLParser.Condition_listContext):
        expression_list = ctx.expression ()
        expression_list_nodes = []

        if isinstance (expression_list, list):
            for expression in expression_list:
                expression_list_nodes.append(self.visit(expression))
        else:
            expression_list_nodes.append(self.visit(expression_list))
        
        return {
            "expression_list"    :   expression_list_nodes
        }

    # Visit a parse tree produced by SQLParser#expression.
    def visitExpression(self, ctx:SQLParser.ExpressionContext):
        column = ctx.column ()
        operator = ctx.operator ()
        value = ctx.value ()
        column_node = None
        operator_node = None
        value_node = None
        
        column_node = self.visit(column)
        operator_node = self.visit(operator)
        value_node = self.visit (value)
       
        return {
            "column"    :   column_node,
            "operator"  :   operator_node,
            "value"     :   value_node,
        }
    

    # Visit a parse tree produced by SQLParser#column.
    def visitColumn(self, ctx:SQLParser.ColumnContext):
        self.annotation = {}
        column_names = []

        for column in ctx.getChildren():
            
            # skip comma and return an empty array instead
            # this will prevent .split(',') function in returning two empty text ['', '']
            if column.getText() == ',':
                columns =  []
            else:
                columns = column.getText().split(',')

            for columnName in columns:
                self.annotation[columnName] =  {
                    "name"      :   columnName,
                    "error"     :   f"Column name [{columnName}] does not exist",
                    "valid"     :   False,
                    "type"      :   "column",
                    "duplicate" :   False
                }
                
                if len(columnName) > 0:
                    # if the columName is a string 
                    # example statement: SELECT "a"
                    if columnName[0] == "'" or columnName[0] == '"':
                        self.annotation[columnName]["type"] = "string"
                    else:
                    
                        # detect if the columName contains dot
                        # table.column
                        tableColumnName = columnName.split('.')
                        
                        if len(tableColumnName) >= 2:
                            # check if column exists
                            self.annotation[columnName]["type"] = "table"
                            self.annotation[columnName]["tableName"] = tableColumnName[0]
                            self.annotation[columnName]["columnName"] = tableColumnName[1]
                    

                    # column must not have a duplicate
                    # INSERT INTO TABLE (name, name)
                    if columnName in column_names:
                        self.annotation[columnName]["error"] = f"Duplicate entry for column name [{columnName}]"
                        self.annotation[columnName]["duplicate"] = True
                    else:
                        column_names.append(columnName)

                else:
                    pass


        return self.annotation


    # Visit a parse tree produced by SQLParser#value.
    def visitValue(self, ctx:SQLParser.ValueContext):

        self.annotation = {}
        name = ctx.getChild(0).getText()

        self.annotation[name] =  {
            "name"  :   name,
            "error" :   None,
            "valid" :   True,
            "type"  :   'string'
        }

        if not name[0] == "'":
            self.annotation[name]['type'] = 'integer'
        
        return self.annotation


    # Visit a parse tree produced by SQLParser#operator.
    def visitOperator(self, ctx:SQLParser.OperatorContext):
        self.annotation = {}
        self.annotation[ctx.getChild(0).getText()] =  {
            "name": ctx.getChild(0).getText(),
            "error": None,
            "valid": True,
        }
        return self.annotation



del SQLParser