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

def genNotify(gn_title="Notification",gn_msg="this is the message",gn_duration=5):
    #This will be the generic notification that will be called throughout
    #it will try to contact xbmc first...if it can't it will pass the message to pynotify.
    global os    
    gn_return=""
    msg=urllib.quote(gn_msg)
    #Hopefully that will have 'escaped' characters and encoded accordingly
    urltoget="GET \"http://%s:%s@%s/xbmcCmds/xbmcHttp?command=ExecBuiltIn(Notification(%s, %s,7500))\"" % (gm_xbmcusername,gm_xbmcpassword,gm_xbmcaddress,gn_title,msg)
    logger.debug("Sending xbmc msg via: %s" % urltoget)
    xbmcsuccess= str(os.system(urltoget))
    if "<li>OK" in xbmcsuccess:
        return gn_return
        exit
    try:
       #will doing this import over and over eat memory, or is it clever enough to not? mmm
       import gtk, pygtk, os, os.path, pynotify
       pygtk.require('2.0')
    except:
       gn_return = "Error: need python-notify, python-gtk2 and gtk"
    if not pynotify.init("Timekpr notification"):
        return "timekpr notification failed to initialize"
        sys.exit(1)
    n = pynotify.Notification(gn_title, gn_msg,"file://%s/icon.png" % mypath)
    #n = pynotify.Notification("Moo title", "test", "file:///path/to/icon.png")
    n.set_urgency(pynotify.URGENCY_CRITICAL)
    n.set_timeout(gn_duration*1000) # 5 seconds
    n.set_category("device")
    if not n.show():
        gn_return= "Failed"
    return gn_return
    
def CreateLog(logname='GenLog',loglevel=logging.DEBUG):
    logger=logging.getLogger('GenLog')
    logger.setLevel(loglevel)
    lh=logging.handlers.RotatingFileHandler("%s/%s.log" % (mypath,logname),maxBytes=256*1024,backupCount=9)
    lh.setLevel(loglevel)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    lh.setFormatter(formatter)
    logger.addHandler(lh)
    return logger

def Startup():
   #This is the "initialisation call"

   #logger is the global logging object..
   global logger
   #gm is our gomiso object (global here in case anyone else needed it, but maybe they won't)
   global gm
   #a login oject to hold our authenticated user info
   global login
   #mypath holds the location of the script so that relative references can be made
   global mypath
   mypath=sys.path[0]
   #create the logger object..
   logger=CreateLog("MisoNotifier")
   #and the gomiso object..
   gm=gomiso.gomiso()
   #try to authentiate with miso..
   logger.info('trying to authenticate with miso to grab api handle')
   loginsuccess = gm.authentification(consumer_key, consumer_secret, gm_username, gm_password, tokensFile)
   try:
      login = json.loads(gm.getUserInfo())
      #getting this far should meant that we were authorized, so we have populated our global login object with the json data
      #and log our success :)
      logger.info ('logged in as ' + login['user']['username'])
   except:
      logger.error('looks like we had issues logging in - check consumer_key,secret, username, password in config')
      return 1
      exit
   return 0

if Startup()>0:
    logger.info("seeing as the startup failed..we'll just exit now")
    sys.exit()
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
         logger.info(newnews)
         curnews = newnews#
         genNotify(gn_title='Miso Notification',gn_msg=newnews)
   except Exception, e:
      logger.error(" %s" %e)
   time.sleep(120)

