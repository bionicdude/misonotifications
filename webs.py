import cherrypy
import dbstuff
class Root(object):
  @cherrypy.expose
  def index(self):
    webdata=dbstuff.db()
    page=open("web/tab-tab.html","r").read()
    listitems=""
    sections='<section id="everyone"></section>\n'
    personshows=""
    names=webdata.TopThreeUsers().split('\n')
    for row in names:
      listitems+='<li><a href="#%s">%s</a></li>\n' % (row,row)
      sections += '<section id="%s">\n' % row
      for line in webdata.UserActivity(row,20).split('\n'):
        sections += line +"<br>\n"
      sections += "</section>\n"
    content=page.replace("<<<listitems>>>",listitems)
    content=content.replace("<<<sections>>>",sections)
    return content


