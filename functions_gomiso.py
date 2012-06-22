import json
from BioTools import parse_timestamp
from gmnotifier import mydata
import gomiso
import dbstuff
from gm_config import *
import logging
logger = logging.getLogger("MisoNotifier")
class gmclass:
	def __init__(self):
		self.loginsuccess=False
		self.curuser=""
		self.curnews=""
		self.newuser=""
		self.newnews=""
		from gmnotifier import CreateLog
		#mydata=gmnotifier.mydata
		self.gm=gomiso.gomiso()
		#create the logger object..
		#and the gomiso object..
		#try to authentiate with miso..
		logger.info('trying to authenticate with miso to grab api handle')
		try:
			authentication=self.gm.authentification(consumer_key, consumer_secret, gm_username, gm_password, tokensFile)
		except:
			logger.info("authentication result:\n" + str(authentication))
		try:
			self.login = json.loads(self.gm.getUserInfo())
			#getting this far should meant that we were authorized, so we have populated our global login object with the json data
			#and log our success :)
			logger.info ('logged in as ' + self.login['user']['username'])
			self.loginsuccess=True
		except Exception as e:
			logger.error('looks like we had issues logging in - check consumer_key,secret, username, password in config')
			return 1
	def fetchgomisodata(self,feedcount):
		myid=self.login['user']['id']
		feed=json.loads(self.gm.userHomeFeed(myid,feedcount))
		#print feed[0]
		for line in feed:
			created_at=parse_timestamp(line['feed_item']['created_at'].encode("utf-8"))
			showname=line['feed_item']['topics']['media']['title'].encode("utf-8")
			username=line['feed_item']['user']['username'].encode("utf-8")
			#logger.info(line)
			if line['feed_item']['topics']['media']['kind']=='TvShow':
				if "badge" in str(line):
					ep_number="badge aquired: %s" % line['feed_item']['topics']['badge']['tagline']
				else:
					if "episode" in str(line):
						ep_number=line['feed_item']['topics']['episode']['label']
					else:
						ep_number=""
			else:
				ep_number=""
			#print created_at, username, showname, ep_number
			mydata.AddTempShowRecord(created_at,username,showname + " " + ep_number)
		self.newuser=username
		self.newnews=showname + " " + ep_number
		mydata.updateshows()
		self.fullnews=str(created_at) +": "+showname+" "+ep_number
		return self.newnews
	def ThereIsNews(self):
		if self.curnews!=self.newnews or self.curuser!=self.newuser:
			return True
		else:
			return False
	def UpdateNews(self):
		self.curnews=self.newnews
	def UpdateUser(self):
		self.curuser=self.newuser
