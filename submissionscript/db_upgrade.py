#!/usr/bin/python3

import sys
import glob
import re
import mysql.connector
from mysql.connector import errorcode

dbVersion = 0
dbScripts = sys.argv[1]
dbUser = sys.argv[2]
dbServer = sys.argv[3]
dbName = sys.argv[4]
dbPassword = sys.argv[5]

def getDbConnection():
    try:
        cnx = mysql.connector.connect(user=dbUser, password=dbPassword, host=dbServer, database=dbName)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print("Error: ", err)
    else:
        return cnx

def createTable(query):
    cnx = getDbConnection()
    cursor = cnx.cursor()
    cursor.execute(query)
    cnx.close()

def insertTable(query):
    cnx = getDbConnection()
    cursor = cnx.cursor()
    cursor.execute(query)
    cnx.commit()
    print(cursor.rowcount, "record inserted.")
    cnx.close()

def updateTable(version):
    print("UPDATE DB VERSION:", version, "\n")
    cnx = getDbConnection()
    cursor = cnx.cursor()
    cursor.execute("UPDATE versionTable SET version = "+version)
    cnx.commit()
    cnx.close()

def getDbVersion():
    cnx = getDbConnection()
    cursor = cnx.cursor()
    cursor.execute("SELECT version from versionTable;")
    result = cursor.fetchone()
    dbVersion = result[0]
    print("DB VERSION: ", dbVersion, "\n")
    cursor.close()
    cnx.close()
    return dbVersion

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def getSortedSqlFiles():
    scriptPath = dbScripts+"*.sql"
    sqlFiles = glob.glob(scriptPath)
    print("SQL FILES: ", sqlFiles, "\n")
    sqlFiles.sort(key=natural_keys)
    print("SORTED SQL FILES: ", sqlFiles, "\n")
    return sqlFiles

def verifyAndRunScript():
    dbVersion = getDbVersion()
    sqlFiles = getSortedSqlFiles()
    
    for f in sqlFiles:
        versionInFile = re.findall(r'^\D*(\d+)', f)
        if len(versionInFile) > 0 and int(versionInFile[0]) > dbVersion :
            try:
                with open(f, 'r') as file:
                    query = file.read().replace('\n', '')
                print(query)
                if query.upper().startswith("CREATE"):
                    updateTable(versionInFile[0]) 
                    createTable(query)
                if query.upper().startswith("INSERT"):
                    updateTable(versionInFile[0])
                    insertTable(query)
            except Exception as e:
                print("Error:", e, "\n")
                         
    
    print("Latest DB version: ", getDbVersion())

verifyAndRunScript()