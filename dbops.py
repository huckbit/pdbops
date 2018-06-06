#! /usr/bin/python

__title__ = "pdbops"
__description__ = "Refresh the database chain ->export->drop_db->create_db->import->db"
__copyright__ = "Copyright (c) 2018 Massimiliano Ranauro (huckbit@gmail.com)"
__author__ = "Massimiliano Ranauro"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Massimiliano Ranuro"
__email__ = "huckbit@huckbit.com"
__status__ = "development"

import os
import sys
import time
import logging
import ConfigParser as configparser
import pymysql
import pymysql.cursors

# variables
CONFIG = '--defaults-extra-file=' + os.getcwd() + '/config/config.cnf'


# ====================================================
#       Create dir if does not exist
# ====================================================
def create_dir(dirname):
    if not os.path.isdir(os.getcwd() + '/' + dirname):
        os.makedirs(dirname)


# ====================================================
#       Current time
# ====================================================
def current_time():
    return time.strftime("[%Y-%m-%d %H:%M:%S] ")


# ====================================================
#  READ CLIENT CONFIG FILE
#  return the value of the chosen element
# ====================================================
def client(value):
    parser = configparser.ConfigParser()
    parser.read(os.getcwd() + '/config/config.cnf')
    parameter = dict(parser.items('client'))

    if parameter[value]:
        return parameter[value]


# ====================================================
#       Connect to the database
# ====================================================
def connect_db(dbname):

    callerFunc = sys._getframe(1).f_code.co_name

    try:

        connection = pymysql.connect(host=client('host'),
                                     user=client('user'),
                                     password=client('password'),
                                     db=dbname,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        if connection:
            logging.info(current_time() + callerFunc + ' Database connection for dbname=' + dbname + 'successfull.')
            return connection

    except pymysql.InternalError as error:
        code, message = error.args
        logging.error("Error: >>>", code, message)
        return "Error: >>>", code, message


# ====================================================
#       LIST AVAILABLE DATABASES
# ====================================================
def select_db(dbname):
    os.system('clear')
    connection = connect_db(dbname)
    with connection.cursor() as cursor:
        sql = "SHOW DATABASES"
        cursor.execute(sql)
        results = cursor.fetchall()
        connection.close()

    for i, dbname in enumerate(results):
        if dbname['Database'] != 'performance_schema' and dbname['Database'] != 'information_schema' and dbname['Database'] != 'mysql':
            print (i, str(dbname["Database"]))

    option = int(input("Inser the number of the database you want to import: "))
    selected_db = results[option]
    return selected_db["Database"]


# ====================================================
#       CHECK IF THE DATABASE IS NOT EMPTY
# ====================================================
def tables_list(db_name):

    connection = connect_db(db_name)
    with connection.cursor() as cursor:
        sql = "SHOW TABLES FROM " + db_name
        cursor.execute(sql)
        results = cursor.fetchall()
        connection.close()

    if results:
        return True


# ====================================================
#       EXPORT DATABASE DUMP
# ====================================================
def export_db(dbname):
    # create dump folder if does not exist
    create_dir('dump')

    command = 'mysqldump ' + CONFIG + ' ' + dbname + ' > ' + os.getcwd() + '/dump/' + dbname + '.sql'

    # check if the database is not empty
    if tables_list(dbname):

        # try to export the database dump
        try:
            print('Exporting the database: ' + dbname + '...')
            os.system(command)

        except OSError:

            print('Dump export failed')
            return False

        # check if the export is completed and print a message
        export_path = os.getcwd() + '/dump/' + dbname + '.sql'
        if os.path.isfile(export_path):
            print('Dump completed!')
        else:
            print('Database dump error')

    else:
        print("Empty database. Export dump skipped")


# ====================================================
#       DROP THE DATABASE IF EXISTS
# ====================================================
def drop_db(dbname):

    if connect_db(dbname):

        try:
            # create the command
            drop_command = 'mysqladmin ' + CONFIG + ' -f DROP ' + dbname

            # drop the database
            print('Dropping the db: ' + dbname)
            os.system(drop_command)

        except OSError:

            return False


# ====================================================
#       CREATE DATABASE
# ====================================================
def create_db(dbname):
    try:

        create_db_command = 'mysql ' + CONFIG + ' -e "CREATE DATABASE ' + dbname + ' $DB CHARACTER SET utf8 COLLATE utf8_general_ci"'
        os.system(create_db_command)

        """if you can connect to the db, the db exists"""
        if connect_db(dbname):
            print ('Database ' + dbname + ' Created!')

    except OSError:

        return False


# ====================================================
#       OPEN DUMP FILE FROM IMPORT DIRECTORY
# ====================================================
def open_dump():
    # list the file inside the folder import and allow to choice the dump file
    importPath = os.getcwd() + '/import'

    # check if the folder exists
    if os.path.isdir(importPath):

        fileList = os.listdir(importPath)

        # enumerate the list fo files to allow the selection
        os.system('clear')
        print('Available dump files inside import folder:')
        for i, fileName in enumerate(fileList):
            print(i, fileName)

        # ask to select a dump and save the selection
        print('--------------------------------------------------')
        option = int(input("insert the number of the file you want to import: "))

        dumpName = fileList[option]

        # if the file name contain white spaces you need to rename and return it
        # if blank space is present you need to rename the file
        check_blank_char = dumpName.count(' ')

        if check_blank_char:

            # create the path
            renameThis = importPath + '/' + dumpName

            # rename the file inside the dir
            os.rename(renameThis, renameThis.replace(" ", "."))

            # remove from dumpName the blank spaces
            renamed_dump_name = dumpName.replace(" ", ".")

            # check if the renamed file is the directory before to return the new name
            if os.path.isfile(os.getcwd() + '/import/' + renamed_dump_name):
                return renamed_dump_name
            else:
                print('Error renaming the file')

        else:
            # if the fileName does not contain blank character return it
            return dumpName

    else:
        print('Copy the dump you want import inside the folder "import"')


# ====================================================
#       IMPORT DATABASE DUMP
# ====================================================
def import_dump(dump_file, dbName):
    import_command = 'mysql ' + CONFIG + ' ' + dbName + ' < ' + os.getcwd() + '/import/' + dump_file
    # print(import_command)
    print('Importing dump >>> ' + dump_file + '...')
    os.system(import_command)

    # if the query returns tables import is completed

    if tables_list(dbName):
        print('Dump import completed!')


# ====================================================
#       ARCHIVE DUMP
# ====================================================
def archive():
    # todo: ask to archive or delete the backup file after the import
    pass


# ====================================================
#       MAIN
# ====================================================
def main():
    create_dir('log')
    logging.basicConfig(filename=os.getcwd() + '/log/' + time.strftime("%Y%m%d%.H%I%S") + '.refresh.log',
                        level=logging.DEBUG)
    dump_file = open_dump()
    db_name = select_db('mysql')

    if db_name and dump_file:
        os.system('clear')
        export_db(db_name)
        drop_db(db_name)
        create_db(db_name)
        import_dump(dump_file, db_name)
        # archive()
    else:
        exit(0)


main()


# todo: allow gzip or unzip the file before the import
# todo: rename file with punctuation
