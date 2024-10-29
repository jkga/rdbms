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

if __name__ == '__main__':
    inputStream = antlr4.InputStream(sys.argv[1])
    sqlAnnotate = SQLAnnotate(sql = inputStream, schema = Students)
    sqlAnnotate.annotate()
    annotations = sqlAnnotate.getAnnotations()

    code = IntermediateCodeGenerator (annotations)
    queryTree = code.generate().getResults()

    print('\r\n-->-------[ORIGINAL QUERY TREES]------')
    print (queryTree)
    print('-->-----------------------------------\r\n')

    # feed the query plan to optimer to generate possible queries
    # NOTE: the current transformer do nothing as of the moment
    queryTreeTransformer = SQLQueryTreeOptimizer (queryTree)
    transformedTrees = queryTreeTransformer.transform ()

    generatedQueryPlans = []

    if "trees" in transformedTrees:
        for tree in transformedTrees["trees"]:

            planner = SQLQueryPlan (tree)
            queryPlan = planner.setDebug(False).create()
            generatedQueryPlans.append(queryPlan)
    
    queryPlans  =    []
    # get estimate
    for plan in generatedQueryPlans:
        queryCostEstimator  =   SQLQueryCost (plan, schema = Students).setDebug(False)
        queryCost   =   queryCostEstimator.estimate ()
        queryPlans.append (queryCost)
    

    # select best plan based on cost
    bestQueryPlan   =   SQLQueryPlanSelector (queryPlans)

    print('\r\n-->-------[BEST PLAN]------')
    print(bestQueryPlan.getResults())
    print('-->----------------------------\r\n')
    