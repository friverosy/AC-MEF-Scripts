# -*- coding: utf-8 -*-
# Need Python-2.7.6
import time
import os
import urllib2
import glob
from pymongo import MongoClient
import xml.etree.ElementTree as ET
import slackweb
import requests


DIR = "/opt/marcasmef/"
LAST_EMPLOYEES = "lastEmployees.txt"
LAST_CONTRACTORS = "lastContractors.txt"
SERVER = "http://0.0.0.0"
PORT = "3000"
ENDPOINT = SERVER + ":" + PORT +"/api/people/updateDbFromXml?file="
SLACK = slackweb.Slack(url="https://hooks.slack.com/services/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")

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


def saveLastFile(text, last_file):
    try:
        file = open(last_file, "a")
        file.write(text + "\n")
        #print "file saved with ", text
    except IOError as io:
        print "Error en saveLastFile()"
        print last_file + " -> " + io.strerror
        f = file(last_file, "w")


def areEquals(new, last_file):
    # Get last file used
    last = readLastFile(last_file)
    # strip() == trim()
    if last != None:
        last = last.strip()
    else:
        # if file not exist, create.
        saveLastFile(new, last_file)
        return False

    # Compare files
    print "Comparing " + new + " with " + last
    if last == new:
        #print "Are equals"
        return True
    else:
        #print "Are not equals"
        return False


def sendGet(profile):
    #print ENDPOINT + profile
    request = urllib2.Request(ENDPOINT + profile)
    try:
        response = urllib2.urlopen(request)
        #print response
        if (response.getcode() == 200):
            print "Instruction sent"
        else:
            print "Error to sent instruction"
    except urllib2.URLError as e:
        print e


def get_db():
    client = MongoClient('0.0.0.0:27017')
    db = client.AccessControl20
    return db


def add_place(db, name, rut):
    db.place.update({"name": name},{'$set': {"name" : name, "companyId": rut}}, upsert=True)


def add_company(db, name, rut):
    db.company.update({"name": name},{"name" : name, "_id": rut}, upsert=True)


def add_person(db, run, fullname, card, company_code, company, place, profile, is_permitted):
    #print run.strip(), fullname.strip(), card, company_code, company, place, profile, is_permitted
    if card == None:
        db.people.insert_one({"run":run.strip(),"fullname": fullname.strip(),"card": 0,"company_code": company_code,"company": company,"place": place,"profile": profile,"is_permitted": is_permitted})
    else:
        db.people.insert_one({"run":run.strip(),"fullname": fullname.strip(),"card": int(card),"company_code": company_code,"company": company,"place": place,"profile": profile,"is_permitted": is_permitted})


def get_place(db):
    return db.place.find_one()


def parseXml(file, profile):
    try:
        db = get_db()
        parser = ET.XMLParser(encoding="utf-8")
        tree = ET.parse(file, parser=parser)
        root = tree.getroot()

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
                # Check if already exist.
                while (db.people.find({"run": { $eq: run }}).count() > 0):
                    SLACK.notify(text="Person "+run+" already exist!", channel="#multiexportfoods", username="Multi-Boot", icon_emoji=":robot_face:")
                    db.people.remove({"run": run})
                add_person(db, run, fullname, card, company_code, company, place, profile="E", is_permitted=True)
            SLACK.notify(text="People updated!", channel="#multiexportfoods", username="Multi-Boot", icon_emoji=":robot_face:")
            #print "People updated!"
            saveLastFile(file, DIR + LAST_EMPLOYEES)
        else:
            for employee in root.findall('SUBCONTRATISTA'):
                run = employee[0].text
                fullname = employee[1].text
                card = employee[2].text
                company_code = employee.find('company_code').text
                company = employee.find('company').text
                place = employee[5].text
                add_person(db, run, fullname, card, company_code, company, place, profile="C", is_permitted=True)
            SLACK.notify(text="Contractors updated!", channel="#multiexportfoods", username="Multi-Boot", icon_emoji=":robot_face:")
            #print "People updated!"
            saveLastFile(file, DIR + LAST_CONTRACTORS)

    except IOError as io:
        print "Error en readLastFile()"
    except UnboundLocalError as ule:
        print file + " empty"
    except ET.ParseError as pe:
        print pe
        SLACK.notify(text="Error parsing XML!" , channel="#multiexportfoods", username="Multi-Boot", icon_emoji=":robot_face:")

def sendUpdate():
    r = requests.post(SERVER + ":" + PORT + "/api/states", data={"updatePeople": True})
    print(r.status_code, r.reason)

def main():
    try:
        # Get last file send
        EM_FILE = max(glob.iglob(DIR + 'EMPLEADOS*.xml'), key=os.path.getctime)
        CO_FILE = max(glob.iglob(DIR + 'SUBCONTRATISTAS*.xml'), key=os.path.getctime)

        db = get_db()
        if areEquals(EM_FILE, DIR + LAST_EMPLOYEES):
            print "Employees are up to date"
            # SLACK.notify(text="Employees are up to date", channel="#multiexportfoods", username="Multi-Boot", icon_emoji=":robot_face:")
        else:
            # update employees from new xml
            db.place.drop()
            db.people.delete_many({"profile": "E"})
            parseXml(EM_FILE, "E")
            # sendGet(EM_FILE)
            sendUpdate()

        if areEquals(CO_FILE, DIR + LAST_CONTRACTORS):
            print "Contractors are up to date"
            # SLACK.notify(text="Contractors are up to date", channel="#multiexportfoods", username="Multi-Boot", icon_emoji=":robot_face:")
        else:
            # update contractors from new xml
            db.people.delete_many({"profile": "C"})
            parseXml(CO_FILE, "C")
            # sendGet(CO_FILE)
            sendUpdate()

    except ValueError as ve:
        print "Empty dir", ve


if __name__ == "__main__":
    main()
