#!/usr/bin/python
import logging
import logging.handlers
import sys
import string
import datetime
import time
import getopt
import gomiso
from gm_config import *
import json
import urllib
import os

def BioNotify(bn_title="Bionic Notification",bn_msg="this is the message",bn_duration=5000):
    bn_return=""
    try:
       import gtk, pygtk, os, os.path, pynotify
       pygtk.require('2.0')
    except:
       bn_return = "Error: need python-notify, python-gtk2 and gtk"
    if not pynotify.init("Timekpr notification"):
        return "timekpr notification failed to initialize"
        sys.exit(1)
    n = pynotify.Notification(bn_title, bn_msg,"file://%s/icon.png" % mypath)
    #n = pynotify.Notification("Moo title", "test", "file:///path/to/icon.png")
    n.set_urgency(pynotify.URGENCY_CRITICAL)
    n.set_timeout(bn_duration*1000) # 5 seconds
    n.set_category("device")

    #Call an icon
    #helper = gtk.Button()
    #icon = helper.render_icon(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_DIALOG)
    #n.set_icon_from_pixbuf(icon)

    if not n.show():
        bn_return= "Failed to send notification"
    return bn_return
    
def CreateLog(logname='BioLog',loglevel=logging.DEBUG):
    logger=logging.getLogger('BioLog')
    logger.setLevel(loglevel)
    lh=logging.handlers.RotatingFileHandler("%s/%s.log" % (mypath,logname),maxBytes=256*1024,backupCount=9)
    lh.setLevel(loglevel)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    lh.setFormatter(formatter)
    logger.addHandler(lh)
    return logger

def Startup():
   global logger
   global gm
   global login
   global mypath
   mypath=sys.path[0]
   print mypath
   logger=CreateLog("MisoNotifier")
   gm=gomiso.gomiso()
   if gm.authentification(consumer_key, consumer_secret, gm_username, gm_password, tokensFile):
      login = json.loads(gm.getUserInfo())
      logger.info ('logged in as ' + login['user']['username'])
    
def XBMCMsg(msg="weeee"):
    msg=urllib.quote(msg)
    #print msg
    urltoget="GET \"http://%s:%s@%s/xbmcCmds/xbmcHttp?command=ExecBuiltIn(Notification(BioNotify, %s,7500))\"" % (gm_xbmcusername,gm_xbmcpassword,gm_xbmcaddress,msg)
    logger.info("Sending xbmc msg via: %s" % urltoget)
    return os.system(urltoget)

Startup()
myid=login['user']['id']
curnews=""
while True:
   try:
      feed=json.loads(gm.userHomeFeed(myid,1))
      #print feed[0]
      for line in feed:
         created_at=line['feed_item']['created_at'].encode("utf-8")
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
      newnews=username+ ": "+showname+" "+ep_number
      if curnews!=newnews:
         aaa = XBMCMsg(newnews)
         #print "result was: %s" % aaa
         logger.info(newnews)
         curnews = newnews#
         if aaa!=0:
            BioNotify(bn_msg=newnews)
   except Exception, e:
      logger.error(" %s" %e)
   time.sleep(120)

