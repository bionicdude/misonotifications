import cherrypy
import dbstuff
import listlast
from gm_config import *
class Root(object):
  @cherrypy.expose
  def index(self):
    webdata=dbstuff.db()
    page=open("web/template.html","r").read()
    listitems=""
    sections=''
    personshows=""
    names=webdata.TopXUsers(gm_tabusercount).split('\n')
    names.insert(0,"Everyone")
    for row in names:
      listitems+='''
   <li><a href='#' onclick="onlyshow('BioDivClass','everything_%s');"><span>%s</span></a>
      <ul>
         <li><a href='#' onclick="onlyshow('BioDivClass','gomiso_%s');"><span>GoMiso</span></a></li>
         <li><a href='#' onclick="onlyshow('BioDivClass','lastfm_%s');"><span>LastFM</span></a></li>
      </ul>
'''	  % (row,row,row,row)
      sections += '<div class="BioDivClass" id="everything_%s" style="display:none;"><br>\n' % row
      for line in webdata.UserActivity(row,20).split('\n'):
        sections += line +"<br>\n"
      sections += listlast.friendtracks(row)
      sections += "<br></div>\n"
      sections += '<div class="BioDivClass" id="gomiso_%s" style="display:none;"><br>\n' % row
      for line in webdata.UserActivity(row,20).split('\n'):
        sections += line +"<br>\n"
      sections += "<br></div>\n"
      sections += '<div class="BioDivClass" id="lastfm_%s" style="display:none;"><br>\n' % row
      sections += listlast.friendtracks(row)
      sections += "<br></div>\n"
    content=page.replace("<<<listitems>>>",listitems)
    content=content.replace("<<<sections>>>",sections)
    return content


