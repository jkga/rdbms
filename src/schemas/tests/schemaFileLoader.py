import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

# manual access to schema directory
sys.path.append(os.path.abspath(os.path.join(dir_path,  '../' +  os.pardir)))
from schemas.SchemaFileLoader import SchemaFileLoader

# restore parent directory path
sys.path.append(os.path.abspath(os.path.join(dir_path, os.pardir)))


def main(argv):
    # ./data/databases/students.db/students.db.json
    db_path     =   argv[1]
    fileLoader  =   SchemaFileLoader (db_path)
    results     =   fileLoader.getResults ()

    print('\r\n-->---------[RESULTS]--------')
    print (results)
    print('-->------------------------------\r\n')

    if 'schema' in results:
        print('\r\n-->---------[DATABSE]--------')
        print (results['schema'].getDatabaseName (), '\r\n')
        print (results['schema'].getTables())
        print('-->------------------------------\r\n')
    
if __name__ == '__main__':
    main(sys.argv)