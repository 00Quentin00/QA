import json
from pprint import pprint
import re
import codecs
from sys import argv
import time
from os import system
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("startT", 
                    help="start time in %%Y.%%m.%%d:%%H:%%M:%%S format")
parser.add_argument("endT", 
                    help="end time in %%Y.%%m.%%d:%%H:%%M:%%S format")
parser.add_argument("-j",
                    "--JumboID", 
                    help="JumboID. Accept muiltiple -j arguments. If not given, will return result count in total", 
                    action='append',
                    default=[])
a = parser.parse_args()

startT = a.startT
endT = a.endT

form = '%Y.%m.%d:%H:%M:%S'
startE = int(time.mktime(time.strptime(startT, form)))
endE = int(time.mktime(time.strptime(endT, form)))

# system('curl -v -H "X-Papertrail-Token: $PAPERTRAIL_API_TOKEN" https://papertrailapp.com/api/v1/events/search.json\?system_id\=1840794891\&min_time\={}\&max_time\={}>sks{}-{}.json'.format(startE,endE,startT,endT))
system('curl -v -H "X-Papertrail-Token: $PAPERTRAIL_API_TOKEN" https://papertrailapp.com/api/v1/events/search.json\?system_id\=1840794891\&max_time\={}>sks{}-{}.json'.format(endE,startT,endT))
with codecs.open('sks{}-{}.json'.format(startT,endT), 'r', 'utf8') as f:
    data = json.load(f)

event = data["events"]

SH = 0
SW = 0
DI = 0
AR = 0
JO = 0
LC = 0
ER = 0

def sum(msg,SH,SW,DI,AR,JO,LC,ER):
    m = re.search(r"\"scode\":\"(\w{2})\d{9},\"",msg)
    if m.group():
            code = m.group(1)
            if code == "SH":
                SH += 1
            elif code == "SW":
                SW += 1
            elif code == "DI":
                DI += 1
            elif code == "AR":
                AR += 1
            elif code == "JO":
                JO += 1
            elif code == "LC":
                LC += 1
            elif code == "ER":
                ER += 1
    return SH,SW,DI,AR,JO,LC,ER

for key in event:
    id = re.search(r"\"uid\":\"(ID-\w{12})\"",key["message"]).group(1)
    if a.JumboID != []:
        if id in a.JumboID:
            SH,SW,DI,AR,JO,LC,ER = sum(key["message"],SH,SW,DI,AR,JO,LC,ER) 
    else:
        SH,SW,DI,AR,JO,LC,ER = sum(key["message"],SH,SW,DI,AR,JO,LC,ER) 

print("Count\nSH: {}\nSW: {}\nDI: {}\nAR: {}\nJO: {}\nLC: {}\nER: {}\n".format(SH,SW,DI,AR,JO,LC,ER))