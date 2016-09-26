# -*- coding: utf-8 -*-
import time
import os

FNAME = "/Users/cristtopher/Repository/node-projects/AccessControlMEF2/backend/common/models/XML_EMPLEADOS.xml"

if os.path.isfile(FNAME):
    print "that's a file alright"
    moddate = os.stat(FNAME)[8] # there are 10 attributes this call returns and you want the next to last
    print time.ctime(moddate)
    #
else:
    print "File not found"
