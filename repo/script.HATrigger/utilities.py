# -*- coding: utf-8 -*-
# 

import os, sys
import xbmc,xbmcaddon,xbmcgui
import time, socket

try: import simplejson as json
except ImportError: import json
import urllib, re

try:
    # Python 3.0 +
    import http.client as httplib
except ImportError:
    # Python 2.7 and earlier
    import httplib

try:
  # Python 2.6 +
  from hashlib import sha as sha
except ImportError:
  # Python 2.5 and earlier
  import sha
  
__author__ = "Ross Glass"
__credits__ = ["Ross Glass"]
__license__ = "GPL"
__maintainer__ = "Ross Glass"
__email__ = "fade@entropism.org"
__status__ = "Production"

__settings__ = xbmcaddon.Addon( "script.HATrigger" )
__language__ = __settings__.getLocalizedString

host = __settings__.getSetting("host")
port = sha.new(__settings__.getSetting("port")).hexdigest()
debug = __settings__.getSetting( "debug" )

headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

def Debug(msg, force=False):
    if (debug == 'true' or force):
        try:
            print "HA Trigger: " + msg
        except UnicodeEncodeError:
            print "HA Trigger: " + msg.encode( "utf-8", "ignore" )

def notification( header, message, time=5000, icon=__settings__.getAddonInfo( "icon" ) ):
    xbmc.executebuiltin( "XBMC.Notification(%s,%s,%i,%s)" % ( header, message, time, icon ) )

def checkSettings(daemon=False):
    if host == "":
        if daemon:
            notification("HA Trigger", __language__(1106).encode( "utf-8", "ignore" )) # please enter the host
        else:
            xbmcgui.Dialog().ok("HA Trigger", __language__(1106).encode( "utf-8", "ignore" )) # please enter the host
            __settings__.openSettings()
        return False
    elif __settings__.getSetting("host") == "":
        if daemon:
            notification("port", __language__(1107).encode( "utf-8", "ignore" )) # please enter the port
        else:
            xbmcgui.Dialog().ok("HA Trigger", __language__(1107).encode( "utf-8", "ignore" )) # please enter the port
            __settings__.openSettings()
        return False
           
    return True	
	
# SQL string quote escaper
def xcp(s):
    return re.sub('''(['])''', r"''", str(s))

# make a httpapi based XBMC db query (get data)
def xbmcHttpapiQuery(query):
    Debug("[httpapi-sql] query: "+query)
    
    xml_data = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % urllib.quote_plus(query), )
    match = re.findall( "<field>((?:[^<]|<(?!/))*)</field>", xml_data,)
    
    Debug("[httpapi-sql] responce: "+xml_data)
    Debug("[httpapi-sql] matches: "+str(match))
    
    return match

# execute a httpapi based XBMC db query (set data)
def xbmcHttpapiExec(query):
    xml_data = xbmc.executehttpapi( "ExecVideoDatabase(%s)" % urllib.quote_plus(query), )
    return xml_data
   
# get tvshows from XBMC
def getTVShowsFromXBMC():
    rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetTVShows','params':{'properties': ['title', 'year', 'imdbnumber', 'playcount']}, 'id': 1})
    
    result = xbmc.executeJSONRPC(rpccmd)
    result = json.loads(result)
    
    # check for error
    try:
        error = result['error']
        Debug("getTVShowsFromXBMC: " + str(error))
        return None
    except KeyError:
        pass # no error
    
    try:
        return result['result']
    except KeyError:
        Debug("getTVShowsFromXBMC: KeyError: result['result']")
        return None
    
# get seasons for a given tvshow from XBMC
def getSeasonsFromXBMC(tvshow):
    Debug("getSeasonsFromXBMC: "+str(tvshow))
    rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetSeasons','params':{'tvshowid': tvshow['tvshowid']}, 'id': 1})
    
    result = xbmc.executeJSONRPC(rpccmd)
    result = json.loads(result)
    
    # check for error
    try:
        error = result['error']
        Debug("getSeasonsFromXBMC: " + str(error))
        return None
    except KeyError:
        pass # no error

    try:
        return result['result']
    except KeyError:
        Debug("getSeasonsFromXBMC: KeyError: result['result']")
        return None
    
# get episodes for a given tvshow / season from XBMC
def getEpisodesFromXBMC(tvshow, season):
    rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetEpisodes','params':{'tvshowid': tvshow['tvshowid'], 'season': season, 'properties': ['playcount', 'episode']}, 'id': 1})
    
    result = xbmc.executeJSONRPC(rpccmd)
    result = json.loads(result)

    # check for error
    try:
        error = result['error']
        Debug("getEpisodesFromXBMC: " + str(error))
        return None
    except KeyError:
        pass # no error

    try:
        return result['result']
    except KeyError:
        Debug("getEpisodesFromXBMC: KeyError: result['result']")
        return None

# get a single episode from xbmc given the id
def getEpisodeDetailsFromXbmc(libraryId, fields):
    rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetEpisodeDetails','params':{'episodeid': libraryId, 'properties': fields}, 'id': 1})
    
    result = xbmc.executeJSONRPC(rpccmd)
    result = json.loads(result)

    # check for error
    try:
        error = result['error']
        Debug("getEpisodeDetailsFromXbmc: " + str(error))
        return None
    except KeyError:
        pass # no error

    try:
        return result['result']['episodedetails']
    except KeyError:
        Debug("getEpisodeDetailsFromXbmc: KeyError: result['result']['episodedetails']")
        return None

# get movies from XBMC
def getMoviesFromXBMC():
    rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetMovies','params':{'properties': ['title', 'year', 'originaltitle', 'imdbnumber', 'playcount', 'lastplayed']}, 'id': 1})

    result = xbmc.executeJSONRPC(rpccmd)
    result = json.loads(result)
    
    # check for error
    try:
        error = result['error']
        Debug("getMoviesFromXBMC: " + str(error))
        return None
    except KeyError:
        pass # no error
    
    try:
        return result['result']['movies']
        Debug("getMoviesFromXBMC: KeyError: result['result']['movies']")
    except KeyError:
        return None

# get a single movie from xbmc given the id
def getMovieDetailsFromXbmc(libraryId, fields):
    rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'VideoLibrary.GetMovieDetails','params':{'movieid': libraryId, 'properties': fields}, 'id': 1})
    
    result = xbmc.executeJSONRPC(rpccmd)
    result = json.loads(result)

    # check for error
    try:
        error = result['error']
        Debug("getMovieDetailsFromXbmc: " + str(error))
        return None
    except KeyError:
        pass # no error

    try:
        return result['result']['moviedetails']
    except KeyError:
        Debug("getMovieDetailsFromXbmc: KeyError: result['result']['moviedetails']")
        return None
   
# get current video being played from XBMC
def getCurrentPlayingVideoFromXBMC():
    rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'Player.GetActivePlayers','params':{}, 'id': 1})
    result = xbmc.executeJSONRPC(rpccmd)
    result = json.loads(result)
    # check for error
    try:
        error = result['error']
        Debug("[Util] getCurrentPlayingVideoFromXBMC: " + str(error))
        return None
    except KeyError:
        pass # no error
    
    try:
        for player in result['result']:
            if player['type'] == 'video':
                rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'Player.GetProperties','params':{'playerid': player['playerid'], 'properties':['playlistid', 'position']}, 'id': 1})
                result2 = xbmc.executeJSONRPC(rpccmd)
                result2 = json.loads(result2)
                # check for error
                try:
                    error = result2['error']
                    Debug("[Util] getCurrentPlayingVideoFromXBMC, Player.GetProperties: " + str(error))
                    return None
                except KeyError:
                    pass # no error
                playlistid = result2['result']['playlistid']
                position = result2['result']['position']
                
                rpccmd = json.dumps({'jsonrpc': '2.0', 'method': 'Playlist.GetItems','params':{'playlistid': playlistid}, 'id': 1})
                result2 = xbmc.executeJSONRPC(rpccmd)
                result2 = json.loads(result2)
                # check for error
                try:
                    error = result2['error']
                    Debug("[Util] getCurrentPlayingVideoFromXBMC, Playlist.GetItems: " + str(error))
                    return None
                except KeyError:
                    pass # no error
                Debug("Current playlist: "+str(result2['result']))
                
                return result2['result'][position]
        Debug("[Util] getCurrentPlayingVideoFromXBMC: No current video player")
        return None
    except KeyError:
        Debug("[Util] getCurrentPlayingVideoFromXBMC: KeyError")
        return None

def getMovieIdFromXBMC(imdb_id, title):
    # httpapi till jsonrpc supports searching for a single movie
    # Get id of movie by movies IMDB
    Debug("Searching for movie: "+imdb_id+", "+title)
    
    match = xbmcHttpapiQuery(
    " SELECT idMovie FROM movie"+
    "  WHERE c09='%(imdb_id)s'" % {'imdb_id':imdb_id}+
    " UNION"+
    " SELECT idMovie FROM movie"+
    "  WHERE upper(c00)='%(title)s'" % {'title':xcp(title.upper())}+
    " LIMIT 1")
    
    if not match:
        Debug("getMovieIdFromXBMC: cannot find movie in database")
        return -1
        
    return match[0]

def getShowIdFromXBMC(tvdb_id, title):
    # httpapi till jsonrpc supports searching for a single show
    # Get id of show by shows tvdb id
    
    Debug("Searching for show: "+str(tvdb_id)+", "+title)
    
    match = xbmcHttpapiQuery(
    " SELECT idShow FROM tvshow"+
    "  WHERE c12='%(tvdb_id)s'" % {'tvdb_id':xcp(tvdb_id)}+
    " UNION"+
    " SELECT idShow FROM tvshow"+
    "  WHERE upper(c00)='%(title)s'" % {'title':xcp(title.upper())}+
    " LIMIT 1")
    
    if not match:
        Debug("getShowIdFromXBMC: cannot find movie in database")
        return -1
        
    return match[0]
