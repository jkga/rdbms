import os
import sys
import glob
import antlr4

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

from compiler.analyzer.SQLAnnotate import SQLAnnotate
from compiler.generator.IntermediateCodeGenerator import IntermediateCodeGenerator
from compiler.optimizer.SQLQueryTreeOptimizer import SQLQueryTreeOptimizer
from compiler.optimizer.SQLQueryPlan import SQLQueryPlan
from compiler.optimizer.SQLQueryCost import SQLQueryCost
from engine.SQLQueryPlanSelector import SQLQueryPlanSelector
from engine.SQLQueryPlanExecution import SQLQueryPlanExecution
from schemas.SchemaFileLoader import SchemaFileLoader

class SQLQueryEngine:
    def __init__(self):
        self.databasePath           =   None
        self.defaultDatabaseSchema  =   None
        self.tree                   =   None
        self.annotatedTree          =   None
        self.optimizedTrees         =   None
        self.plan                   =   None
        self.results                =   None
        self.error                  =   None

    def setDatabasePath (self, dbPath):
        self.databasePath   =   dbPath


    def showDatabases (self):
        databasesNames  =   []
        databases       =   glob.glob(f"{self.databasePath}/*.db")

        for database in databases:
            db      =   database.split('/')
            dbFile  =   db[-1]
            if len(dbFile) > 0:
                name = dbFile.split('.')
                if len(name) > 0:
                    databasesNames.append(name[0])

        return databasesNames

    def useDatabase (self, dbName):
        self.databaseName               =   dbName
        self.fileLoader                 =   SchemaFileLoader (f"{self.databasePath}/{self.databaseName}.db/{self.databaseName}.db.json")
        self.databaseSchemaInstance     =   self.fileLoader.getResults ()
    
        # set default database schema
        if 'schema' in self.databaseSchemaInstance: self.defaultDatabaseSchema = self.databaseSchemaInstance['schema']
        
        return self
    
    def showTables (self):
        return self.defaultDatabaseSchema.getTables ()

    def showColumns (self, tableName):
        return self.defaultDatabaseSchema.getColumns (tableName)
    
    def getResults (self):
        return self.results
    
    def getRowCount (self):
        if not 'rowCount' in self.results: return 0
        return self.results['rowCount']

    def getExecutionTime (self):
        if not 'executionTime' in self.results: return 0
        return self.results['executionTime']
    
    def getRows (self):
        if not 'rows' in self.results: return 0
        return self.results['rows']
    
    def parse (self, SQL):
        try:
            self.error  =   None
            inputStream = antlr4.InputStream(SQL)
            sqlAnnotate = SQLAnnotate(sql = inputStream, schema = self.defaultDatabaseSchema)
            sqlAnnotate.annotate()
            self.annotatedTree   = sqlAnnotate.getAnnotations()

            if self.annotatedTree['error'] == None:
                self.__generateIntermediateCode(self.annotatedTree)
            else:
                self.error  =   self.__generateError ('SYNTAX ERROR', self.annotatedTree['error'])
                
        except Exception as e:
            self.error  =   self.__generateError ('INTERMEDIATE CODE', e)

        return self
        
    def __generateIntermediateCode (self, tree):
        if tree['error'] == None:
            try:
                code        =   IntermediateCodeGenerator (tree)
                self.tree   =   code.generate().getResults()
                self.__optimizeTree (self.tree)

            except Exception as e:
                self.error  =   self.__generateError (e)
        else:
            self.error  =   self.__generateError ('SEMANTIC ERROR: ', tree['error'])
        
        return self

    def __optimizeTree (self, tree):
        try:
            queryTreeTransformer    =   SQLQueryTreeOptimizer (tree)
            transformedTrees        =   queryTreeTransformer.transform ()
            
            if "trees" in transformedTrees:
                self.optimizedTrees  =   transformedTrees
                self.__generateQueryPlan (self.optimizedTrees)

        except Exception as e:
            self.error  =   self.__generateError ('OPTIMIZED TREE', e)
        
        return self

    def __generateQueryPlan (self, trees):
        
        try:
            generatedQueryPlans = []
            for tree in trees["trees"]:
                planner = SQLQueryPlan (tree)
                queryPlan = planner.create()
                generatedQueryPlans.append(queryPlan)
            
            self.__generateCost (generatedQueryPlans)

        except Exception as e:
            
            self.error  =   self.__generateError ('QUERY PLANS', e)
        
        return self

    def __generateCost (self, plans):
        try:
            queryPlans  =    []
            # get estimate
            for plan in plans:
                queryCostEstimator  =   SQLQueryCost (plan, schema = self.defaultDatabaseSchema)
                queryCost   =   queryCostEstimator.estimate ()
                queryPlans.append (queryCost)
            self.__selectQueryPlan (queryPlans)

        except Exception as e:
            self.error  = self.__generateError ('QUERY COSTS', e)
        
        return self

    def __selectQueryPlan (self, plans):
        try:
            bestQueryPlan   =   SQLQueryPlanSelector (plans)
            self.plan       =   bestQueryPlan.getResults()
            if 'plan' in self.plan: self.__executeQueryPlan (self.plan['plan'])
        except Exception as e:
            self.error  =   self.__generateError ('QUERY PLAN', e)
        
        return self

    def __executeQueryPlan (self, plan):
        queryPlanExecution  =   SQLQueryPlanExecution (plan)
        queryPlanExecution.setDatabasePath(self.databasePath).setDatabaseName(self.databaseName).execute ()

        self.results        =   queryPlanExecution.getResults ()

        return self

    def __generateError (self, title, message):
        return {'error' : f"[{title}]:{message}"}