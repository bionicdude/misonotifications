#!/usr/bin/python
from pylast import *
import time

myapikey="306e79055126acf66ac4162d020da61d"
myapisecret="db810aebb02bc1ecb0aeff02c551c049"
username="bionicdude"
password="lastmatch"
#Set up the api key, secret, user and password here
network = LastFMNetwork(myapikey,myapisecret, username, password)
userData = User(username, network)
def friendtracks(friend):
    result=""
    try:
        frienddata=User(friend, network)
        topartists=frienddata.get_recent_tracks()
        result += "<br>initial lastfm fetching experiment<br>"
        for track in topartists:
            result+= time.ctime(int(track.timestamp)) +" " +str(track.track) + '<br>\n'
    except:
        pass
    return result