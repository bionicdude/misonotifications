#!/usr/bin/python
from pylast import *
import datetime
import string
import dbstuff
import logging
import traceback
from gmnotifier import mydata

myapikey="306e79055126acf66ac4162d020da61d"
myapisecret="db810aebb02bc1ecb0aeff02c551c049"
username="bionicdude"
password="lastmatch"
#Set up the api key, secret, user and password here
network = LastFMNetwork(myapikey,myapisecret, username, password)
userData = User(username, network)
logger = logging.getLogger("MisoNotifier")
class LastFMClass:
	def __init__(self):
		self.loginsuccess=False
		self.curuser=""
		self.curnews=""
		self.newuser=""
		self.newnews=""
		from gmnotifier import CreateLog
		#mydata=gmnotifier.mydata
		#create the logger object..
	def friendtracks(self,friend,NeedUserName=False):
		result=""
		if NeedUserName==True:
			username="<stu>"+friend+"</stu> "
		else:
			username=""
		self.dbusername=username[5:-7]
		try:
			frienddata=User(friend, network)
			topartists=frienddata.get_recent_tracks(10)
			for track in topartists:
				timestring=string.replace(datetime.datetime.fromtimestamp(int(track.timestamp)).isoformat(),"T"," ")
				timestring=timestring[:19]
				try:
					album=""
					album=Track(track.track.artist,track.track.title,network).get_album().title
				except:
					pass
				try:
					mydata.AddTempFMRecord(timestring,self.dbusername,str(track.track),album)
				except:
					print "couldn't add temp record"
				result+= "<li>"+timestring+" " +username+"-" + album+"-"+str(track.track) + '</li>\n'
				self.newnews=album
			#mydata.UpdateFM()
		except:
			logger.error("didn't get friend data\n" + traceback.format_exc())
			pass
		return result
	def FetchLastFMData(self):
		result=""
		friendlist=self.getfriends()
		for friend in friendlist:
				result+=self.friendtracks(friend,True)
		return result
	def getfriends(self):
		result=list()
		for friend in User(username, network).get_friends():
			result.append(str(friend))
		return result
	def ThereIsNews(self):
		if self.curnews!=self.newnews or self.curuser!=self.newuser:
			return True
		else:
			return False
	def UpdateNews(self):
		self.curnews=self.newnews
	def UpdateUser(self):
		self.curuser=self.newuser