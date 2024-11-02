import sys
import os
import copy
import time
import re

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

from schemas.SchemaTableFileLoader import SchemaTableFileLoader

class SQLQueryPlanExecution :
    def __init__ (self, plan):
        self.databasePath       =   None
        self.databaseName       =   None
        self.databaseRealPath   =   None
        self.plan               =   plan
        self.currentRow         =   {}
        self.cachedTables       =   {}
        self.error              =   None
        self.startTime          =   None
        self.endTime            =   None
        self.debug              =   False
        self.tablePathSuffix    =   '.table'
        self.tableFileFormat    =   'csv'
        self.rowCount           =   0
        self.rows               =   []
        self.__mustContinue     =   True

    def setDebug (self, debug = False):
        self.debug      = debug
        self.debugLevel =   1
        return self
    
    def setDatabasePath (self, dbPath):
        self.databasePath   =   dbPath
        return self

    def setDatabaseName (self, name):
        self.databaseName  =   name
        return self
    
    def execute (self):
        if self.databasePath == None or self.databaseName == None:
            self. error =   f"Database [{self.databasePath}/{self.databaseName}] does not exists"
            return self
        
        # ensures that the directory of the selected database is present
        if not self.__isDatabaseFolderExists ():
            print('non')
            self. error =   f"Database [{self.databasePath}/{self.databaseName}] does not exists"
            return self
        
        

        # execute query
        self.startTime    =   time.perf_counter()
        self.__executePlan (self.plan)
        self.endTime    =   time.perf_counter()
        return self

    
    def __isDatabaseFolderExists (self):
        fullDBPath  =   os.path.dirname(os.path.realpath(f"{self.databasePath}/{self.databaseName}"))
        realPath    =   f"{fullDBPath}/{self.databaseName}.db"
        isDBExists  =   os.path.isdir(realPath)
        # set dabase full path
        if isDBExists: self.__setDatabaseRealPath (realPath)
        return isDBExists

    def __setDatabaseRealPath (self, path):
        self.databaseRealPath   =   path
        return self
        
    def __executePlan (self, plan):
        __stepLength    =   len(plan)
        for x in range(__stepLength):
            if x == 0:
                for stepName in plan[x]:
                    if '__MERGE__' in stepName:
                        # get next step if the first step is merge
                        __nextStep  =   None
                        if (x+1) < __stepLength: __nextStep = plan[x+1]
 
                        if len(__nextStep) > 0:
                            for n in __nextStep:
                                __nextStep  = __nextStep[n]

                        self.__processMergeSteps (plan[x][stepName], __nextStep)
            else:
                for stepName in plan[x]:
                    if '__SEQUENCE__' in stepName:
                        self.__processSequenceSteps (plan[x][stepName])
                    if '__MERGE__' in stepName:
                        # get next step if the first step is merge
                        __nextStep  =   None
                        if (x+1) < __stepLength: __nextStep = plan[x+1]
 
                        if len(__nextStep) > 0:
                            for n in __nextStep:
                                __nextStep  = __nextStep[n]

                        self.__processMergeSteps (plan[x][stepName], __nextStep)
        

        return self
        
    def __processMergeSteps (self, steps, callbackSteps = None):
        if 'children' in steps:
            while self.__mustContinue:
                __parentCount       =   0
                __childrenLength    =   len(steps['children'])

                for children in steps['children']:
                    __childCount = 0

                    #process first branch
                    if __parentCount == 0:

                        if self.debug :
                            print(f'\r\n-----[INIT]-----')
                            print(__parentCount, ':', children)
                            print('----------------\r\n')
                    
                        # ensure that the current children is not an array before processing
                        if isinstance(children, list):
                            for child in children:
                                if isinstance(child, list):
                                    for ch in child:
                                        self.__processStep (ch, True if __parentCount == 0 else False)
                                else:
                                    self.__processStep (child, True if __parentCount == 0 else False)
                        else:
                            self.__processStep (children, True if __parentCount == 0 else False)

                        if self.debug :
                            print(f'\r\n-----[CURRENT:PARENT]-----')
                            print(self.currentRow)
                            print('----------------\r\n')

                        # next step look ahead
                        __parentRow     =   self.currentRow
                        __childCount    += 1

                        # process next step
                        if(__childCount < __childrenLength) and (not __parentRow == None):

                            if self.debug :
                                print(f'\r\n-----[PROCESSING NEXT STEPS]-----')
                                print(steps['children'][__childCount])
                                print(f'\r\n--------------------------------\r\n')
                            
                            __loopChildren  =   0
                            #reset the cursor of the next step
                            if self.debug : print('-----[RESETING CURSOR]-----')
                            self.__processSequenceSteps({'children': steps['children'][__childCount]}, False, True)

                            if self.debug :
                                print('\r\n-----[PROCESSED FIRST SEQUENCE]-----\r\n')
                                print(self.currentRow)
                            
                            if((not self.currentRow == 'EOF') and (not self.currentRow == None) and (not self.currentRow == {}) and (not __parentRow == 'EOF')):
                                if not self.currentRow == 'EOF':

                                        self.currentRow = {**__parentRow, **self.currentRow}

                                        if self.debug :
                                            print('\r\n-------[PIPE]---------')
                                            print(callbackSteps)
                                            print('----------------------\r\n')

                                        # run callback sequence
                                        if not callbackSteps == None: self.__processSequenceSteps(callbackSteps)
                                         
                                        # current data after running the pipeline 
                                        if self.debug : 
                                            print(self.currentRow)
                                            print('\r\n-------[END PIPE]---------\r\n')

                                        # after merging and pipelining
                                        if self.currentRow != None:
                                            self.rowCount += 1
                                            self.rows.append (self.currentRow)

                            
                            while True:
                                if self.debug :
                                    print('\r\n-----[RUNNING WHILE LOOOP]-----\r\n')
                                    print(self.currentRow)
                                    print (__parentRow)

                                if((not self.currentRow == 'EOF') and (not __parentRow == 'EOF')):
   
                                    if __loopChildren > 0:
                                        
                                        if self.debug : print(f'-----[START LOOP CHILDREN: {__loopChildren}]-----')
                                        self.__processSequenceSteps({'children': steps['children'][__childCount]})

                                        # inspect rows before merging
                                        if self.debug :
                                            print('-----[END LOOP CHILDREN]-----\r\n')
                                            print()
                                            print('------[MERGING: PARENT]-----')
                                            print(__parentRow)

                                            print('\r\n------[MERGING: CHILD]-----')
                                            print(self.currentRow)

                                        if not self.currentRow == 'EOF':
                                            if not self.currentRow == None:
                                                self.currentRow = {**__parentRow, **self.currentRow}

                                                if self.debug :
                                                    print('\r\n-------[PIPE 2]---------')
                                                    print(callbackSteps)
                                                    print('----------------------\r\n')

                                                # run callback sequence
                                                if not callbackSteps == None : self.__processSequenceSteps(callbackSteps)
                                                    
                                                # current data after running the pipeline
                                                if self.debug :    
                                                    print(self.currentRow)
                                                    print('\r\n-------[END PIPE]---------\r\n')

                                                # after merging and pipelining
                                                if self.currentRow != None:
                                                    self.rowCount += 1
                                                    self.rows.append (self.currentRow)
                                        else:
                                            # eof
                                            break
                                            
                                    # mark child loop  
                                    __loopChildren += 1
                                else:
                                    break

                    # prevent running infinite steps
                    __parentRow     =  self.currentRow
                    __parentCount  +=   1 

                
    def __processSequenceSteps (self, steps, stopIfEOF = False, resetRelation = False):
        if not 'children' in steps: return None
        for children in steps['children']:
            # ensure that the current children is not an array before processing
            if isinstance(children, list):
                for child in children:
                    if isinstance(child, list):
                        for ch in child:
                            self.__processStep (ch, stopIfEOF, resetRelation)
                    else:
                        self.__processStep (child, stopIfEOF, resetRelation)
            else:
                self.__processStep (children, stopIfEOF, resetRelation)

    def __processStep (self, step, stopIfEOF = False, resetRelation = False):
        if '__π__' in step: self.__processProjection (step)
        if '__Ω__' in step: self.__processSelection (step)
        if '__r__' in step: self.__processRelation (step, stopIfEOF, resetRelation)

    def __processRelation (self, step, stopIfEOF = False, resetRelation = False):
        # set default table name
        __tableName     =   step['__r__']
        if isinstance(step['__r__'], list):
            __tableName =   step['__r__'][0]
        
        if self.debug:
            print('\r\n-----[RELATION]-----')
            print(__tableName)
            print('----------------\r\n')

        # prevent empty relation
        if len(step['__r__']) < 1: return None

        # ignore if already present in cache
        if not __tableName in self.cachedTables:
            tableName           =   f"{__tableName}{self.tablePathSuffix}.{self.tableFileFormat}"
            tableFullPath       =   f"{self.databaseRealPath}/{tableName}"
            tableFileLoader     =   SchemaTableFileLoader (tableFullPath)
            # save to cache
            if tableFileLoader:
                if len(tableFileLoader.headers) > 0: 
                    self.cachedTables[__tableName] = tableFileLoader
                    
                    # set the next row to be processed
                    self.currentRow =   tableFileLoader.nextRow ()
                    if self.debug :
                        print('---[load from file]--')
                        print(self.currentRow)
        else:

            # reset row if needed
            if resetRelation:
                self.cachedTables[__tableName].reset ()
                self.currentRow =   self.cachedTables[__tableName].nextRow ()
                if self.debug : print('---[reset cursor]--')

            # set the next row to be processed
            self.currentRow =   self.cachedTables[__tableName].nextRow ()
            if self.debug : 
                print('---[load from cache]--')
                print(self.currentRow)

            # stop if encounter an EOF
            if stopIfEOF and self.currentRow == 'EOF': 
                self.__mustContinue = False
                if self.debug : print('---[EOF]---')

            
    def __processSelection (self, step):
        __shouldReturnRow   =   False
        __selections        =   step['__Ω__']
        __operators         =   step['operators']
        __curRow            =   self.currentRow

        if len(__selections) == 1:
            if self.debug:
                print('\r\n------[SELECTION]-----')
                print(__curRow)

            # do not proceed if EOF detected
            if __curRow == 'EOF': return

            # split selection
            columnWithCondition = re.split(r'\s*(=|!=|<=|>=|<|>)\s*', __selections[0])
            
            if __curRow:
                for headerName in self.currentRow:
                    # match row and condition
                    if headerName == columnWithCondition[0]:
                        
                        # ==
                        if columnWithCondition[1] == '=':
                            if self.debug:
                                print(f'\r\n--[COMPARING] : {headerName}--', self.currentRow[headerName], ':', columnWithCondition[2])
                                print('----', type(self.currentRow[headerName]), type(columnWithCondition[2]))
                                print('----', len(self.currentRow[headerName]), len(columnWithCondition[2]))
                                print('----', f"{self.currentRow[headerName]}" == f"{columnWithCondition[2]}")
                                print('----', f"'{self.currentRow[headerName]}'" == f"{columnWithCondition[2]}")

                            # convert to string and ' to match string
                            if (f"'{self.currentRow[headerName]}'" == f"{columnWithCondition[2]}") or (f"{self.currentRow[headerName]}" == f"{columnWithCondition[2]}") : 
                                __shouldReturnRow = True
                        
                        if columnWithCondition[1] == '!=':
                            # convert to string and ' to match string
                            if (f"'{self.currentRow[headerName]}'" != f"{columnWithCondition[2]}") and (not f"{self.currentRow[headerName]}" != f"{columnWithCondition[2]}") : 
                                __shouldReturnRow = True

                        if columnWithCondition[1] == '<':
                            if (f"{self.currentRow[headerName]}" < f"{columnWithCondition[2]}") : 
                                __shouldReturnRow = True
                        
                        if columnWithCondition[1] == '>':
                            if (f"{self.currentRow[headerName]}" > f"{columnWithCondition[2]}") : 
                                __shouldReturnRow = True
                        
                        if columnWithCondition[1] == '<=':
                            if (f"{self.currentRow[headerName]}" <= f"{columnWithCondition[2]}") : 
                                __shouldReturnRow = True
                        
                        if columnWithCondition[1] == '>=':
                            if (f"{self.currentRow[headerName]}" >= f"{columnWithCondition[2]}") : 
                                __shouldReturnRow = True

            if __shouldReturnRow:
                self.currentRow = __curRow
            else:
                self.currentRow =   None
        else:
            if self.debug:
                print('\r\n---[MULTIPLE SELECTION]---')
                print(self.currentRow)
                print('---------------------------\r\n')

            for headerName in self.currentRow:

                for sel in __selections:
                    # split selection
                    columnWithCondition = re.split(r'\s*(=|!=|<=|>=|<|>)\s*', sel)

                    # match row and condition
                    if headerName == columnWithCondition[0]:
                         # ==
                        if columnWithCondition[1] == '=':
                            if self.debug:
                                print(f'\r\n--[COMPARING] : {headerName}--', self.currentRow[headerName], ':', columnWithCondition[2])
                                print('----', type(self.currentRow[headerName]), type(columnWithCondition[2]))
                                print('----', len(self.currentRow[headerName]), len(columnWithCondition[2]))
                                print('----', f"{self.currentRow[headerName]}" == f"{columnWithCondition[2]}")
                                print('----', f"'{self.currentRow[headerName]}'" == f"{columnWithCondition[2]}")

                            # convert to string and ' to match string
                            if (f"'{self.currentRow[headerName]}'" == f"{columnWithCondition[2]}") or (f"{self.currentRow[headerName]}" == f"{columnWithCondition[2]}") : 
                                __shouldReturnRow = True

                        if columnWithCondition[1] == '!=':
                            # convert to string and ' to match string
                            if (f"'{self.currentRow[headerName]}'" != f"{columnWithCondition[2]}") and (not f"{self.currentRow[headerName]}" != f"{columnWithCondition[2]}") : 
                                __shouldReturnRow = True

                        if columnWithCondition[1] == '<':
                            if (f"{self.currentRow[headerName]}" < f"{columnWithCondition[2]}") : 
                                __shouldReturnRow = True
                        
                        if columnWithCondition[1] == '>':
                            if (f"{self.currentRow[headerName]}" > f"{columnWithCondition[2]}") : 
                                __shouldReturnRow = True
                        
                        if columnWithCondition[1] == '<=':
                            if (f"{self.currentRow[headerName]}" <= f"{columnWithCondition[2]}") : 
                                __shouldReturnRow = True
                        
                        if columnWithCondition[1] == '>=':
                            if (f"{self.currentRow[headerName]}" >= f"{columnWithCondition[2]}") : 
                                __shouldReturnRow = True

            if __shouldReturnRow:
                self.currentRow = __curRow
            else:
                self.currentRow =   None


        return self

    def __processProjection (self, step):
        # ignore *
        __columns   =   []
        if '*' in step : return self

        __columns   =   step['__π__']
        __curRow    =   copy.deepcopy(self.currentRow)

        # ignore *
        if '*' in __columns : return self

        if __curRow:
            for headerName in self.currentRow:
                if not headerName in __columns:
                    del __curRow[headerName]
        
        self.currentRow =   __curRow
        return self

    def getResults (self):
        return {
            'rowCount'      :   self.rowCount,
            'rows'          :   self.rows,
            'executionTime' :   f"{self.endTime - self.startTime:.8f}s",
        }
    
    def getPerformance (self):
        return {
            'rowCount'      :   self.rowCount,
            'executionTime' :   f"{self.endTime - self.startTime:.8f}s",
        }