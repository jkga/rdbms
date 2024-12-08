import sys
import os
import copy

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

class SQLQueryCost:
    def __init__(self, plan, **kwargs):
        self.plan           =      plan
        self.steps          =      0
        self.debug          =      False
        self.totalCosts     =      0
        self.operation      =      'select'

        if 'schema' in kwargs:
            self.schema         =      self.schema = kwargs['schema']() if callable(kwargs['schema']) else kwargs['schema']
        
        if 'operation' in kwargs:
            self.operation  =   kwargs['operation']
    
    def setDebug (self, debug = False):
        self.debug      =   debug

        return self
    
    def estimate (self):
        self.__parse (self.plan)

        return {
            'costs'     :   self.totalCosts,
            'plan'      :   self.plan,
            'operation' :   self.operation
        }
    
    def loadSchema (self, Schema):
        if Schema != None:
            self.schema = Schema()
        
    
    def __readSteps(self, step):
        if self.debug : print('----[STEP]-----')

        # read __merge__ and __sequence__
        for name in step:
            if '__MERGE__' in name:
                self.__readMerge (step[name], step)
            else:
                self.__readSequence (step[name], step)

    def __parse (self, plan):
        for step in plan:
            self.__readSteps (step)

    def __readSequence (self, steps, parent):
        # holds all the tables on the list
        relations    =   []
        selections   =   []
        projections  =   []

        if self.debug :
            print('-----[SEQUENCE]-----')
            print(steps)

        for step in steps:
            if self.debug :
                print('\r\n---[SEQUENCE STEPS]---')
                print(step)
                print('------------------\r\n')

            if isinstance(step, list):
                for s in step:
                    if '__r__' in s:
                        relations.append(self.__readRelation (s))
                
                    if '__Ω__' in s:
                        selections.append(self.__readSelection (s))
                    
                    if '__π__' in s:
                        projections.append(self.__readProjection (s))    

            else:
            
                if '__r__' in step:
                    relations.append(self.__readRelation (step))
                
                if '__Ω__' in step:
                    selections.append(self.__readSelection (step))
                
                if '__π__' in step:
                    projections.append(self.__readProjection (step))


        if self.debug :
            print('\r\n------[DONE SEQUENCE]-------')
            print(steps)
            print('------------------\r\n')

            print('\r\n------[READING ALL RELATIONS]-------')
            print(relations)
            print('------------------\r\n')

        # get all the costs and cols of all the relations
        relCosts    =   0
        relCols     =   0

        # compute the join cost of the relation
        # total = tableA(row) * tableB(row)
        for rel in relations:
            if relCosts == 0:
                relCosts = rel['rows'] * 1
            else:
                relCosts += relCosts * (rel['rows'] * 1)
            
            # rows
            relCols +=  rel['rows']
        
        # selections
        for sel in selections:
            relCosts += sel['cost']

        # projections
        for proj in projections:
            relCosts += proj['cost']


        if self.debug :
            print('\r\n------[COST OF ALL RELATIONS]-------')
            print(relCosts)
            print('------------------\r\n')

            print('\r\n------[TRANSFORMING PARENT NODE]-------')
            print(parent)
            print('------------------\r\n')

        # return the updated list
        for name in parent:
            parent[name] = {
                'children'  :   steps,
                'cost'      :   relCols,
                'rows'      :   0,
                'cols'      :   relCols,
            }
            # add to total cost of the query plan
            self.totalCosts += relCosts
        
        if self.debug :
            print('\r\n------[TRANSFORMED PARENT NODE]-------')
            print(parent)
            print('------------------\r\n')



    def __readMerge (self, steps, parent):
        # holds all the tables on the list
        relations    =   []
        selections   =   []
        projections  =   []

        if self.debug :
            print('-----[MERGE]-----')
            print(steps)
            
        # '__MERGE__:step:x = [[[]]]'
        # cost = costA * costB 

        for mergeSteps in steps:
            if self.debug :
                print('\r\n---[MERGE STEPS]---')
                print(mergeSteps)
                print('------------------\r\n')

            for step in mergeSteps:
                if self.debug :
                    print('\r\n---[BREAKDOWN]---')
                    print(step)
                    print('------------------\r\n')

                if '__r__' in step:
                    relations.append(self.__readRelation (step))
                
                if '__Ω__' in step:
                    selections.append(self.__readSelection (step))
                
                if '__π__' in step:
                    relations.append(self.__readProjection (step))
                    
        if self.debug :
            print('\r\n------[DONE MERGE]-------')
            print(steps)
            print('------------------\r\n')

            print('\r\n------[READING ALL RELATIONS]-------')
            print(relations)
            print('------------------\r\n')

        relCosts    =   0
        relCols     =   0
        # relations
        for rel in relations:
            if relCosts == 0:
                relCosts = rel['rows'] * 1
            else:
                relCosts += relCosts * (rel['rows'] * 1)
            
            # rows
            relCols +=  rel['rows']
        
        # selections
        for sel in selections:
            relCosts += sel['cost']

        # projections
        for proj in projections:
            relCosts += proj['cost']
            
        if self.debug :
            print('\r\n------[COST OF ALL RELATIONS]-------')
            print(relCosts)
            print('------------------\r\n')
    
            print('\r\n------[TRANSFORMING PARENT NODE]-------')
            print(parent)
            print('------------------\r\n')
        

        for name in parent:
            parent[name] = {
                'children'  :   steps,
                'cost'      :   relCosts,
                'rows'      :   0,
                'cols'      :   relCols,
                'algorithm' :   'nested'
            }

            # add to total cost of the query plan
            self.totalCosts += relCosts
        
        if self.debug :
            print('\r\n------[TRANSFORMED PARENT NODE]-------')
            print(parent)
            print('------------------\r\n')

    def __readRelation (self, step):
        stepRel = step['__r__']
        step['cost'] = 0
        step['rows'] = 0
        step['cols'] = 0
        
        if isinstance(step['__r__'], list):
            stepRel =   step['__r__'][0]

        
        prop = self.schema.getProperties (stepRel)
        cols = self.schema.getColumns (stepRel)

        if not prop == None:
            if 'rows' in prop: 
                step['cost']    =   prop['rows']
                step['rows']    =   prop['rows']
            
            step['cols'] = len(cols)

        return step
    
    def __readSelection (self, step):
        # estimate based on blocks or tuple
        # cost = total rows * (number of blocks per data | 1)
        # single selection [c.a=1]
        step['cost'] = 0
        step['rows'] = 0
        step['cols'] = 0
    
        if len(step['__Ω__']) < 2:
            tableColumn = step['__Ω__'][0].split('.')

            if len (tableColumn) >=2:
                prop = self.schema.getProperties (tableColumn[0])
                cols = self.schema.getColumns (tableColumn[0])
                
                if not prop == None:
                    if 'rows' in prop:
                        step['cost']    =   prop['rows'] * 1
                        step['rows']    =   prop['rows']
                    step['cols'] = len(cols)

        else:
            # multiple selection [c.a=1 , c.b=2]
            tempTables = []
            for col in step['__Ω__']:
                tableColumn = col.split('.')

                if len (tableColumn) >=2:
                    if not tableColumn[0] in tempTables:
              
                        tempTables.append(tableColumn[0])

            tempCostCount   =   0
            tempRowCount    =   0
            tempColCount    =   0

            for table in tempTables:
                prop = self.schema.getProperties (table)
                cols = self.schema.getColumns (table)
                tempRowCount   +=   prop['rows']
                tempColCount   +=   len(cols)

                if tempCostCount == 0:
                    tempCostCount  =   (prop['rows'] * 1)
                else:
                    tempCostCount  +=   tempCostCount * (prop['rows'] * 1)

            # get total cost for all the tables
            step['cost']    =   tempCostCount
            step['rows']    =   tempRowCount
            step['cols']    =   tempColCount
    

        return step
    
    def __readProjection (self, step):
        # cost = total (tuples)
        step['cost'] = 0
        step['rows'] = 0

        return step