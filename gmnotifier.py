#!/usr/bin/python
try:
 notkinter=False
 from easygui import *
except:
 print "you need to install tkinter to show popup"
 notkinter=True
import thread
import traceback
import cherrypy
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
import pygtk
pygtk.require('2.0')
import gtk
gtk.gdk.threads_init()
import gobject
import dbstuff
mydata=dbstuff.db()
import webs
import listlast
#import misoform
from BioTools import parse_timestamp
import functions_gomiso

current_dir= os.path.dirname(os.path.abspath(__file__))

class SystrayIconApp:
	def __init__(self):
		global mgm
		global gomiso_curnews
		global doing
		global tkinter
		self.menu = gtk.Menu()
		if gm_UseUnity == False:
			print "not using unity"
			self.tray = gtk.status_icon_new_from_file("icon.png")
			self.tray.set_title("AcitvityNotifier")
			self.tray.connect('popup-menu', self.on_right_click)
		else:
			print "using unity"
			import appindicator
			self.tray = appindicator.Indicator("ActivityNotifier", "gtk-execute", appindicator.CATEGORY_APPLICATION_STATUS)
			self.tray.set_status (appindicator.STATUS_ACTIVE)
			self.tray.set_attention_icon ("indicator-messages-new")
			self.tray.set_icon(os.getcwd() + "/icon.png")
			self.tray.set_menu(self.menu)
		if Startup()>0:
			logger.info("seeing as the startup failed..we'll just exit now")
			print "Error(see log)..Exiting"
			sys.exit()
		gomiso_curnews=""
		genNotify(gn_title='Activity Notifier',gn_msg='Starting Application')
		logger.info("Starting the main thread")
		mainprogloop() #without this line nothing updates for 5 mins
		something=gobject.timeout_add(3000000,mainprogloop)
		# show about dialog
		about = gtk.MenuItem("About")
		self.menu.append(about)
		about.show()
		about.connect('activate', self.show_about_dialog)

		#miso window
		if notkinter:
			miso = gtk.MenuItem("install python-tk to use popup list")
		else:
			miso = gtk.MenuItem("newsfeed")
		self.menu.append(miso)
		miso.show()
		miso.connect('activate', self.show_miso_list)

		# add quit item
		quit = gtk.MenuItem("Quit")
		quit.show()
		self.menu.append(quit)
		quit.connect('activate', gtk.main_quit)

	def on_right_click(self, icon, event_button, event_time):
		self.menu.popup(None, None, gtk.status_icon_position_menu,
		event_button, event_time, self.tray)

	def  show_about_dialog(self, widget):
		about_dialog = gtk.AboutDialog()
		about_dialog.set_destroy_with_parent (True)
		about_dialog.set_icon_name ("Activity Notifier")
		about_dialog.set_name('Activity Notifier')
		about_dialog.set_version('0.1')
		about_dialog.set_copyright("2012 BionicDude")
		about_dialog.set_comments(("keep up to date on what your friends are doing...without the need for a webcam"))
		about_dialog.set_authors(['bionicdude'])
		about_dialog.run()
		about_dialog.destroy()
	def set_tooltip(self,msg):
		try:
			self.tray.set_tooltip((msg))
		except Exception, e:
			#probably don't have tooltip property as we're using the unity stuff..
			#we won't even bother writing debug..
			pass
	def show_miso_list(self, widget):
		try:
			msgbox(shows)
		except:
			pass

def genNotify(gn_title="Notification",gn_msg="this is the message",gn_duration=5):
	#This will be the generic notification that will be called throughout
	#it will try to contact xbmc first...if it can't it will pass the message to pynotify.
	global os
	global logger
	gn_return=""
	msg=urllib.quote(gn_msg)
	#Hopefully that will have 'escaped' characters and encoded accordingly
	urltoget="GET \"http://%s:%s@%s/xbmcCmds/xbmcHttp?command=ExecBuiltIn(Notification(%s, %s,7500))\"" % (gm_xbmcusername,gm_xbmcpassword,gm_xbmcaddress,gn_title,msg)
	#logger.debug("Sending xbmc msg via: %s" % urltoget)
	try:
		xbmcsuccess= str(os.system(urltoget))
	except:
		logger.info("xbmc probably not running (although that in itself shouldn't give me an error..)")
	#logger.debug(xbmcsuccess)
	if ("<li>OK" in xbmcsuccess) or str(xbmcsuccess)=="0":
		return gn_return
		exit
	try:
		#logger.debug("importing py stuff")
		#will doing this import over and over eat memory, or is it clever enough to not? mmm
		import gtk, pygtk, os, os.path, pynotify
		pygtk.require('2.0')
	except:
		gn_return = "Error: need python-notify, python-gtk2 and gtk"
	if not pynotify.init("Timekpr notification"):
		return "timekpr notification failed to initialize"
		sys.exit(1)
	n = pynotify.Notification(gn_title, gn_msg,"file://%s/icon.png" % sys.path[0])
	#n = pynotify.Notification("Moo title", "test", "file:///path/to/icon.png")
	n.set_urgency(pynotify.URGENCY_LOW)
	n.set_timeout(gn_duration*1000) # 5 seconds
	n.set_category("device")
	if not n.show():
		gn_return= "Failed"
	return gn_return

def CreateLog(logname='GenLog',loglevel=logging.DEBUG):
	logger=logging.getLogger(logname)
	logger.setLevel(loglevel)
	lh=logging.handlers.RotatingFileHandler("%s/%s.log" % (sys.path[0],logname),maxBytes=256*1024,backupCount=9)
	lh.setLevel(loglevel)
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	lh.setFormatter(formatter)
	logger.addHandler(lh)
	return logger

def Startup():
	#This is the "initialisation call"

	#logger is the global logging object..
	global logger
	#mgm is our gomiso object (global here in case anyone else needed it, but maybe they won't)
	global mgm
	#mlf is our lastfm object
	global mlf
	#mypath holds the location of the script so that relative references can be made
	#create the logger object..
	logger=CreateLog("MisoNotifier")
	mgm=functions_gomiso.gmclass()
	mlf=listlast.LastFMClass()
	if not mgm.loginsuccess:
		sys.exit
	return 0

def mainprogloop():
	global gomiso_curnews
	global curuser
	global myid
	global mgm
	global mlf
	global logger
	global oh
	global initialrun
	global shows
	if True:
		print "loop"
		try:
			if initialrun:
				feedcount=30#change to 30 when not debugging
			else:
				feedcount=10
			mgm.fetchgomisodata(feedcount)
			mlf.FetchLastFMData()
			if gm_repeatnotify==False:
				mgm.curuser=mgm.newuser
			#print "new news for tv?=",mgm.ThereIsNews()
			#print "current gotmiso news(%s) and newnews(%s)" % (mgm.curnews, mgm.newnews)
			#print "new news for lastfm?=",mlf.ThereIsNews()
			#print "current lastfm news(%s) and newnews(%s)" % (mlf.curnews, mlf.newnews)
			if mgm.ThereIsNews():
				newshows=mydata.newshows()
				if len(newshows)>0:
					newshows=newshows.split('\n')
					for show in newshows:
						items=show.split('@')
						if not items[1]==gm_me:
							logger.info(items[0] +' '+ items[1] +' '+items[2])
							genNotify(gn_title=items[1],gn_msg=items[2])
					shows=mydata.updateshows()
				mgm.UpdateNews()
				mgm.UpdateUser()
			if mlf.ThereIsNews():
				tracks=mydata.UpdateFM()#maybe need this first...
				newtracks=mydata.newFM()
				if len(newtracks)>0:
					newtracks=newtracks.split('\n')
					for track in newtracks:
						items=track.split('@')
						if not items[1]==gm_me:
							logger.info("notifying: "+items[0] +' '+ items[1])
							genNotify(gn_title=items[0],gn_msg=items[1])
					tracks=mydata.UpdateFM()
				mlf.UpdateNews()
				mlf.UpdateUser()
				#last thing
			try:
				oh.set_tooltip((mydata.GetTooltip()))
			except:
				#this won't work the very first time round as the object isn't fully initialized yet
				#will revisit later to see if i can rejig stuff to compensate..
				pass
		except:
			logger.error(traceback.format_exc())
	return True

initialrun=True
if __name__ == "__main__":
	oh=SystrayIconApp()
	oh.set_tooltip((mydata.GetTooltip()))
	cherrypy.server.socket_host = gm_bindip
	cherrypy.server.socket_port = gm_bindport
	cherrypy.tree.mount(webs.Root(),config={
'/':
{'tools.staticdir.on':True,
'tools.staticdir.dir':current_dir
}
})
	thread.start_new_thread(cherrypy.engine.start,())
	gtk.main()
