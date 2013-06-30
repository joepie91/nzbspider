import requests, random, socket

# These are just some random useragents, you can replace these with a different list
user_agents = [
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20100101 Firefox/21.0",
	"Mozilla/5.0 (Windows NT 5.1; rv:21.0) Gecko/20100101 Firefox/21.0",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/536.30.1 (KHTML, like Gecko) Version/6.0.5 Safari/536.30.1",
	"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.63 Safari/537.36"
]

class NotFoundException(Exception):
	pass
	
class DownloadException(Exception):
	pass
	
# Very nasty monkeypatching ahead!
socket.real_create_connection = socket.create_connection

class ModifiedSession(requests.Session):
	def __init__(self, *args, **kwargs):
		try:
			self.bound_ip = kwargs['bound_ip']
			del kwargs['bound_ip']
		except KeyError, e:
			self.bound_ip = ""
			
		requests.Session.__init__(self, *args, **kwargs)
		self.headers['User-Agent'] = random.choice(user_agents)
		
	def patch_socket(self):
		socket.create_connection = get_patched_func(self.bound_ip)
	
	def unpatch_socket(self):
		socket.create_connection = socket.real_create_connection
	
	def get(self, *args, **kwargs):
		self.patch_socket()
		response = requests.Session.get(self, *args, **kwargs)
		self.unpatch_socket()
		return response
		
	def post(self, *args, **kwargs):
		self.patch_socket()
		response = requests.Session.post(self, *args, **kwargs)
		self.unpatch_socket()
		return response

def get_patched_func(bind_addr):
	def set_src_addr(*args):
		address, timeout = args[0], args[1]
		source_address = (bind_addr, 0)
		return socket.real_create_connection(address, timeout, source_address)
	return set_src_addr
	
# You're looking at duct tape and tie-wraps. It's like your local Home
# Depot, except in Python.
	
def download_file(request, target):
	if request.status_code == 200:
		f = open(target, "wb")
		
		for chunk in request.iter_content():
			f.write(chunk)
			
		f.close()
	else:
		raise DownloadException("Status code was %s" % request.status_code)
