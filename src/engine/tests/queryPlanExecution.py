import antlr4
import sys
import os
import pprint
from antlr4 import *

dir_path = os.path.dirname(os.path.realpath(__file__))

# manual access to schema directory
sys.path.append(os.path.abspath(os.path.join(dir_path,  '../' +  os.pardir)))
from schemas.samples.Students import Students

# restore parent directory path
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

from compiler.analyzer.SQLAnnotate import SQLAnnotate
from compiler.generator.IntermediateCodeGenerator import IntermediateCodeGenerator
from compiler.optimizer.SQLQueryTreeOptimizer import SQLQueryTreeOptimizer
from compiler.optimizer.SQLQueryPlan import SQLQueryPlan
from compiler.optimizer.SQLQueryCost import SQLQueryCost
from engine.SQLQueryPlanSelector import SQLQueryPlanSelector
from engine.SQLQueryPlanExecution import SQLQueryPlanExecution
from schemas.SchemaFileLoader import SchemaFileLoader

databasePath        =   './data/databases'
databaseName        =   'students' 

if __name__ == '__main__':
    # load schema from file
    defaultDatabaseSchema       =   None
    fileLoader                  =   SchemaFileLoader (f"{databasePath}/{databaseName}.db/{databaseName}.db.json")
    databaseSchemaInstance      =   fileLoader.getResults ()
    
    # set default database schema
    if 'schema' in databaseSchemaInstance: defaultDatabaseSchema = databaseSchemaInstance['schema']

    inputStream = antlr4.InputStream(sys.argv[1])
    sqlAnnotate = SQLAnnotate(sql = inputStream, schema = defaultDatabaseSchema)
    sqlAnnotate.annotate()
    annotations = sqlAnnotate.getAnnotations()

    code        =   IntermediateCodeGenerator (annotations)
    queryTree   =   code.generate().getResults()
    operation   =   'select'

    # SAMPL QUERY
    # "SELECT student.StudNo, student.StudentName, studcourse.StudNo, studcourse.AcadYear FROM (SELECT student.StudNo, student.StudentName, studcourse.StudNo FROM student, studcourse WHERE student.StudNo='2007-52623' and studcourse.AcadYear=2000);"
    print('\r\n-->-------[ORIGINAL QUERY TREES]------')
    print (queryTree)
    print('-->-----------------------------------\r\n')

    # feed the query plan to optimer to generate possible queries
    # NOTE: the current transformer do nothing as of the moment
    queryTreeTransformer = SQLQueryTreeOptimizer (queryTree)
    transformedTrees = queryTreeTransformer.transform ()

    generatedQueryPlans = []

    if 'operation' in transformedTrees:
        operation = transformedTrees['operation']
    
    if "trees" in transformedTrees:
        for tree in transformedTrees["trees"]:

            planner = SQLQueryPlan (tree)
            queryPlan = planner.setDebug(False).create()
            generatedQueryPlans.append(queryPlan)
    
    queryPlans  =    []
    # get estimate
    for plan in generatedQueryPlans:
        queryCostEstimator  =   SQLQueryCost (plan, schema = defaultDatabaseSchema, operation = operation).setDebug(False)
        queryCost   =   queryCostEstimator.estimate ()
        queryPlans.append (queryCost)
    

    # select best plan based on cost
    bestQueryPlan   =   SQLQueryPlanSelector (queryPlans)
    bestPlan        =   bestQueryPlan.getResults()

    print('\r\n-->-------[PLAN]------')
    print(bestPlan)
    print('-->----------------------------\r\n')
    
    if 'plan' in bestPlan:  
        queryPlanExecution  =   SQLQueryPlanExecution (bestQueryPlan.getResults()['plan'], bestPlan['operation'] if 'plan' in bestPlan else 'select')
        queryPlanExecution.setDebug(False).setDatabasePath(databasePath).setDatabaseName(databaseName).execute ()
        
        # use getPerformance returns the total rowCount and execution time
        # queryPlanExecution.getPerformance ()
        print('\r\n-->-------[EXECUTE]------')
        print(queryPlanExecution.getResults ())
        print('-->----------------------------\r\n')
        