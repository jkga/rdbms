import antlr4
from antlr4 import *
import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

from compiler.parser.SQLLexer import SQLLexer
from compiler.parser.SQLParser import SQLParser
from compiler.parser.SQLVisitor import SQLVisitor
from compiler.parser.SQLCustomErrorListener import SQLCustomErrorListener


class SQLAnnotate:

    def __init__(self, **kwargs):
        self.lexer = None
        self.input = None
        self.stream = None
        self.parser = None
        self.tree = None
        self.schema = None
        self.visitor = None
        self.inputStream = None
        self.error = None
        self.data = None
        self.debug = False

        self.errorList = [
            "0000:SQL NOT FOUND",
            "0001:SCHEMA NOT DEFINED",
            "0002: SYNTAX ERROR"
        ]

        # detect sql query
        if 'sql' in kwargs: 
            self.input = kwargs['sql']
        else:
            self.error = self.errorList[0]
        
        # ensure that schema is loaded
        if 'schema' in kwargs: 
            self.schema = kwargs['schema']
        else:
            self.error = self.errorList[1]
    
    def setDebug (self, debug = False):
        self.debug = debug
        return self

    def loadSchema (self, schema):
        self.schema = schema
        return self
    
    def annotate (self):

        if not self.input == None:
            try:
                self.lexer          =   SQLLexer(self.input)
                self.stream         =   CommonTokenStream(self.lexer)
                self.parser         =   SQLParser(self.stream)
                self.errorListener  =   SQLCustomErrorListener ()

                self.parser.removeErrorListeners()
                self.parser.addErrorListener(self.errorListener)

                self.tree = self.parser.sql_statement()

                if self.errorListener.errors: self.error = self.errorListener.errors

                
                if self.parser.getNumberOfSyntaxErrors() > 0:
                    self.error = self.errorListener.errors
                
                if self.error == None:
                    # walk to parse tree and generate annnotations
                    self.visitor = SQLVisitor()
                    self.visitor.loadSchema (self.schema)
                    self.data = self.visitor.setDebug(self.debug).visit(self.tree)
                    
            except Exception as e:
                self.error  =   e
                self.data   =   []
        
        return self
    
    def getAnnotations (self):
        return {
            'error': self.error,
            'data': self.data
        }
