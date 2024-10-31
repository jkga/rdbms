import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

# manual access to schema directory
sys.path.append(os.path.abspath(os.path.join(dir_path,  '../' +  os.pardir)))
from schemas.SchemaTableFileLoader import SchemaTableFileLoader

# restore parent directory path
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))


def main(argv):
    # ./data/databases/students.db/student_table.csv
    db_path     =   argv[1]
    fileLoader  =   SchemaTableFileLoader (db_path)

    print('\r\n-->--------[FIRST ROW]--------')
    print (fileLoader.nextRow())
    print('\r\n-->---------[NEXT ROW]--------')
    print (fileLoader.nextRow())
    print('-->---------------------------\r\n')

    # close file
    fileLoader.close ()

if __name__ == '__main__':
    main(sys.argv)