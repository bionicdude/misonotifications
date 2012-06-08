import os
import datetime
import sqlite3
import logging
import logging.handlers
from gm_config import *

logger = logging.getLogger("MisoNotifier")

class db:
    def __init__(self):
        if not os.path.exists('data'):
            #create new DB, create table stocks
            self.con = sqlite3.connect('data')
            conn=self.con
            conn.execute('create table usernames (id integer primary key, NickName text, alias_gomiso text);')
            conn.execute('create table gomiso ( "When" integer, Who text, What text, notified integer);')
            conn.execute('create table tmp_gomiso("When" integer, Who text, What text);')
            conn.execute('create unique index usernames_gomiso on usernames(alias_gomiso);')
            conn.execute('create index gomiso_when on gomiso("when");')
            conn.execute('insert into usernames values (null,"bionicdude","bionicdude");')
            conn.execute('insert into gomiso values (1234567890123456789,"placeholder","initial record",0);')
            conn.commit()
        else:
            #use existing DB
            self.con = sqlite3.connect('data')
        self.cur = self.con.cursor()
        self.con.row_factory = sqlite3.Row

    def updateshows(self):
        logger.info("updating shows")
        conn=self.con
        conn.row_factory=sqlite3.Row
        curs=conn.cursor()
        curs.execute('select * from gomiso')
	#only insert new programs for users...don't worry if they've watched the same thing again (ignore the when bit)
        querystring='''
insert into gomiso
select a.*,0
from tmp_gomiso a
left outer join gomiso b
on a.who=b.who and a.what=b.what
where b.who is null;'''
        conn.execute(querystring)
        conn.commit()
        conn.execute('delete from tmp_gomiso;')
        conn.commit()
        querystring='select * from gomiso left outer join usernames on who=alias_gomiso where nickname!="%s" or nickname is null order by "when" desc limit %s' % (gm_me,str(gm_tooltipsize))
        #print querystring
        curs.execute(querystring)
        #print "What we have now\n"
        sofar=curs.fetchall()
        result = ''
        for row in sofar:
            result += "%s %s: %s\n" % (row["When"], row["Who"], row["What"])
        logger.debug(result)
        return result.strip()
    def newshows(self):
        result=''
        logger.info("getting new shows")
        conn=self.con
        conn.row_factory=sqlite3.Row
        curs=conn.cursor()
        curs.execute('select * from gomiso where notified=0 order by "when" asc')
        newshows=curs.fetchall()
        for row in newshows:
            result += "%s@%s@%s\n" % (row["When"], row["Who"], row["What"])
        logger.debug(result)
        logger.info('setting newshows as notified')
        conn.execute('update gomiso set notified=1 where notified=0;')
        return result.strip()
    def TopXUsers(self,usercount):
        logger.info("fetching top three users for webpage")
        conn=self.con
        conn.row_factory=sqlite3.Row
        curs=conn.cursor()
        curs.execute('select who,count(who) howmany from gomiso where upper(who)!="%s" group by who order by howmany desc limit %s' % (gm_me.upper(),str(usercount)))
        sofar=curs.fetchall()
        result = ''
        for row in sofar:
            result += "%s\n" % row["Who"]
        logger.debug(result)
        return result.strip()
    def UserActivity(self,user="",noa=20):
        if user.upper()!="EVERYONE":
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
                result += '<a style="font-family:Andale Mono;font-size:12px;">%s <stu>%s</stu> %s</a>\n' % (row["when"],row["Who"],row["what"])
            else:
                result += '<a style="font-family:Andale Mono;font-size:12px;">%s %s</a>\n' % (row["when"],row["what"])
        #print result
        return result.strip()
