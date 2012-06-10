import cherrypy
import dbstuff
import listlast
from gm_config import *
class Root(object):
  @cherrypy.expose
  def index(self):
    webdata=dbstuff.db()
    page=open("web/tab-tab.html","r").read()
    listitems=""
    sections=''
    personshows=""
    names=webdata.TopXUsers(gm_tabusercount).split('\n')
    names.insert(0,"Everyone")
    for row in names:
      listitems+='<li><a href="#%s">%s</a></li>\n' % (row,row)
      sections += '<section id="%s">\n' % row
      for line in webdata.UserActivity(row,20).split('\n'):
        sections += line +"<br>\n"
      sections += listlast.friendtracks(row)
      sections += "</section>\n"
    content=page.replace("<<<listitems>>>",listitems)
    content=content.replace("<<<sections>>>",sections)
    return content


