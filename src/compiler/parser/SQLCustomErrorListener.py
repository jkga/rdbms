from antlr4.error.ErrorListener import ErrorListener

class SQLCustomErrorListener(ErrorListener):
    def __init__(self):
        super(SQLCustomErrorListener, self).__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # Catch the mismatched input and log it
        error_message = f"Syntax Error: line {line}, column {column}, {msg}"
        self.errors.append(error_message)
        return self.errors