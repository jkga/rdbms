import antlr4
import sys
import os
from antlr4 import *
from dotenv import load_dotenv

dir_path = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.abspath(os.path.join(dir_path,  '../' +  os.pardir)))
# restore parent directory path
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))

from engine.SQLQueryEngine import SQLQueryEngine

# load env variables
load_dotenv(dotenv_path=f'configs/.env')

databasePath        =   os.getenv('DATABASE_PATH')
databaseName        =   'students' 

if __name__ == '__main__':
    # SAMPLE QUERY
    # "SELECT * FROM (SELECT * FROM STUDENT, STUDCOURSE WHERE STUDENT.StudNo='2007-52623' OR STUDCOURSE.AcadYear>2000 AND STUDCOURSE.CNo='COMM 10');"
    engine = SQLQueryEngine ()
    engine.setDatabasePath (databasePath)
    engine.useDatabase (databaseName)
    engine.parse (sys.argv[1])

    print('\r\n-----------[DATABASES]----------')
    print (engine.showDatabases ())

    print('\r\n-----------[TABLES]----------')
    print (engine.showTables ())

    print('\r\n-----------[STUDENT COLUMNS]----------')
    print (engine.showColumns ("STUDENT"))

    print('\r\n-----------[RESULTS]----------')
    print('TOTAL NUMBER OF ROWS :', engine.getRowCount ())
    print('EXECUTION TIME :', engine.getExecutionTime ())