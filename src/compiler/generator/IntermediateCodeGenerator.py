import antlr4
import sys
import os
from antlr4 import *

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

class IntermediateCodeGenerator:
    def __init__ (self, annotations):  
        self.errors         =   []
        self.data           =   None
        self.annotations    =   annotations
        self.statement      =   {}
        
    def errorInvalidAnnotation (self):
        self.errors.append("Invalid annotation")
        return self

    def errorEmptyAnnotation (self):
        self.errors.append("No data in annotation tree")
        return self

    def getResults (self):
        return {
            'error'     :   self.errors,
            'data'      :   self.data
        }
    
    def generate (self):
        # annotation tree must be present, otherwise, stop traversal and show error instead
        if not isinstance(self.annotations, dict):
            self.errorInvalidAnnotation ()
            return self.getResults ()
        
        if not 'data' in self.annotations:
            self.errorEmptyAnnotation ()
            return self.getResults ()

        if 'select_statement' in self.annotations['data']:
            if len(self.annotations['data']['select_statement']) >= 1:
                self.statement = self.__readSelectStatement (self.annotations['data']['select_statement'])
        
        if 'delete_statement' in self.annotations['data']:
            if len(self.annotations['data']['delete_statement']) >= 1:
                self.statement = self.__readDeleteStatement (self.annotations['data']['delete_statement'])
        
        if 'insert_statement' in self.annotations['data']:
            if len(self.annotations['data']['insert_statement']) >= 1:
                self.statement = self.__readInsertStatement (self.annotations['data']['insert_statement'])
        
        # returns all the data and error if any
        return self.statement 
    
    def __readSelectStatement (self, statement):

        for stmt in statement:
            # returns a single table or
            table_list = self.__readTableList (stmt['table_list'])
            tbl = []

            if '__r__' in table_list:
                if len(table_list['__r__']) > 1:
                    for tb in table_list['__r__']:
                        tbl.append({
                            '__r__' :   tb,
                            'children' :   None
                        })
                else:
                    tbl.append({
                        '__r__' :   table_list['__r__'],
                        'children' :   None
                    })

            if len(tbl) > 1:
                where_clause = self.__readWhereClause (stmt['where_clause'], self.__crossJoin(tbl))
            else:
                if len(stmt['subquery']):
                    where_clause = self.__readWhereClause (stmt['where_clause'], self.__readSelectStatement(stmt['subquery'])) 
                else:
                    where_clause = self.__readWhereClause (stmt['where_clause'], tbl)
            
            column_list = self.__readColumnList (stmt['column_list'], where_clause)

            return column_list

    
    def __readDeleteStatement (self, statement):

        for stmt in statement:
            # returns a single table or
            table_list = self.__readTableList (stmt['table_list'])
            tbl = []

            if '__r__' in table_list:
                if len(table_list['__r__']) > 1:
                    for tb in table_list['__r__']:
                        tbl.append({
                            '__r__' :   tb,
                            'children' :   None
                        })
                else:
                    tbl.append({
                        '__r__' :   table_list['__r__'],
                        'children' :   None
                    })
                    
            if len(tbl) > 1:
                where_clause = self.__readWhereClause (stmt['where_clause'], self.__crossJoin(tbl))
            else:
                where_clause = self.__readWhereClause (stmt['where_clause'], tbl)

            return where_clause
        
    def __readInsertStatement (self, statement):

        for stmt in statement:
            # returns a single table or
            table_list = self.__readTableList (stmt['table_list'])
            value_list = self.__readValueList (stmt['value_list'])

            tbl = []

            if '__r__' in table_list:
                if len(table_list['__r__']) > 1:
                    for tb in table_list['__r__']:
                        tbl.append({
                            '__r__' :   tb,
                            'children' :   None
                        })
                else:
                    tbl.append({
                        '__r__' :   table_list['__r__'],
                        'children' :   None
                    })

                column_list = self.__readColumnList (stmt['column_list'], self.__union(tbl, value_list))

            return  column_list

    def __readColumnList (self, column_list, children = []):
        columns = []
        for column in column_list:
            for name in column:
                columns.append(column[name]['name'])
        
        return {
            '__π__' : columns,
            'children' : children
        }
        
    
    def __readWhereClause (self, where_clause, children = []):
        conditions = []
        condition_operators = []
        x = 0
        
        for whereClause in where_clause:
            for expressionList in whereClause['condition_list']:

                for expression in expressionList['expression_list']:

                    col = ''
                    op  = ''
                    val = ''

                    # column name
                    for colName in expression['column']:
                        col =  expression['column'][colName]['name']

                    # operator name
                    for operatorName in expression['operator']:
                        op  =   expression['operator'][operatorName]['name']

                     # value name
                    for valueName in expression['value']:
                        val =   expression['value'][valueName]['name']
                    
                    # add to list of conditions
                    conditions.append(f"{col}{op}{val}")
                
                if len(whereClause['logic_list']) >= 1:
                    if whereClause['logic_list'][x]:
                        for logicName in whereClause['logic_list'][x]:
                            condition_operators.append(f"{whereClause['logic_list'][x][logicName]['name']}")
                
                    
                # count condtion at the end
                x = x + 1

        return {'__Ω__'  : conditions, 'operators': condition_operators, 'children' : children}

    def __readValueList (self, value_list):
        values = []
        for value in value_list:
            for name in value:
                values.append (value[name]['name'].strip("'"))
        return values

    def __readTableList (self, table_list):
        tables = []
        for table in table_list:
            for name in table:
                tables.append (table[name]['name'])

        return {'__r__'  : tables, 'children' : None}
    
    def __crossJoin (self, table_list):
        return { '__x__' : table_list }

    def __union (self, table_list, value_list = []):
        return { '__u__' : table_list, '__t__' : value_list }



        
        