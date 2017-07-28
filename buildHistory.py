#!/usr/local/bin/python
# -*- coding: utf-8 -*-

"""buildHistory.py: Extract all backups from a especific dir
for each extract import bson files to mongo
creat a new db for each file with tgz file name
then export from this db to csv file type
finally drop database created

The generated csv files are hosted in the csvs directory

Warning: This script has hardcoded the fields and the name
from the Multi Export database

Usage: python buildHistory.py <Dumps dir>
example: python buildHistory.py ~/dump
"""

__author__      = "Cristtopher Quintana T. <cquintana@axxezo.com>"

import os
import sys
import subprocess
import tarfile
from pymongo import MongoClient

rootDir = sys.argv[1]

def extract(tarPath):
    tar = tarfile.open(rootDir+'/'+tarPath, 'r')
    for item in tar:
        tar.extract(item, rootDir)

def export(dbName):
    cmd = 'mongoexport --db ' + dbName
        + ' --collection record --type=csv '
        + '--fields run,fullname,profile,is_permitted,input_datetime,'
        + 'destination,output_datetime,comment --out '
        + rootDir + '/csv/' + dbName + '.csv'
    os.system(cmd)
    client = MongoClient('localhost:27017')
    client.drop_database(dbName)

def restore(tarPath):
    tarSplit = tarPath.split('.')
    dbName = tarSplit[0]
    cmd = 'mongorestore --db ' + dbName
        + ' --collection record '
        + rootDir + '/' + dbName + '/AccessControl20/record.bson'
    subprocess.call(cmd,shell=True)
    export(dbName)

for dirName, subdirList, fileList in os.walk(rootDir):
    if not os.path.exists(rootDir + '/csv'):
        os.makedirs(rootDir + '/csv')
    for fname in fileList:
        if (fname.endswith('tgz')):
            extract(fname)
            fnameSplit = fname.split('.')
            dirName = fnameSplit[0]
            restore(dirName)
