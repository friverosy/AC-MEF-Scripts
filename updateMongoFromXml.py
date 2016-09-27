# -*- coding: utf-8 -*-
import time
import os
import urllib2
import glob

DIR = "/Users/cristtopher/Desktop/xmls/"
LAST_EMPLOYEES = "lastEmployees.txt"
LAST_CONTRACTORS = "lastContractors.txt"
SERVER = "http://0.0.0.0"
PORT = "3000"
ENDPOINT = SERVER + ":" + PORT +"/api/people/updateDbFromXml?file="

def readLastFile(profile):
    try:
        with open(profile, "r") as lf:
            for line in lf:
                pass
            last = line
        return last
    except IOError as io:
        print "Error en readLastFile()"
        print profile + " -> " + io.strerror
        f = file(profile, "w")
        return None
    except UnboundLocalError as ule:
        print profile + " empty"
        return None


def saveLastFile(new_file, profile):
    try:
        file = open(profile, "a")
        file.write(new_file + "\n")
    except IOError as io:
        print "Error en saveLastFile()"
        print profile + " -> " + io.strerror
        f = file(profile, "w")


def areEquals(new, profile):
    # Get last file used
    last = readLastFile(DIR + profile)
    # strip() == trim()
    if last != None:
        last = last.strip()
    else:
        # if file not exist, create.
        saveLastFile(new, DIR + profile)
        return False

    # Compare employees files
    if last == new:
        return True
    else:
        return False


def sendGet(profile):
    request = urllib2.Request(ENDPOINT + profile)
    try:
        response = urllib2.urlopen(request)
        if (response.getcode() == 200):
            print "Instruction sent"
        else:
            print "Error to sent instruction"
    except urllib2.URLError as e:
        print e


def main():
    try:
        # Get last file send
        EM_FILE = min(glob.iglob(DIR + 'EMPLEADOS*.xml'), key=os.path.getctime)
        CO_FILE = min(glob.iglob(DIR + 'SUBCONTRATISTAS*.xml'), key=os.path.getctime)

        if areEquals(EM_FILE, LAST_EMPLOYEES):
            # update employees from new xml
            print "updating employees"
            sendGet(EM_FILE)

        if areEquals(CO_FILE, LAST_CONTRACTORS):
            # update contractors from new xml
            print "updating contractors"
            sendGet(CO_FILE)

    except ValueError:
        print "Empty dir"


if __name__ == "__main__":
    main()
