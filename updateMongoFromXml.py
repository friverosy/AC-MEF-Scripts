# -*- coding: utf-8 -*-
import time
import os
import urllib2
import glob
from pymongo import MongoClient
import xml.etree.ElementTree as ET

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
    print "Comparing " + last + " with " + new
    if last == new:
        print "Are equals"
        return True
    else:
        print "Are not equals"
        return False


def sendGet(profile):
    print ENDPOINT + profile
    request = urllib2.Request(ENDPOINT + profile)
    try:
        response = urllib2.urlopen(request)
        print response
        if (response.getcode() == 200):
            print "Instruction sent"
        else:
            print "Error to sent instruction"
    except urllib2.URLError as e:
        print e


def get_db():
    client = MongoClient('localhost:27017')
    db = client.AccessControl20
    return db


def add_place(db, name, rut):
    db.place.update({"name": name},{"name" : name, "companyId": rut}, upsert=True)


def add_company(db, name, rut):
    db.company.update({"name": name},{"name" : name, "_id": rut}, upsert=True)


def add_person(db, run, fullname, card, company_code, company, place, profile, is_permitted):
    if card == None:
        db.people.insert({"run": run,"fullname": fullname,"card": 0,"company_code": company_code,"company": company,"place": place,"profile": profile,"is_permitted": is_permitted})
    else:
        db.people.insert({"run": run,"fullname": fullname,"card": card,"company_code": company_code,"company": company,"place": place,"profile": profile,"is_permitted": is_permitted})


def get_place(db):
    return db.place.find_one()


def parseXml(file, profile):
    try:
        db = get_db()
        parser = ET.XMLParser(encoding="utf-8")
        tree = ET.parse(file, parser=parser)
        root = tree.getroot()
        result = db.people.delete_many({})

        if profile == "E":
            for employee in root.findall('EMPLEADO'):
                run = employee[0].text
                fullname = employee[1].text
                card = employee[2].text
                company_code = employee.find('company_code').text
                company = employee[4].text
                place = employee[5].text
                add_place(db, place, company_code)
                add_company(db,company, company_code)
                add_person(db, run, fullname, card, company_code, company, place, profile="E", is_permitted=True)
        else:
            for employee in root.findall('SUBCONTRATISTA'):
                run = employee[0].text
                fullname = employee[1].text
                card = employee[2].text
                company_code = employee.find('company_code').text
                company = employee[4].text
                place = employee[5].text
                add_person(db, run, fullname, card, company_code, company, place, profile="C", is_permitted=True)

    except IOError as io:
        print "Error en readLastFile()"
    except UnboundLocalError as ule:
        print file + " empty"
    except ET.ParseError as pe:
        print pe


def main():
    try:
        # Get last file send
        print "Reading buffer files"
        EM_FILE = min(glob.iglob(DIR + 'EMPLEADOS*.xml'), key=os.path.getctime)
        CO_FILE = min(glob.iglob(DIR + 'SUBCONTRATISTAS*.xml'), key=os.path.getctime)

        if areEquals(EM_FILE, LAST_EMPLOYEES):
            print "Employees are up to date"
        else:
            # update employees from new xml
            print "Updating employees"
            parseXml(EM_FILE, "E")
            # sendGet(EM_FILE)

        if areEquals(CO_FILE, LAST_CONTRACTORS):
            print "Contractors are up to date"
        else:
            # update contractors from new xml
            print "Updating contractors", CO_FILE
            parseXml(CO_FILE, "C")
            # sendGet(CO_FILE)

    except ValueError:
        print "Empty dir"


if __name__ == "__main__":
    main()
