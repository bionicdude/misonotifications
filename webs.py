import cherrypy
import dbstuff
import listlast
from gm_config import *
from gmnotifier import mydata as webdata
class Root(object):
  @cherrypy.expose
  def index(self):
    #webdata=dbstuff.db()
    page=open("web/template.html","r").read()
    listitems=""
    sections=''
    personshows=""
    names=webdata.TopXUsers(gm_tabusercount).split('\n')
    names.insert(0,"EVERYONE")
    for row in names:
      listitems+='''
   <li><a href='#' onclick="onlyshow('BioDivClass','everything_%s');"><span>%s</span></a>
      <ul>
         <li><a href='#' onclick="onlyshow('BioDivClass','gomiso_%s');"><span>GoMiso</span></a></li>
         <li><a href='#' onclick="onlyshow('BioDivClass','lastfm_%s');"><span>LastFM</span></a></li>
      </ul>
'''	  % (row,row,row,row)
      sections += '<div class="BioDivClass" id="everything_%s"><br>\n<ul class="BioList">' % row
      for line in webdata.UserActivity(row,20).split('\n'):
        sections += "<li>" +line +"</li>\n"
      for line in webdata.UserFMActivity(row,20).split('\n'):
        sections += "<li>" +line +"</li>\n"
      sections += "</ul><br></div>\n"
      sections += '<div class="BioDivClass" id="gomiso_%s">\n<ul class="BioList"><br>\n' % row
      for line in webdata.UserActivity(row,20).split('\n'):
        sections += "<li>" +line +"</li>\n"
      sections += "</ul><br></div>\n"
      sections += '<div class="BioDivClass" id="lastfm_%s">\n<ul class="BioList">\n' % row
      for line in webdata.UserFMActivity(row,20).split('\n'):
        sections += "<li>" +line +"</li>\n"
      sections += "</ul><br></div>\n"
    content=page.replace("<<<listitems>>>",listitems)
    content=content.replace("<<<sections>>>",sections)
    return content


