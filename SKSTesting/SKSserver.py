from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi,json, re, time, threading
from queue import Queue
from termcolor import colored

class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		self.wfile.write(bytes("GET request for {}".format(str(self.path)), 'utf8'))

	def do_POST(self):
		global lastSig

		if self.headers['content-type'] is None:
			self.headers['content-type'] = ''
			self.headers['content-length'] = 0
	
		ctype, pdict = cgi.parse_header(self.headers['content-type'])
				
		if ctype == "application/json":
			length = int(self.headers['content-length'])
			content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
			post_data = self.rfile.read(content_length) # <--- Gets the data itself
			self.path_logic(post_data)
		else:
			self.send_error(415, "Only json data is supported.")
			return

		
		locateTime = (time.time() % 60)
		mnoSearch = re.search(r'\"mno\":.?"(\d{7})\"',post_data.decode("utf-8"))
		
		if mnoSearch is None:
			mno = 'log'
		else:
			mno = mnoSearch.group(1)
			sigtime = re.search(r'\"sigtime\":.?\"(.{15,20})\"',post_data.decode("utf-8")).group(1)
			sigEpoch = time.mktime(time.strptime(sigtime, "%Y/%m/%d %H:%M:%S"))
			
			lock.acquire()
			q.get()
			if lastSig > sigEpoch:
				print(colored("###Process out of order", "yellow"))
			lastSig = sigEpoch
			q.put(lastSig)
			lock.release()
		
		code = 200
		self.send_response(code)
		self.send_header('Content-type','application/json')
		self.end_headers()
		self.getHeaders()
		
		print()
		self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))
		current_time = time.strftime("%Y %b %d, %a, %H:%M:%S", time.gmtime())

		file_name = "{}.txt".format(mno)
		log = "UTC: {0} POST {3}{1}{2}{1}{1}".format(current_time,'\n',post_data.decode("utf-8"),code)
		
		with open(file_name, "a") as log_f:
			log_f.write(log)
	def getHeaders(self):
		headersList = []
		for h in self.headers:
			headersList.append({h:self.headers[h]})
		encodedjson = json.dumps(headersList)
		with open('header.json','w') as f:
			f.write(encodedjson)
		self.wfile.write(bytes(encodedjson, 'utf8'))
	def path_logic(self, post_data):
		print("send to machine " + str(json.loads(post_data.decode('utf-8'))["mno"][0:3]))

if __name__ == '__main__':
	print('starting the server...')

	# server_address = ('127.0.0.1', 8081) #localhost:8081
	# URL：http://52.196.55.218:80
	server_address = ('127.0.0.1', 8080)
	httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
	print('runnig the server...')
	lock = threading.Lock()
	q = Queue()
	lastSig = 0
	q.put(lastSig)
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
