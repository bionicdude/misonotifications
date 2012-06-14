import os
import sqlite3
import logging
import logging.handlers
from gm_config import *

logger = logging.getLogger("MisoNotifier")

class db:
	def __init__(self):
		if not os.path.exists('data'):
			#create new DB, create table stocks
			self.con = sqlite3.connect('data' ,check_same_thread = False)
			conn=self.con
			curs=conn.cursor()
			curs.execute('create table usernames (id integer primary key, NickName text, alias_gomiso text, alias_lastfm text);')
			curs.execute('create table gomiso ( "When" integer, Who text, What text, notified integer);')
			curs.execute('create table tmp_gomiso("When" integer, Who text, What text);')
			curs.execute('create unique index usernames_gomiso on usernames(alias_gomiso);')
			curs.execute('create index gomiso_when on gomiso("when");')
			#curs.execute('insert into usernames values (null,"bionicdude","bionicdude","bionicdude");')
			#curs.execute('insert into gomiso values (1234567890123456789,"placeholder","initial record",0);')
			curs.execute('create table lastfm ( "When" integer, Who text, What text,Which text, notified integer);')
			curs.execute('create table tmp_lastfm("When" integer, Who text, What text,Which text);')
			curs.execute('create unique index usernames_lastfm on usernames(alias_lastfm);')
			curs.execute('create index lastfm_when on lastfm("when");')
			conn.commit()
		else:
			#use existing DB
			self.con = sqlite3.connect('data' ,check_same_thread = False)
		self.con.row_factory = sqlite3.Row

	def updateshows(self):
		logger.info("import tmp data and return top x records")
		conn=self.con
		conn.row_factory=sqlite3.Row
		curs=conn.cursor()
		#curs.execute('select * from gomiso')
		#only insert new programs for users...don't worry if they've watched the same thing again (ignore the when bit)
		querystring='''
		insert into gomiso
		select a.*,0
		from tmp_gomiso a
		left outer join gomiso b
		on a.who=b.who and a.what=b.what
		where b.who is null;'''
		curs.execute(querystring)
		conn.commit()
		curs.execute('delete from tmp_gomiso;')
		conn.commit()
		querystring='select * from gomiso left outer join usernames on upper(who)=upper(alias_gomiso) where upper(nickname)!="%s" or nickname is null order by "when" desc limit %s' % (gm_me.upper(),str(gm_tooltipsize))
		#print querystring
		curs.execute(querystring)
		#print "What we have now\n"
		sofar=curs.fetchall()
		result = ''
		for row in sofar:
			result += "%s %s: %s\n" % (row["When"], row["Who"], row["What"])
		logger.info("\nrecords returned\n" + str(result))
		conn.commit()
		curs.close()
		return result.strip()

	def newshows(self,SetAsNotified=True):
		result=''
		logger.info("getting new shows")
		conn=self.con
		conn.row_factory=sqlite3.Row
		curs=conn.cursor()
		curs.execute('select * from gomiso where notified=0 order by "when" asc')
		newshows=curs.fetchall()
		for row in newshows:
			result += "%s@%s@%s\n" % (row["When"], row["Who"], row["What"])
		logger.info("\nShows not notified yet:\n" + str(result))
		if SetAsNotified:
			logger.info('set newshows as notified')
			curs.execute('update gomiso set notified=1 where notified=0;')
		logger.debug("\nHere's what new shows we're returning\n" + result.strip())
		conn.commit()
		curs.close()
		return result.strip()

	def TopXUsers(self,usercount):
		logger.info("fetching top three users for webpage")
		conn=self.con
		conn.row_factory=sqlite3.Row
		curs=conn.cursor()
		curs.execute('''
		select distinct who from (
		select * from(
		select trim(upper(who)) who,count(who) howmany
		from gomiso where upper(who)!="%s"
		group by who order by howmany desc limit %s) dataone
		union
		select * from (
		select trim(upper(who)) who,count(who) howmany
		from lastfm where upper(who)!="%s"
		group by who order by howmany desc limit %s) datatwo) datathree
		limit %s
		''' % (gm_me.upper(),str(usercount),gm_me.upper(),str(usercount),str(usercount)))
		sofar=curs.fetchall()
		result = ''
		for row in sofar:
			result += "%s\n" % row["Who"]
		logger.debug(result)
		conn.commit()
		curs.close
		return result.strip()

	def UserActivity(self,user="",noa=20):
		if user.upper()!="EVERYONE":
			noa=40
			user='where upper(who)="%s"' % user
		else:
			user=""
		conn=self.con
		conn.row_factory=sqlite3.Row
		curs=conn.cursor()
		curs.execute('select "when", Who, What from gomiso %s order by "when" desc limit %s' % (user.upper(),str(noa)))
		thelist=curs.fetchall()
		result=''
		for row in thelist:
			if user=="":
				result += '%s <appid>GOMISO</appid> <dbname>%s</dbname> %s\n' % (row["when"],row["Who"],row["what"])
			else:
				result += '%s <appid>GOMISO</appid> %s\n' % (row["when"],row["what"])
		#print result
		conn.commit()
		curs.close
		if result.strip()=="":
			result="No Shows in gomiso history"
		return result.strip()

	def AddTempShowRecord(self,when="",who="", what=""):
		conn=self.con
		conn.row_factory=sqlite3.Row
		curs=conn.cursor()
		curs.execute('insert into tmp_gomiso values(?,?,?);', (when, who, what))
		conn.commit()
		curs.close

	def AddTempFMRecord(self,when="",who="", what="",which=""):
		conn=self.con
		conn.row_factory=sqlite3.Row
		curs=conn.cursor()
		curs.execute('insert into tmp_lastfm values(?,?,?,?);', (when, who, what,which))
		conn.commit()
		curs.close
	def UpdateFM(self):
		logger.info("Importing tmp LastFM data into database")
		conn=self.con
		conn.row_factory=sqlite3.Row
		curs=conn.cursor()
		#curs.execute('select * from gomiso')
		querystring='''
		insert into lastfm
		select a.*,0
		from tmp_lastfm a
		left outer join lastfm b
		on a.who=b.who and a.what=b.what and a."when"=b."when"
		where b.who is null;'''
		curs.execute(querystring)
		conn.commit()
		curs.execute('delete from tmp_lastfm;')
		conn.commit()
		querystring='select * from lastfm left outer join usernames on upper(who)=upper(alias_lastfm) where upper(nickname)!="%s" or nickname is null order by "when" desc limit %s' % (gm_me.upper(),str(gm_tooltipsize))
		#print querystring
		curs.execute(querystring)
		#print "What we have now\n"
		sofar=curs.fetchall()
		result = ''
		for row in sofar:
			result += "%s %s: %s\n" % (row["When"], row["Who"], row["What"])
		logger.info("\nreturned results:\n" + str(result))
		conn.commit()
		curs.close
		return result.strip()
	def UserFMActivity(self,user="",noa=20):
		if user.upper()!="EVERYONE":
			user='where upper(who)="%s"' % user
		else:
			user=""
			noa=80
		conn=self.con
		conn.row_factory=sqlite3.Row
		curs=conn.cursor()
		curs.execute('select "when", Who, What from lastfm %s order by "when" desc limit %s' % (user.upper(),str(noa)))
		thelist=curs.fetchall()
		result=''
		for row in thelist:
			if user=="":
				result += '%s <appid>LASTFM</appid> <dbname>%s</dbname> %s\n' % (row["when"],row["Who"],row["what"])
			else:
				result += '%s <appid>LASTFM</appid> %s\n' % (row["when"],row["what"])
		#print result
		conn.commit()
		curs.close
		return result.strip()
	def newFM(self,SetAsNotified=True):
		result=''
		logger.info("getting non-notified tracks from database..")
		conn=self.con
		conn.row_factory=sqlite3.Row
		curs=conn.cursor()
		curs.execute('select distinct who,which from lastfm where notified=0 order by "when" asc')
		newtracks=curs.fetchall()
		for row in newtracks:
			result += "%s@%s\n" % (row["Who"],row["which"])
		logger.info("\nTracks not notified yet:\n" + str(result))
		if SetAsNotified:
			logger.info('set new tracks as notified')
			curs.execute('update lastfm set notified=1 where notified=0;')
		conn.commit()
		curs.close
		return result.strip()