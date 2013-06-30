from shared import NotFoundException, ModifiedSession, download_file
import requests, re, HTMLParser

class BinsearchSpider(object):
	def __init__(self, bound_ip):
		self.bound_ip = bound_ip
		
	def find(self, name):
		parser = HTMLParser.HTMLParser()
		self.session = ModifiedSession(bound_ip=self.bound_ip)
		
		response = self.session.get("https://binsearch.info/index.php", params={
			"q": name,
			"m": "",
			"adv_age": "600",
			"max": "100",
			"adv_g": "",
			"adv_sort": "date",
			"minsize": "100",
			"maxsize": "",
			"adv_col": "on",
			"adv_nfo": "on",
			"font": "",
			"postdate": ""
		}, verify=False)
		
		search_results = []
		
		# Nice try, corrupting your HTML to deter scrapers. Not going to stop me, though.
		results = re.findall('<tr[^>]+>(.*?)<a href="browse\.php', response.text, re.DOTALL)
		
		for result in results:
			if 'requires password' in result:
				# Password protected
				continue
			
			match = re.search('<span[^>]*class="s"[^>]*>(.*?)<\/span>', result, re.DOTALL)
			
			if match is None:
				continue
				
			title = parser.unescape(re.sub("<[^>]+>", "", match.group(1)))
			
			if name.lower() in title.lower():
				match = re.search('<input[^>]*type="checkbox"[^>]*name="([0-9]+)"[^>]*>', result)
				
				if match is not None:
					search_results.append(BinsearchResult(name, title, match.group(1), self))
		
		if len(search_results) == 0:
			raise NotFoundException("No results were found.")
				
		return search_results
	
class BinsearchResult(object):
	def __init__(self, name, title, id_, spider):
		self.name = name
		self.title = title
		self.id_ = id_
		self.spider = spider
	
	def show(self):
		print "%s -> %s (%s)" % (self.title, self.id_, self.name)
	
	def download(self, target_path):
		data_dict = {"action": "nzb"}
		data_dict[self.id_] = "on"
		
		response = self.spider.session.post("https://www.binsearch.info/fcgi/nzb.fcgi", params={
			"q": self.name,
			"m": "",
			"adv_age": "600",
			"max": "100",
			"adv_g": "",
			"adv_sort": "date",
			"minsize": "100",
			"maxsize": "",
			"adv_col": "on",
			"adv_nfo": "on",
			"font": "",
			"postdate": ""
		}, data=data_dict)
		
		download_file(response, target_path)
