import re, oursql, requests, sys, json, shlex, argparse, os, random

from sources.nzbindex import NzbindexSpider
from sources.binsearch import BinsearchSpider
from shared import NotFoundException

parser = argparse.ArgumentParser(description="Automatically download NZBs for releases")
parser.add_argument("--config", dest="config", action="store", help="Use a configuration file to match against the database as source")
parser.add_argument("--list", dest="list", action="store", help="Use a newline-delimited list of releases as source")
parser.add_argument("--target", dest="target", action="store", help="Where to save the NZBs (only needed in list mode)")
parser.add_argument("--iplist", dest="iplist", action="store", help="Bind every request to a random IP from a newline-delimited list")
parser.add_argument("--limit", dest="limit", action="store", help="How many records to select in configuration file mode, at most (default: 250)", default=250)
args = parser.parse_args()

if args.config is not None:
	mode = "config"
elif args.list is not None:
	mode = "list"
else:
	sys.stderr.write("You must specify either a configuration file or a release list.\n")
	exit(1)
	
if args.iplist is not None:
	iplist_file = open(args.iplist, "r")
	iplist = iplist_file.read().splitlines()
else:
	iplist = [""]

if mode == "config":
	try:
		conf = json.load(open("config.json", "r"))
	except IOError, e:
		sys.stderr.write("You must have a valid config.json.\n")
		exit(1)
	
	if not re.match("^[a-zA-Z0-9_-]+$", conf['db']['table']):
		sys.stderr.write("Table name must be a-z, A-Z, 0-9, _, -\n")
		exit(1)
	
	try:
		searchconf_file = open(args.config, "r")
	except IOError, e:
		sys.stderr.write("The specified configuration file doesn't exist.\n")
		exit(1)
		
	queries = searchconf_file.read().splitlines()
	searchconf_file.close()
	
	db = oursql.connect(host=conf['db']['host'], user=conf['db']['user'], passwd=conf['db']['pass'], db=conf['db']['db'], autoreconnect=True)
	c = db.cursor()
	
	releases = []
	
	for query in queries:
		title, section, target = shlex.split(query)
		
		fields = []
		values = []
		
		if title != "-":
			fields.append("`release` LIKE ?")
			values.append("%" + title + "%")
			
		if section != "-":
			fields.append("`section` LIKE ?")
			values.append("%" + section + "%")
		
		values.append(args.limit)
		
		if len(fields) == 0:
			db_query = "SELECT `release` FROM %s WHERE `time` < (UNIX_TIMESTAMP(NOW()) - 86400) ORDER BY `time` DESC LIMIT ?" % conf['db']['table']
		else:
			db_query = "SELECT `release` FROM %s WHERE %s AND `time` < (UNIX_TIMESTAMP(NOW()) - 86400) ORDER BY `time` DESC LIMIT ?" % (conf['db']['table'], " AND ".join(fields))
		
		c.execute(db_query, values)
		
		for row in c:
			releases.append((row[0], target))
elif mode == "list":
	if args.target is None:
		sys.stderr.write("You did not specify a target directory with --target.\n")
		exit(1)
	
	try:
		list_file = open(args.list, "r")
	except IOError, e:
		sys.stderr.write("The specified list file doesn't exist.\n")
		exit(1)
	
	releases = [(release, args.target) for release in list_file.read().splitlines()]
	list_file.close()

sys.stdout.write("Found %d releases.\n" % len(releases))

downloaded = 0
skipped = 0
errors = 0
notfound = 0

notfound_list = []

for release in releases:
	release_name, target_dir = release
	target_path = os.path.join(target_dir, "%s.nzb" % release_name)
	
	if os.path.exists(target_path):
		# This NZB was already downloaded.
		skipped += 1
		continue
		
	if release_name in notfound_list:
		# This NZB couldn't be found before
		notfound += 1
		continue
	
	try:
		os.makedirs(target_dir)
	except OSError, e:
		# Target directory already exists
		pass
	
	try:
		spider = NzbindexSpider(random.choice(iplist))
		results = spider.find(release_name)
	except NotFoundException, e:
		try:
			spider = BinsearchSpider(random.choice(iplist))
			results = spider.find(release_name)
		except NotFoundException, e:
			sys.stderr.write("Could not find release %s\n" % release_name)
			notfound_list.append(release_name)
			notfound += 1
			continue
			
	# Process result
	result = results[0]
	
	try:
		result.download(target_path)
	except Exception, e:
		errors += 1
		sys.stderr.write("Downloading NZB for %s failed: %s\n" % (release_name, repr(e)))
		continue
		
	sys.stdout.write("Downloaded NZB for %s.\n" % release_name)
	downloaded += 1

sys.stdout.write("Finished. %d downloaded, %d skipped, %d errors and %d not found.\n" % (downloaded, skipped, errors, notfound))
