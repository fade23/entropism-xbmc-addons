# -*- coding: utf-8 -*-
# 

import os
import xbmc,xbmcaddon,xbmcgui
import threading
import urllib2
from utilities import *
  
__author__ = "Ross Glass"
__credits__ = ["Ross Glass"]
__license__ = "GPL"
__maintainer__ = "Ross Glass"
__email__ = "rglass@entropism.org"
__status__ = "Production"

__settings__ = xbmcaddon.Addon( "script.HATrigger" )
__language__ = __settings__.getLocalizedString

host = __settings__.getSetting( "host" )
port = __settings__.getSetting( "port" )
debug = __settings__.getSetting( "debug" )

movie_start = __settings__.getSetting( "movie_start" )
movie_pause = __settings__.getSetting( "movie_pause" )
movie_stop = __settings__.getSetting( "movie_stop" )

episode_start = __settings__.getSetting( "episode_start" )
episode_pause = __settings__.getSetting( "episode_pause" )
episode_stop = __settings__.getSetting( "episode_stop" )

music_start = __settings__.getSetting( "music_start" )
music_pause = __settings__.getSetting( "music_pause" )
music_stop = __settings__.getSetting( "music_stop" )

url_base = "http://" + host + ":" + port + "/"


headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

class Trigger(threading.Thread):
    totalTime = 0
    playedTime = 0
    startTime = 0
    curPlaying = None
    pinging = False
    playlistLength = 1
    abortRequested = False
    
    def run(self):
        # When requested ping trakt to say that the user is still watching the item
        count = 0
        while (not (self.abortRequested or xbmc.abortRequested)):
            time.sleep(5) # 1min wait
            if self.pinging:
                count += 1
                if count>=100:
                    Debug("[HATrigger] Pinging watching "+str(self.curPlaying))
                    tmp = time.time()
                    self.playedTime += tmp - self.startTime
                    self.startTime = tmp
                    self.startedPlaying()
                    count = 0
            else:
                count = 0
    
    def playbackStarted(self, data):
        self.curPlaying = data['item']
        if self.curPlaying <> None:
            if 'type' in self.curPlaying and 'id' in self.curPlaying:
                Debug("[HATrigger] Playing: "+self.curPlaying['type']+" - "+str(self.curPlaying['id']))
                self.startTime = time.time()
                self.startedPlaying()
                self.pinging = True
            else:
                self.curPlaying = None
                self.startTime = 0

    def playbackPaused(self):
        if self.startTime <> 0:
            self.playedTime += time.time() - self.startTime
            Debug("[HATrigger] Paused after: "+str(self.playedTime))
            self.startTime = 0
            self.pinging = False
            self.pausedPlaying()

    def playbackEnded(self):
        if self.startTime <> 0:
            if self.curPlaying == None:
                Debug("[HATrigger] Warning: Playback ended but video forgotten")
                return
            self.playedTime += time.time() - self.startTime
            self.pinging = False
            if self.playedTime <> 0:
                self.playedTime = 0
            self.startTime = 0
            self.stoppedPlaying()
            
    def startedPlaying(self):
            
        if self.curPlaying['type'] == 'movie':
            match = getMovieDetailsFromXbmc(self.curPlaying['id'], ['imdbnumber','title','year'])
            Debug("[HATrigger] Started a movie: " + str(match['title']))
            url = url_base + movie_start
            urllib2.urlopen(url)
            Debug("[HATrigger] Called URL: " + url)
            
        elif self.curPlaying['type'] == 'episode':
            match = getEpisodeDetailsFromXbmc(self.curPlaying['id'], ['showtitle', 'season', 'episode'])
            Debug("[HATrigger] Started an episode: " + str(match['showtitle']) + " S" + str(match['season']) + "E" + str(match['episode']))
            url = url_base + episode_start
            urllib2.urlopen(url)
            Debug("[HATrigger] Called URL: " + url)
            
        elif self.curPlaying['type'] == 'song':
            Debug("[HATrigger] Started a song")
            url = url_base + music_start
            urllib2.urlopen(url)
            Debug("[HATrigger] Called URL: " + url)
            
    def stoppedPlaying(self):
        
        if self.curPlaying['type'] == 'movie':
            Debug("[HATrigger] Stopped a movie")
            url = url_base + movie_stop
            urllib2.urlopen(url)
            Debug("[HATrigger] Called URL: " + url)
        elif self.curPlaying['type'] == 'episode':
            Debug("[HATrigger] Stopped an episode")
            url = url_base + episode_stop
            urllib2.urlopen(url)
            Debug("[HATrigger] Called URL: " + url)
        elif self.curPlaying['type'] == 'song':
            Debug("[HATrigger] Stopped a song")    
            url = url_base + music_stop
            urllib2.urlopen(url)
            Debug("[HATrigger] Called URL: " + url)
            
    def pausedPlaying(self):
        
        if self.curPlaying['type'] == 'movie':
            Debug("[HATrigger] Paused a movie")
            url = url_base + movie_pause
            urllib2.urlopen(url)
            Debug("[HATrigger] Called URL: " + url)
        elif self.curPlaying['type'] == 'episode':
            Debug("[HATrigger] Paused an episode")
            url = url_base + episode_pause
            urllib2.urlopen(url)
            Debug("[HATrigger] Called URL: " + url)
        elif self.curPlaying['type'] == 'song':
            Debug("[HATrigger] Paused a song") 
            url = url_base + music_pause
            urllib2.urlopen(url)
            Debug("[HATrigger] Called URL: " + url)