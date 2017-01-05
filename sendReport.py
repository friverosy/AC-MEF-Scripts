# -*- coding: utf-8 -*-
# Need Python-2.7.6
import requests
import urllib
import pandas as pd

url = "http://0.0.0.0:3000/api/records?filter[order]=input_datetime%20DESC"
json = urllib.urlopen(url)
df = pd.read_json(json)
#df['input_datetime'].plot(figsize=(15,5));

del df['bus']
del df['company_code']
del df['id']
del df['is_input']
del df['reviewed']
del df['type']
del df['updating']

df.to_excel('output.xls', index=False, sheet_name='Registos')
