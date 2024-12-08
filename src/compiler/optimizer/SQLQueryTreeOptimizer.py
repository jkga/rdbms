import sys
import os
import re
import copy

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

class SQLQueryTreeOptimizer:
    def __init__ (self, queryTree):
        self.queries        =       []
        self.queryTree      =       queryTree
        self.passCount      =       5
        self.operation      =       'select'
        self.debug          =       False
        self.debugLevel     =       0

    def setDebug (self, debug = False):
        self.debug      = debug
        self.debugLevel =   1
        return self
    
    def setDebugLevel (self, debugLevel):
        self.debugLevel =   debugLevel
        return self
    
    def transform (self):
        if 'operation' in self.queryTree:
            self.operation   =   self.queryTree['operation']

        if 'data' in self.queryTree:
            # original data
            parsedNode = self.queryTree['data']
            
            # set ideal passCount based on node's length
            # min: 3
            nodeCount = self.__getNodeLength(self.queryTree['data'], 1)
            if nodeCount > 3 : self.passCount = nodeCount

            if self.debug:
                print(f"-->[ORIGINAL TREE]-----------------")
                print(parsedNode)
                print('--------------------------------\r\n')
            
            for i in range(self.passCount):
                # start parsing the tree
                if self.debug:
                    print(f"-->[PASS: {i}]-----------------")
                    print(parsedNode)
                    print('-->-----------------------------\r\n')


                parsedNode = self.__visitNode (parsedNode)
                if self.debug:
                    print('-->--------[PARSED RESULTS]------------')
                    print(parsedNode)
                    print('-->--------[END PARSED RESULTS]-----\r\n')

                # prevent inserting the same tree
                if not parsedNode in self.queries:
                    self.queries.append (parsedNode)


        return { 'trees' : self.queries, 'operation' : self.operation }
    
    def __getLastChild (self, node):
        # get all children's children
        if not node == None:
            if 'children' in node:
                if not node['children'] == None: 
                    return self.__getLastChild (node['children'])
        return node

    def __getParentNode (self, childNode, parentNode = None):
        # get all children's children
        if not childNode == None:
            if 'children' in childNode:
                if not childNode['children'] == None: 
                    return self.__getParentNode(childNode['children'], childNode)
    
        return parentNode
    
    
    def __getNodeLength (self, node, length):
        # get all children's children
        if not node == None:
            if 'children' in node:
                if not node['children'] == None: 
                    return self.__getNodeLength (node['children'], length + 1)
        return length

    def __getNodeType (self, node):
        nodeType        =   None
        nodeValue       =   None
        nodeChildren    =   None

        if not node == None:
            if '__π__' in node: nodeType = '__π__'
            if '__Ω__' in node: nodeType = '__Ω__'
            if '__x__' in node: nodeType = '__x__'
            if '__θ__' in node: nodeType = '__θ__'

            if not nodeType == None:
                nodeValue = node[nodeType]

                if 'children' in node:
                    if not node['children'] == None: nodeChildren = node['children']

        return { 
            'nodeType'      :   nodeType, 
            'nodeValue'     :   nodeValue,
            'nodeChildren'  :   nodeChildren 
        }
    
    def __insertNodeBefore (self, currentNode, nodeToInsert):

        if not 'children' in nodeToInsert: nodeToInsert['children'] = None

        nodeToInsert['children'] = currentNode

        return nodeToInsert


    def __visitNode (self, node):

        currentNodeType     =   self.__getNodeType (node)
        currentNode         =   node
        nextNode            =   None
        nextNextNode        =   None
        nextNodeType        =   None
        nextNextNodeType    =   None

        # assign current node
        currentNode = node

        # get child nodes
        if 'children' in currentNode:
            if not currentNode['children'] == None:
                nextNode        =   currentNode['children']
                nextNodeType    =   self.__getNodeType (currentNode['children'])  

                #read children of the next node
                if 'children' in nextNode:
                    nextNextNode = nextNode['children']
                    if not nextNextNode == None : nextNextNodeType = self.__getNodeType (nextNextNode)

                # remove duplicate parent and direct descendant
                if (currentNodeType['nodeType'] == nextNodeType['nodeType']) and (currentNodeType['nodeValue'] == nextNodeType['nodeValue']):
                    parsedNode          =   self.__removeDuplicateNextNode (currentNode, nextNode)
                    currentNode         =   parsedNode['currentNode']
                    #nextNode            =   parsedNode['nextNode']
                    currentNodeType     =   parsedNode['currentNodeType']
                    nextNodeType        =   parsedNode['nextNodeType']
                
                # look ahead
                # remove duplicate if the children has also a children with the same type of the current node
                if not nextNextNodeType == None and 'children' in nextNode:
                    # same type and value
                    if (currentNodeType['nodeType'] == nextNextNodeType['nodeType']) and (currentNodeType['nodeValue'] == nextNextNodeType['nodeValue']):
                        # replace the children of the next children
                        nextNode['children'] = nextNextNodeType['nodeChildren']
                        currentNode['children'] = nextNode
                        currentNodeType     =   self.__getNodeType (currentNode)
                        nextNodeType        =   self.__getNodeType (currentNode['children'])

                        if self.debug and self.debugLevel > 2:
                            print('-----DUPLICATE CURRENT AND NEXR NEXT NODE-------')
                            print(currentNode)
                            print('--------------------------')

                if self.debug and self.debugLevel > 2:
                    print('-->START PATTERN CHECKING-------')
                    print('-->',currentNodeType['nodeValue'])
                    print('-->-----------------------------\r\n')

                # check for patterns
                # __Ω__1,2,3...n = __Ω__ --> __Ω__ --> __Ω__
                # __Ω__1,2,3...n = __Ω__ --> __r__
                # (node1) == (node2) = remove(node2)
                # __π1__ + __π2__ = remove(__π2__)
                # __π1__ + (node)--> + __π2__ = remove(__π2__)
                # __Ω__ + __x__ = __θ__
                # __π__ + __θ__ = pushProjectToThetaJoin(__r__)
                # __π__ + __x__ = pushProjectToTables(__r__)
                # __Ω__ + __θ__ = pushSelectionToJoin(__x__)

                if (currentNodeType['nodeType'] == '__π__') and (nextNodeType['nodeType'] == '__π__'):
                    # remove subsequent columns(__π__)
                    parsedNode      =   self.__removeSubsequentProjection (currentNode, nextNode)
                    currentNode     =   parsedNode['currentNode']
                    nextNode        =   parsedNode['nextNode']
                    currentNodeType =   parsedNode['currentNodeType']
                    nextNodeType    =   parsedNode['nextNodeType']

                    #read children of the next node
                    if 'children' in nextNode:
                        nextNextNode = nextNode['children']
                        if not nextNextNode == None : nextNextNodeType = self.__getNodeType (nextNextNode)

                if not nextNextNode == None:
                    if (currentNodeType['nodeType'] == '__π__') and (nextNextNodeType['nodeType'] == '__π__'):
                        # remove subsequent columns(__π__)
                        parsedNode      =   self.__removeSubsequentProjection (currentNode, nextNode, nextNextNode)
                        currentNode     =   parsedNode['currentNode']
                        nextNode        =   parsedNode['nextNode']
                        currentNodeType =   parsedNode['currentNodeType']
                        nextNodeType    =   parsedNode['nextNodeType']

                if (currentNodeType['nodeType'] == '__Ω__'):
                    # only split of there are two or more selections
                    if len(currentNodeType['nodeValue']) > 1:
                        parsedNode      =   self.__splitSelections (currentNode, nextNode)
                        currentNode     =   parsedNode['currentNode']
                        nextNode        =   parsedNode['nextNode']
                        currentNodeType =   parsedNode['currentNodeType']
                        nextNodeType    =   parsedNode['nextNodeType']
                    else:
                        # push noded to __r__
                        parsedNode      =   self.__pushSelectionsToRelations (currentNode, nextNode)
                        currentNode     =   parsedNode['currentNode']
                        nextNode        =   parsedNode['nextNode']
                        currentNodeType =   parsedNode['currentNodeType']
                        nextNodeType    =   parsedNode['nextNodeType']
                
                if (currentNodeType['nodeType'] == '__Ω__') and (nextNodeType['nodeType'] == '__x__'):
                    parsedNode      =   self.__pushSelectionToJoin(currentNode, nextNode)
                    currentNode     =   parsedNode['currentNode']
                    nextNode        =   parsedNode['nextNode']
                    currentNodeType =   parsedNode['currentNodeType']
                    nextNodeType    =   parsedNode['nextNodeType']

                '''if (currentNodeType['nodeType'] == '__π__') and (nextNodeType['nodeType'] == '__x__'):
                    parsedNode      =   self.__pushProjectionToCrossJoin (currentNode, nextNode)
                    currentNode     =   parsedNode['currentNode']
                    nextNode        =   parsedNode['nextNode']
                    currentNodeType =   parsedNode['currentNodeType']
                    nextNodeType    =   parsedNode['nextNodeType']'''

                # Disable converting to theta join
                '''if (currentNodeType['nodeType'] == '__Ω__') and (nextNodeType['nodeType'] == '__x__'):
                    parsedNode      =   self.__convertToThetaJoin (currentNode, nextNode)
                    currentNode     =   parsedNode['currentNode']
                    nextNode        =   parsedNode['nextNode']
                    currentNodeType =   parsedNode['currentNodeType']
                    nextNodeType    =   parsedNode['nextNodeType']

                if (currentNodeType['nodeType'] == '__π__') and (nextNodeType['nodeType'] == '__θ__'):
                    parsedNode      =   self.__pushProjectionToThetaJoin(currentNode, nextNode)
                    currentNode     =   parsedNode['currentNode']
                    nextNode        =   parsedNode['nextNode']
                    currentNodeType =   parsedNode['currentNodeType']
                    nextNodeType    =   parsedNode['nextNodeType']
                
                if (currentNodeType['nodeType'] == '__Ω__') and (nextNodeType['nodeType'] == '__θ__'):
                    parsedNode      =   self.__pushSelectionToJoin(currentNode, nextNode)
                    currentNode     =   parsedNode['currentNode']
                    nextNode        =   parsedNode['nextNode']
                    currentNodeType =   parsedNode['currentNodeType']
                    nextNodeType    =   parsedNode['nextNodeType']'''


                if self.debug and self.debugLevel > 2:
                    print('\r\n-->--------[RESULTS AFTER PATTERN CHECKING]-------------')
                    print(currentNode)
                    print('-->-----------------------------------------------------\r\n')
                    print('-->------------[NEXT NODE]----------------------------------')
                    print(nextNode)
                    print('-->-----------------------------------------------------\r\n')

            # process next node
            if not nextNode == None:
                if 'children' in nextNode:
                    if not nextNode['children'] == None:
                        currentNode['children'] = self.__visitNode (nextNode) 
       
    
        return currentNode
    
    def __convertToThetaJoin (self, currentNode, nextNode):

        currentNodeType   =       self.__getNodeType (currentNode)
        nextNodeType      =       self.__getNodeType (nextNode) 

        # replace next node (cross join) with theta join
        newNextNode = {
            '__θ__'     :   nextNodeType['nodeValue'],
            '__c__'     :   currentNodeType['nodeValue'],
            'operators' :   currentNode['operators'],
            'children'  :   nextNodeType['nodeChildren']
        }
        
        if self.debug and self.debugLevel > 2:
            print('-->-----[CONVERT (__Ω__ and __x__) TO __θ__]-------')
            print('--FROM--', currentNode)
            print('------\r\n')
            print('--TO--', newNextNode)
            print('-->-----------------------------------------------')
        
        return {
            'currentNode'       :       newNextNode,
            'nextNode'          :       newNextNode['children'],
            'currentNodeType'   :       self.__getNodeType (currentNode),
            'nextNodeType'      :       self.__getNodeType (newNextNode['children']) 
        }

    def __splitSelections (self, currentNode, nextNode):
        # look for relations and push projection on top of the table
        columns             =   currentNode['__Ω__']
        operators           =   currentNode['operators']
        originalColumnCount =   len (columns)

        # holds the columns who do not belong to any relation
        undistributedColumns    =   columns.copy ()

        newColumns      =   []
        newOperators    =   []
        newChildren     =   None
        colIndex        =   0

        # remove columns with and operators
        for col in columns:
            if colIndex < len(operators):
                if operators[colIndex].lower() == 'and':
                    # remove and add new operators
                    newColumns.append (col)
                    undistributedColumns.remove(col)

            colIndex += 1
        
        for col in range(len(newColumns)-1):
            # fill up operators with OR based on the new children's length
            # if colIndex < (len(operators) - 1):
            newOperators.append ('OR')
        
        # replace current node if there are unsplit selections
        if (originalColumnCount > len(undistributedColumns)) and len (newColumns) > 0:
            for col in newColumns:
                # new childNode
                child = {
                    '__Ω__'         :   [col],
                    'operators'     :   [],
                    'children'      :   None
                }

                if newChildren == None:
                    newChildren = child
                else:
                    # append the next __Ω__ to the last children
                    # __Ω__ -> children -> __Ω__ -> children -> ...
                    lastChild = self.__getLastChild (newChildren)

                    if 'children' in lastChild:
                        # assign the last child with the nextNode of the currentNode
                        lastChild['children'] = child

            if self.debug and self.debugLevel > 2: print('\r\n---newChildren---', newChildren)
   
            # get the last node of the new children and append the next node
            # ensure that it was cloned to avoid unnecessary referencing
            childrenCopy = copy.deepcopy(newChildren)
            lastChild = self.__getLastChild (childrenCopy)

            if self.debug and self.debugLevel > 2:
                print('\r\n---lastChild---', lastChild)
                print('\r\n---node to append---', nextNode)
                print('\r\n---remaining columns---', undistributedColumns)

            if 'children' in lastChild:
                    # assign the last child with the nextNode of the currentNode
                    lastChild['children']   =   nextNode
            
            if self.debug and self.debugLevel > 2:
                print('\r\n---children with nextNode---', childrenCopy)
                print('\r\n---curNode---', currentNode)

            currentNode =    copy.deepcopy(currentNode)
            currentNode['__Ω__']        =   undistributedColumns
            currentNode['operators']    =   newOperators
            currentNode['children']     =   childrenCopy
            
            if self.debug and self.debugLevel > 2: print('\r\n---new current---', currentNode)
    

        if self.debug and self.debugLevel > 2:
            print('\r\n-->------[SPLIT SELECTION (__Ω__)]--------')
            print(currentNode)
            print('-->---------------------------------------\r\n')

        # next node to parse
        nextNode = currentNode['children'] 

        return {
            'currentNode'       :     currentNode,
            'nextNode'          :     nextNode,
            'currentNodeType'   :     self.__getNodeType (currentNode),
            'nextNodeType'      :     self.__getNodeType (nextNode)
        }

    def __pushProjectionToCrossJoin (self, currentNode, nextNode):
        # look for relations and push projection on top of the table
        columns = currentNode['__π__']

        # holds the columns who do not belong to any relation
        undistributedColumns = columns.copy ()
        newChildren = []

        # read all the children of cross join but only process those that are table type (__r__)
        # those that are not a table type (__r__) will be retained
        for children in nextNode['__x__']:
            if '__r__' in children:
                # compare table names
                cols = []
                for col in columns:

                    # get the table name of the column and compare it to the table's(__r__) name 
                    tableColumn = col.split('.')
                    if len (tableColumn) >=2:
                        if tableColumn[0] == children['__r__']: 
                            cols.append(col)
                            undistributedColumns.remove(col)

                # move the current table(__r__) down on the tree if there is a match in the list of columns ('__π__')
                # otherwise, retain the same position
                if len(cols) >=1:
                    newChildren.append({
                        '__π__'     :   cols,
                        'children'  :   children
                    })
                else :
                    newChildren.append(children)
            
            else:
                # add the children to the parent as-is for a non __r__ type 
                newChildren.append (children)

        nextNode['__x__']       =   newChildren

        # move columns ('__π__') on top of the table (__r__) if there is a match
        # otherwise, retain the same position
        if len(undistributedColumns) > 0:
            currentNode['__π__']     =   undistributedColumns
            currentNode['children']  =   nextNode
        else:
            currentNode     =   nextNode

        # mark the nex object to be transformed
        if 'children' in  currentNode:
            nextNode    =   currentNode['children']
        else :
            nextNode    =   None
        

        if self.debug and self.debugLevel > 2:
            print('-->------[PUSH (__π__) TO (__x__)]--------')
            print(currentNode)
            print('-->-------------------------------------')

        return {
            'currentNode'       :     currentNode,
            'nextNode'          :     nextNode,
            'currentNodeType'   :     self.__getNodeType (currentNode),
            'nextNodeType'      :     self.__getNodeType (nextNode)
        }

    def __pushProjectionToThetaJoin (self, currentNode, nextNode):
        # look for relations and push projection on top of the table
        columns = currentNode['__π__']

        # holds the columns who do not belong to any relation
        undistributedColumns = columns.copy ()

        newChildren = []
        for children in nextNode['__θ__']:

            # only parse __r__ in children
            if '__r__' in children:
                # compare table names
                cols = []
                for col in columns:
                    tableColumn = col.split('.')
                    if len (tableColumn) >=2:
                        if tableColumn[0] == children['__r__']: 
                            cols.append(col)
                            # track the existing column name
                            undistributedColumns.remove (col)

                # add columns for each relation
                if len(cols) > 0:
                    newChildren.append({
                        '__π__'     :   cols,
                        'children'  :   children
                    })
                else:
                    # prevent adding empty __π__ as descendant
                    newChildren.append (children)
            else:
                # add the children to the parent as-is for a non __r__ type 
                newChildren.append (children)
  
        if len (newChildren) > 0:
            newNode = nextNode
            newNode['__θ__']    =   newChildren

            if len(undistributedColumns) > 0:
                currentNode['children']     =   newNode
                nextNode       =   currentNode['children']
            else:
                currentNode    =   newNode
                nextNode       =   currentNode['children']

            
            if self.debug and self.debugLevel > 2:
                print('-->-----PUSH (__π__) to (__r__ in __θ__) -------')
                print(currentNode)
                print('-->---------------------------------------------')
            
            return {
                'currentNode'       :   currentNode,
                'nextNode'          :   nextNode,
                'currentNodeType'   :   self.__getNodeType (currentNode),
                'nextNodeType'      :   self.__getNodeType (nextNode)
            }

    def __pushSelectionToJoin (self, currentNode, nextNode):
        # look for relations and push selection on top of the table
        columns         =   currentNode['__Ω__']
        nextNodeType    =   self.__getNodeType (nextNode)

        # holds the columns who do not belong to any relation
        undistributedColumns = columns.copy ()

        newChildren     = []
        newOperators    = []
        for children in nextNode[nextNodeType['nodeType']]:

            # only parse __r__ in children
            if '__r__' in children:

                # compare table names
                cols        =   []
                colIndex    =   0

                for col in columns:
                    # split expression by its operator
                    # example: c.b=2 will be transformed to --> ['c.b', '=', '2']
                    columnWithCondition = re.split(r'\s*(=|!=|<=|>=|<|>)\s*', col)

                    if len (columnWithCondition) > 2:
                        tableColumn = columnWithCondition[0].split('.')
                        if len (tableColumn) >=2:
                            if tableColumn[0] == children['__r__']: 
                                
                                # remove operator from the list
                                if len(currentNode['operators']) >= colIndex :
                                    
                                    # this ensures that the previous conditions will be read instead of the next one
                                    # example where clause: a.b=1 and a.c=2 or b.d=3 and b.e=4
                                    # selections: [a.b=1, a.c=2, b.d=3, b.d=4]
                                    # operators: [and, or, and]
                                    # for instance, if the current column index (2) points to b.d=3
                                    # the operation will read the previous condition (or) instead of the current (and)
                                    opIndex     =   colIndex
                                    if opIndex  > 0: opIndex -=  1   
                                    
                                    # only push condition with AND operation
                                    # pushing seclection with OR operation will results to different results
                                    # however, if the selection contains only one item, ignore operators
                                    if (len(currentNode['operators']) > opIndex) or len(currentNode['operators']) < 1: 
                                        if len(currentNode['operators']) >= 1:
                                            if (currentNode['operators'][opIndex].lower() == 'and'):
                                                # track the existing column name                        
                                                cols.append(col)
                                                undistributedColumns.remove (col)
                                                # remove conditional operators from the original and move to the new one
                                                newOperators.append(currentNode['operators'][opIndex])
                                                currentNode['operators'].pop (opIndex)
                                        else:
                                            cols.append(col)
                                            undistributedColumns.remove (col)


                    # increment the next column index
                    colIndex += 1

                # add columns for each relation
                if len(cols) > 0:
                    newChildren.append({
                        '__Ω__'     :   cols,
                        'operators' :   newOperators,
                        'children'  :   children
                    })
                else:
                    # prevent adding empty __π__ as descendant
                    newChildren.append (children)
            else:
                # add the children to the parent as-is for a non __r__ type 
                newChildren.append (children)
  
        if len (newChildren) > 0:
            newNode = nextNode
            newNode[nextNodeType['nodeType']]    =   newChildren

            # do not remove the parent (selection) if there is a column left
            # otherwise, remove the parent completelely (selection)
            if len(undistributedColumns) > 0:
                currentNode['__Ω__']        =   undistributedColumns
                currentNode['children']     =   newNode
            else:
                # replace current node   
                currentNode    =   newNode

                if self.debug and self.debugLevel > 2:
                    print(f"-->-----PUSHED ALL(__Ω__) to (__r__ in {nextNodeType['nodeType']}) -------")
                    print(newNode)
                    print('-->---------------------------------------------\r\n')

            # replce nexNode
            if 'children' in currentNode: nextNode    =   currentNode['children']
            
        if self.debug and self.debugLevel > 2:
            print(f"-->-----PUSH (__Ω__) to (__r__ in {nextNodeType['nodeType']}) -------")
            print(currentNode)
            print('-->---------------------------------------------\r\n')

            
        return {
            'currentNode'           :   currentNode,
            'nextNode'              :   nextNode,
            'currentNodeType'       :   self.__getNodeType (currentNode),
            'nextNodeType'          :   self.__getNodeType (nextNode),
            'undistributedColumns'  :   undistributedColumns,
            'operators'             :   newOperators
        }

    def __pushSelectionsToRelations (self, currentNode, nextNode):
        columns                 =   currentNode['__Ω__']
        lastChildren            =   self.__getLastChild(currentNode)
        lastChildrenNodeType    =   self.__getNodeType (lastChildren)
        parsedNode              =   { 'currentNode'   :   {}}
        originalColumnCount     =   len(columns)
        undistributedColumns    =   columns.copy()

        if self.debug and self.debugLevel > 2:
            print(f"-->-----[PUSHING SELECTIONS TO RELATIONS] -------")
            print(currentNode)
            print('--\r\n---', lastChildren)
            print('-->---------------------------------------------\r\n')


        if lastChildrenNodeType['nodeType'] == '__x__':
            for c in lastChildren:
                if not lastChildren[c] == None:
                    for x in lastChildren[c]:
                        # get the last node
                        l = self.__getLastChild(x)
                        # get the parent of the same node
                        t = self.__getParentNode(x)

                        # as a final check, ensure that it is the same node to be replaced
                        # it must also be a relation (_r__)
                        # otherwise, do not proceed
                        p = self.__getLastChild(t)

                        if self.debug and self.debugLevel > 2:
                            print('\r\n--parentNode--', p)
                            print('\r\n--lastChildren--', lastChildren)
                            print('\r\n--lastNode--', lastChildren[c])
                            print('\r\n--currentNode--', currentNode)
                        
                        # if the parentNode is None, the parent is probably a cross join (__r__)
                        # '__x__' : [{'__r__ : ..} ...]
                        if p == None:
                            # ensure that it contains a selection
                            if '__Ω__' in currentNode:
                                # push to current node to cross join
                                parsedNode = self.__pushSelectionToJoin (currentNode, lastChildren)

                                # update the current node if something has been moved
                                if not originalColumnCount == len(parsedNode['undistributedColumns']):
                                    # replace current node if all has been pushed down
                                    if len(parsedNode['undistributedColumns']) < 1:
                                        currentNode =   nextNode
                                        nextNode    =   currentNode['children']
                                    else:
                                        # update the current node with the remaining selections
                                        currentNode['__Ω__']        =   parsedNode['undistributedColumns']
                                        currentNode['operators']    =   parsedNode['operators']
                                        nextNode                    =   currentNode['children']

                                        if self.debug and self.debugLevel > 2:
                                            print('---parsedNode undistributedColumns', parsedNode['undistributedColumns'])
                                        
                        # proceed if the last child's parent is the same with the last node's parent
                        # this ensures that we are manipulating the right branch of the query tree                
                        if (p == l) and (not p == None):
                            if '__r__' in l:
                                for column in columns:
                                    # split expression by its operator
                                    # example: c.b=2 will be transformed to --> ['c.b', '=', '2']
                                    columnWithCondition = re.split(r'\s*(=|!=|<=|>=|<|>)\s*', column)
                                    if len (columnWithCondition) > 2:
                                        tableColumn = columnWithCondition[0].split('.')
                                        if len (tableColumn) >=2:
                                            if tableColumn[0] == l['__r__']: 
                                                if 'children' in t:
                                                    t['children'] = {
                                                        '__Ω__'     :   [column],
                                                        'operators' :   [],
                                                        'children'  :   l
                                                    }
                                                    undistributedColumns.remove(column)

            if self.debug and self.debugLevel > 2:    
                print('\r\n--current--', currentNode)
                if not nextNode == None:
                    if 'children' in nextNode:
                        print('\r\n----nextNode', nextNode['children'])
                    else:
                        print('\r\n----nextNode No children')
                else:
                    print('\r\n----nextNode is None')
                print('--und', undistributedColumns)

             # if there are changes on the current selection list
            if not originalColumnCount == len(undistributedColumns):
                # if all has been distributed to it respective relations (__r__), replace the current node
                if len(undistributedColumns) < 1:
                    currentNode =   nextNode
                    nextNode    =   currentNode['children']
 
            if self.debug and self.debugLevel > 2:
                print('\r\n--current--', currentNode)

        return {
            'currentNode'       :   currentNode,
            'nextNode'          :   nextNode,
            'currentNodeType'   :   self.__getNodeType (currentNode),
            'nextNodeType'      :   self.__getNodeType (nextNode),
        }

    def __removeDuplicateNextNode (self, currentNode, nextNode):
        # replace the children of the current node with the next node and all of its children 
        currentNodeType     =   self.__getNodeType (currentNode)
        nextNodeType        =   self.__getNodeType (nextNode)

        currentNode['children'] = nextNodeType['nodeChildren']

        if self.debug and self.debugLevel > 2:
            print('-----DUPLICATE CURRENT AND NEXT NODE-------')
            print(currentNode)
            print('--------------------------')

        return {
            'currentNode'       :   currentNode,
            'currentNodeType'   :   currentNodeType,
            'nextNodeType'      :   nextNodeType
        }
    
    def __removeSubsequentProjection (self, currentNode, nextNode,  nextNextNode = None):
        # replace the children of the current node with the next node and all of its children
        if not nextNextNode:
            if 'children' in nextNode:
                currentNode['children'] = nextNode['children']
                nextNode    =   nextNode['children']
        else:
            if 'children' in nextNextNode:
                nextNode['children']    =   nextNextNode['children']
                currentNode['children'] =   nextNode

        if self.debug and self.debugLevel > 2:
            print('-----[Remove subsequent projection(__π__)]-------')
            print(currentNode)
            print('--------------------------')

        return {
            'currentNode'       :   currentNode,
            'nextNode'          :   nextNode,
            'currentNodeType'   :   self.__getNodeType (currentNode),
            'nextNodeType'      :   self.__getNodeType (nextNode)
        }




