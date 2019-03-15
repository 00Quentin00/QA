import http.client as httplib
import urllib, json, time, re, csv, sys, threading
from termcolor import colored
from collections import OrderedDict

httpClient = None
# operation = input("request-type(get/post): ")
# operation = 'post' # initially set to post

def tr(hr, steps, add):
	if 3600%steps == 0:
		tr = [i for i in range(int(hr*3600)+add, int((hr+1)*3600)+add, int(3600/steps))]
	else:
		print("wrong time step")
	return tr

interval1SH = tr(16,5,0) + tr(21,5,0) + tr(22,10,0) + tr(23,25,0) + tr(0,50,0) + tr(0,5,3) + tr(1,60,0) + tr(2,60,0) + tr(3,50,0) + tr(3,5,3) + tr(4,40,0) + tr(5,50,0) + tr(6,50,0) + tr(7,50,0) + tr(8,50,0) + tr(8,5,3) + tr(9,40,0) + tr(10,20,0) + tr(11,10,0) + tr(11,5,3) +tr(12,10,0) + tr(13,5,0) + tr(14,5,0)
interval2SH = tr(17,5,0) + tr(21,5,0) + tr(22,10,0) + tr(23,25,0) + tr(0,50,0) + tr(0,5,3) + tr(1,60,0) + tr(2,60,0) + tr(3,50,0) + tr(3,5,3) + tr(4,40,0) + tr(5,50,0) + tr(6,50,0) + tr(7,50,0) + tr(8,50,0) + tr(8,5,3) + tr(9,40,0) + tr(10,20,0) + tr(11,10,0) + tr(11,5,3) +tr(12,10,0) + tr(13,5,0) + tr(14,5,0)
interval3SH = tr(18,5,0) + tr(22,10,0) + tr(23,25,0) + tr(23,5,3) + tr(0,50,0) + tr(0,5,3) + tr(1,60,0) + tr(1,5,3) + tr(2,60,0) + tr(3,50,0) + tr(4,40,0) + tr(5,50,0) + tr(5,5,3) + tr(6,50,0) + tr(7,50,0) + tr(8,50,0) + tr(9,40,0) + tr(10,20,0) + tr(10,5,3) + tr(11,10,0) +tr(12,10,0) + tr(13,5,0) + tr(15,5,0)
interval4SH = tr(20,5,0) + tr(22,10,0) + tr(23,25,0) + tr(23,5,3) + tr(0,50,0) + tr(0,5,3) + tr(1,60,0) + tr(1,5,3) + tr(2,60,0) + tr(3,50,0) + tr(4,40,0) + tr(5,50,0) + tr(5,5,3) + tr(6,50,0) + tr(7,50,0) + tr(8,50,0) + tr(9,40,0) + tr(10,20,0) + tr(10,5,3) + tr(11,10,0) +tr(12,10,0) + tr(14,5,0) + tr(15,5,0)

interval1LC = tr(1,1,0) + tr( 9,1,0) + tr(17,1,0)
interval2LC = tr(3,1,0) + tr(11,1,0) + tr(19,1,0)
interval3LC = tr(5,1,0) + tr(13,1,0) + tr(21,1,0)
interval4LC = tr(7,1,0) + tr(15,1,0) + tr(23,1,0)

interval1SH.sort()
interval2SH.sort()
interval3SH.sort()
interval4SH.sort()

interval1LC.sort()
interval2LC.sort()
interval3LC.sort()
interval4LC.sort()

def SKSWebAPI(value): # AR, DI, JO, LC, AL, ER
	jsonDict = {}
	print("SKSWebAPI")
	for index in range(0,len(APIKey)):
		jsonDict[APIKey[index]] = value[index]
		if APIKey[index] == 'scode':
			configChar = value[index][:2]
	return jsonDict, configChar

def generator(catg,mno,uid,power,lan,configChar,timeIntervalMin):
	global snoCounter, lock, APIPipeline #,pipeIndex
	while True:
		for second in timeIntervalMin:
			locateTime = (time.time() % (60*60*24))
			if locateTime < float(second):
				created_day = time.strftime("%Y%m%d", time.gmtime((time.time() + 60*60*8)))
				lock.acquire()

				sno = snoCounter[0]
				last_created = snoCounter[1]
				if last_created == created_day:
					sno = str(int(sno) + 1).zfill(3)

				elif created_day > last_created:
					sno = "001"
				else:
					print('generator time error')	

				snoCounter = [sno, created_day]
				lock.release()	
				sigtime = time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime((time.time() + 60*60*8)))
				scode = '{}400010000'.format(configChar)
				APIData = [sno,sigtime,catg,mno,uid,power,lan,scode]
				lock.acquire()
				APIPipeline.append(APIData)
				lock.release()

				last_created = created_day
				time.sleep(float(second) - locateTime )
				break
			else:
				if float(locateTime) > float(timeIntervalMin[-1]):
					# time.sleep( 60*60*24 - locateTime )
					created_day = time.strftime("%Y%m%d", time.gmtime((time.time() + 60*60*8)))
					lock.acquire()

					sno = snoCounter[0]
					last_created = snoCounter[1]
					if last_created == created_day:
						sno = str(int(sno) + 1).zfill(3)

					elif created_day > last_created:
						sno = "001"
					else:
						print('generator time error')	

					snoCounter = [sno, created_day]
					lock.release()	
					sigtime = time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime((time.time() + 60*60*8)))
					scode = '{}400010000'.format(configChar)
					APIData = [sno,sigtime,catg,mno,uid,power,lan,scode]
					lock.acquire()
					APIPipeline.append(APIData)
					lock.release()

					last_created = created_day
					time.sleep(float(second) - locateTime )
					break	
				
				else:
					pass

def post():
	global APIPipeline, snoCounter, lock
	num_of_retries = 5
	time_interval = 3
	lock.acquire()
	APIData = APIPipeline.pop(0)
	lock.release()	
	i = 1
	while i >= 0:
		print(i)
		try:
			data, configChar = SKSWebAPI(APIData)
			json_data = json.dumps(OrderedDict(data))
			headers = {"Content-type": "application/json"
							, "Accept": "application/json"}
							
			# httpClient = httplib.HTTPConnection("54.187.40.215", 6000, timeout=30)
			httpClient = httplib.HTTPConnection("127.0.0.1", 6000, timeout=30)
			httpClient.request("POST", "/", json_data, headers)
			response = httpClient.getresponse()
			print("{1}{3}{2}{3}{3}{3}{0}".format("="*154, configChar, json_data, "\n"))
			print("haha")
		except Exception as e:
			print(e)
			if str(e).find("200") == -1:
				log = "{3}{1}{3}{2}{3}{3}{0}".format("="*154, configChar, json_data, "\n")
				elog = colored("{}".format(e), "cyan")
				print(elog + log)
				time.sleep(time_interval)
			else:
				print("{1}{4}{2}{4}{3}{4}{4}{0}".format("="*154, e, configChar, json_data, "\n"))
				break 
		finally:	
			if httpClient:
				httpClient.close()
		if i == (num_of_retries + 1):
			created_day = time.strftime("%Y%m%d", time.gmtime())
			lock.acquire()
			sno = snoCounter[0]
			last_created = snoCounter[1]
			if last_created == created_day:
				sno = str(int(sno) + 1).zfill(3)
			elif created_day > last_created:
				sno = "001"
			else:
				print('generator time error')
			snoCounter = [sno, created_day]
			lock.release()
			sigtime = time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(time.time() + 60*60*8))		
			ERAPIData = [sno, sigtime, APIData[2], APIData[3], APIData[4], APIData[5], APIData[6], 'ER400010000']
			lock.acquire()
			APIPipeline.append(ERAPIData)
			lock.release()			
		i += 1
	
	

if __name__ == '__main__':
	lock = threading.Lock()
	# pipeIndex = {}
	snoCounter = ["", ""]
	APIPipeline = []
	data = {}
	jsonDict = {}
	APIKey = ['sno','sigtime','catg','mno','uid','power','lan','scode']
	g1 = threading.Thread(target=generator, args=("3", "1312412", "ID-1C21D1C2007A", "A", "1", "SH", interval1SH))

	g5 = threading.Thread(target=generator, args=("3", "1312412", "ID-1C21D1C2007A", "A", "1", "LC", interval1LC))
	g1.start()

	g5.start()

	while True:
		if len(APIPipeline) > 5:
			for i in range(5):
				p = threading.Thread(target=post, args=())
				p.start()
		elif (len(APIPipeline) > 0 and len(APIPipeline) <= 5):
			for i in range(len(APIPipeline)):
				p = threading.Thread(target=post, args=())
				p.start()
		else:
			time.sleep(1000)

		time.sleep(1000)
