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
import re
import string


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
        print "Error en readLastFile()", io.strerror
        SLACK.notify(text="Error reading last file!: "+str(io), channel="#multiexportfoods", username="Multi-Bot", icon_emoji=":robot_face:")
        print profile + " -> " + io.strerror
        f = file(profile, "w")
        return None
    except UnboundLocalError as ule:
        print profile + " empty", ule
        SLACK.notify(text="Error reading last file!: "+str(ule), channel="#multiexportfoods", username="Multi-Bot", icon_emoji=":robot_face:")
        return None


def saveLastFile(text, last_file):
    try:
        file = open(last_file, "a")
        file.write(text + "\n")
        #print "file saved with ", text
    except IOError as io:
        print "Error en saveLastFile()", io
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


def get_db():
    client = MongoClient('0.0.0.0:27017')
    db = client.AccessControl20
    return db


def add_place(db, name, rut):
    try:
        db.place.update({"name": name},{'$set': {"name" : name, "companyId": rut}}, upsert=True)
    except:
        print('Error updating places')
        SLACK.notify(text="Error adding places", channel="#multiexportfoods", username="Multi-Bot", icon_emoji=":robot_face:")


def add_company(db, name, rut):
    try:
        db.company.update({"name": name},{"name" : name, "_id": rut}, upsert=True)
    except:
        print('Error updating companies')
        SLACK.notify(text="Error adding companies", channel="#multiexportfoods", username="Multi-Bot", icon_emoji=":robot_face:")


def add_person(db, run, fullname, card, company_code, company, place, profile, is_permitted):
    try:
        #print run.strip(), fullname.strip(), card, company_code, company, place, profile, is_permitted
        people = db.people
        if card == None:
            response = people.insert_one({"run":run.strip(),"fullname": fullname.strip(),"card": 0,"company_code": company_code,"company": company,"place": place,"profile": profile,"is_permitted": is_permitted})
        else:
            response = people.insert_one({"run":run.strip(),"fullname": fullname.strip(),"card": int(card),"company_code": company_code,"company": company,"place": place,"profile": profile,"is_permitted": is_permitted})
        #print response
    except Exception as e:
        print "Error inserting person ", run, e
        SLACK.notify(text="Error inserting person to Mongo from XML with rut: "+run+" "+str(e), channel="#multiexportfoods", username="Multi-Boot", icon_emoji=":robot_face:")


def get_place(db):
    return db.place.find_one()


def parseXml(file, profile):
    try:
        db = get_db()
        parser = ET.XMLParser(encoding="iso-8859-5")
        tree = ET.parse(file, parser=parser)

        root = tree.getroot()

        if profile == "E":
            try:
                db.place.drop()
                db.people.delete_many({"profile": "E"})
            except Exception as e:
                print "Error droping places or Employees", e
                return
            for employee in root.findall('EMPLEADO'):
                try:
                    run = employee[0].text
                    fullname = employee[1].text
                    card = employee[2].text
                    company_code = employee.find('company_code').text
                    company = employee[4].text
                    place = employee[5].text
                    add_place(db, place, company_code)
                    add_company(db,company, company_code)
                    print run, fullname, card
                    add_person(db, run, fullname, card, company_code, company, place, profile="E", is_permitted=True)
                except Exception as e:
                    print "Error parsing", run, fullname, card, company_code, company, place, profile, e
                    #SLACK.notify(text="Error parsing rut: "+str(run), channel="#multiexportfoods", username="Multi-Bot", icon_emoji=":robot_face:")
            #SLACK.notify(text="People updated!", channel="#multiexportfoods", username="Multi-Bot", icon_emoji=":robot_face:")
            print "Employees updated!"
            # Update API state to true, for update people on PDA.
            for x in range(1, 5):
                sendUpdate(x)
            saveLastFile(file, DIR + LAST_EMPLOYEES)
        else:
            db.people.delete_many({"profile": "C"})
            for employee in root.findall('SUBCONTRATISTA'):
                run = employee[0].text
                fullname = employee[1].text
                card = employee[2].text
                company_code = employee.find('company_code').text
                company = employee.find('company').text
                place = employee[5].text
                add_person(db, run, fullname, card, company_code, company, place, profile="C", is_permitted=True)
            #SLACK.notify(text="Contractors updated!", channel="#multiexportfoods", username="Multi-Bot", icon_emoji=":robot_face:")
            print "Contractors updated!"
            saveLastFile(file, DIR + LAST_CONTRACTORS)
    except IOError as io:
        print "Error en parseXML()", io
        #SLACK.notify(text="Error parsing XML!: "+srt(io), channel="#multiexportfoods", username="Multi-Bot", icon_emoji=":robot_face:")
    except UnboundLocalError as ule:
        print file + " empty", ule
        #SLACK.notify(text="Error parsing XML!: "+srt(ule), channel="#multiexportfoods", username="Multi-Bot", icon_emoji=":robot_face:")
    except ET.ParseError as pe:
        print pe
        SLACK.notify(text="Error parsing XML!: "+str(pe), channel="#multiexportfoods", username="Multi-Bot", icon_emoji=":robot_face:")

def sendUpdate(pda):
    try:
        payload = {"updatePeople": True, "pda": pda}
        r = requests.post(SERVER + ":" + PORT + "/api/states", data=payload)
        #print(r.text)
        #print(r.status_code, r.reason)
    except:
        print('Error updating states')
        #SLACK.notify(text="Error updating states", channel="#multiexportfoods", username="Multi-Bot", icon_emoji=":robot_face:")

def main():
    try:
        # Get last file send
        EM_FILE = max(glob.iglob(DIR + 'EMPLEADOS*.xml'), key=os.path.getctime)
        CO_FILE = max(glob.iglob(DIR + 'SUBCONTRATISTAS*.xml'), key=os.path.getctime)

        db = get_db()
        if areEquals(EM_FILE, DIR + LAST_EMPLOYEES):
            print "Employees are up to date"
        else:
            # update employees from new xml
            print "Have differents!!, Update start..."
            parseXml(EM_FILE, "E")

        if areEquals(CO_FILE, DIR + LAST_CONTRACTORS):
            print "Contractors are up to date"
        else:
            # update contractors from new xml
            parseXml(CO_FILE, "C")
            for x in range(1, 5):
                sendUpdate(x)

    except ValueError as ve:
        print "Empty dir", ve
        SLACK.notify(text="Error, empty dir marcasmef", channel="#multiexportfoods", username="Multi-Bot", icon_emoji=":robot_face:")


if __name__ == "__main__":
    main()

