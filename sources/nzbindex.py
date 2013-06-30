from shared import NotFoundException, ModifiedSession, download_file
import requests, re, HTMLParser

class NzbindexSpider(object):
	def __init__(self, bound_ip):
		self.bound_ip = bound_ip
		
	def find(self, name):
		parser = HTMLParser.HTMLParser()
		self.session = ModifiedSession(bound_ip=self.bound_ip)
		self.session.post("https://nzbindex.com/agree/", data={"agree": "I agree"}, verify=False)
		
		response = self.session.get("https://nzbindex.com/search/", params={
			"q": name,
			"age": "",
			"max": "50",
			"minage": "",
			"sort": "agedesc",
			"minsize": "100",
			"maxsize": "",
			"dq": "",
			"poster": "",
			"nfo": "",
			"hasnfo": "1",
			"complete": "1",
			"hidespam": "1",
			"more": "1"
		}, verify=False)
		
		search_results = []
		
		results = re.findall("<tr[^>]*>(.*?)<\/tr>", response.text, re.DOTALL)
		
		for result in results:
			if 'class="threat"' in result:
				# Password protected or otherwise unsuitable for download
				continue
			
			match = re.search("<label[^>]*>(.*?)<\/label>", result, re.DOTALL)
			
			if match is None:
				continue
				
			title = parser.unescape(re.sub("<[^>]*>", "", match.group(1)))
			
			if name.lower() in title.lower():
				match = re.search('https?:\/\/nzbindex\.com\/download\/[^"]+\.nzb', result)
				
				if match is not None:
					search_results.append(NzbindexResult(title, match.group(0), self))
		
		if len(search_results) == 0:
			raise NotFoundException("No results were found.")
				
		return search_results
		
class NzbindexResult(object):
	def __init__(self, title, url, spider):
		self.title = title
		self.url = url
		self.spider = spider
		
	def show(self):
		print "%s -> %s" % (self.title, self.url)
		
	def download(self, target_path):
		download_file(self.spider.session.get(self.url), target_path)
