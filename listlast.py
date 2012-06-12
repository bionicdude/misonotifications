#!/usr/bin/python
from pylast import *
import datetime
import string

myapikey="306e79055126acf66ac4162d020da61d"
myapisecret="db810aebb02bc1ecb0aeff02c551c049"
username="bionicdude"
password="lastmatch"
#Set up the api key, secret, user and password here
network = LastFMNetwork(myapikey,myapisecret, username, password)
userData = User(username, network)
def friendtracks(friend,NeedUserName=False):
    result=""
    if NeedUserName==True:
        username="<stu>"+friend+"</stu> "
    else:
        username=""
    if friend.upper()=="EVERYONE":
        result+=geteveryone()
    try:
        frienddata=User(friend, network)
        topartists=frienddata.get_recent_tracks()
        for track in topartists:
            timestring=string.replace(datetime.datetime.fromtimestamp(int(track.timestamp)).isoformat(),"T"," ")
            timestring=timestring[:19]
            result+= "<li>"+timestring+" " +username+str(track.track) + '</li>\n'
    except:
        pass
    return result
def geteveryone():
	result=""
	friendlist=User(username, network).get_friends()
	for friend in friendlist:
		result+=friendtracks(str(friend),True)
	return result
