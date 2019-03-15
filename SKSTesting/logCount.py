import re
import sys

file = sys.argv[1]

with open(file) as f:
	s = f.read()

# print(s)

counter = {}
HRcounter = {
             "00": {},
             "01": {},
             "02": {},
             "03": {},
             "04": {},
             "05": {},
             "06": {},
             "01": {},
             "07": {},
             "08": {},
             "09": {},
             "10": {},
             "11": {},
             "12": {},
             "13": {},
             "14": {},
             "15": {},
             "16": {},
             "17": {},
             "18": {},
             "19": {},
             "20": {},
             "21": {},
             "22": {},
             "23": {} }

lines = s.split("\n\nUTC: ")

### sort by alert and hour
for line in lines:
	logHR = re.search(r'\d{2}\s(\d{2}):\d{2}\:\d{2}',line).group(1) 
	logResponse = re.search(r'POST\s(\d+)',line).group(1)
	logEvent = re.search(r'scode\"\:\s\"(\w{2})',line).group(1) 
	if logResponse == "200":
		hr = logHR
		eventCode = logEvent
		if eventCode in counter:
			count = counter[eventCode]
			count += 1
		else:
			count = 1
		counter[eventCode] = count

		if eventCode in HRcounter[hr]:
			count = HRcounter[hr][eventCode]
			count += 1
		else:
			count = 1
		HRcounter[hr][eventCode] = count

	else:
		pass

###SUM
counterValue = counter.values()
counterSum = 0
for i in counterValue:
	counterSum += i 

HRcounterList = HRcounter.values()
HRcounterValue = [ i.values() for i in HRcounterList]
HRcounterSum = 0
for i in HRcounterValue:
	for j in i:
		HRcounterSum += j 

# print(HRcounter)

### percentage
def percentage(HRcounter): 
	print("Percentage of Each Hour for SH:{}".format('\n'))
	for key, value in HRcounter.items():
		count = 0
		if 'SH' in value:
			count += value['SH']
		p = count/counter['SH']*10000
		percentage = "{}%".format(int(p)/100)
		print("{}: {}".format(key, percentage))

###pretty
def pretty(d, indent=0):
	print("Hourly counter:")
	for key, value in d.items():
		if isinstance(value, dict):
			if len(value) != 0:
				print('\n' + '\t' * indent + str(key))
				for keys, values in value.items(): 
					print('\t' * (indent+1) + str(keys) + ': ' + str(values))
		else:
			print('\t' * indent + str(key) + ': ' + str(value))

print()
print("MNO {}{}".format(re.search(r'\w{7}',file).group(), '\n'))
print("counter: {}".format(counter))
print('\n' + "Total: {}".format(counterSum))
print('\n' + "="*100)
pretty(HRcounter)
print('\n' + "Total: {}".format(HRcounterSum))
print('\n' + "="*100)
percentage(HRcounter)
print()