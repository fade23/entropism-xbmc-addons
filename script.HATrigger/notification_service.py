# -*- coding: utf-8 -*-
# 

import xbmc,xbmcaddon,xbmcgui
import telnetlib, time

try: import simplejson as json
except ImportError: import json

import threading
from trigger import Trigger
from utilities import *

__author__ = "Ross Glass"
__credits__ = ["Ross Glass"]
__license__ = "GPL"
__maintainer__ = "Ross Glass"
__email__ = "rglass@entropism.org"
__status__ = "Production"

__settings__ = xbmcaddon.Addon( "script.HATrigger" )
__language__ = __settings__.getLocalizedString

# Receives XBMC notifications and passes them off to the trigger functions
class NotificationService(threading.Thread):
    abortRequested = False
    def run(self):        
        #while xbmc is running
        trigger = Trigger()
        
        while (not (self.abortRequested or xbmc.abortRequested)):
            try:
                tn = telnetlib.Telnet('localhost', 9090, 10)
            except IOError as (errno, strerror):
                #connection failed, try again soon
                Debug("[Notification Service] Telnet too soon? ("+str(errno)+") "+strerror)
                time.sleep(1)
                continue
            
            Debug("[Notification Service] Waiting~");
            bCount = 0
            
            while (not (self.abortRequested or xbmc.abortRequested)):
                try:
                    if bCount == 0:
                        notification = ""
                        inString = False
                    [index, match, raw] = tn.expect(["(\\\\)|(\\\")|[{\"}]"], 0.2) #note, pre-compiled regex might be faster here
                    notification += raw
                    if index == -1: # Timeout
                        continue
                    if index == 0: # Found escaped quote
                        match = match.group(0)
                        if match == "\"":
                            inString = not inString
                            continue
                        if match == "{":
                            bCount += 1
                        if match == "}":
                            bCount -= 1
                    if bCount > 0:
                        continue
                    if bCount < 0:
                        bCount = 0
                except EOFError:
                    break #go out to the other loop to restart the connection
                
                Debug("[Notification Service] message: " + str(notification))
                
                # Parse recieved notification
                data = json.loads(notification)
                
                # Forward notification to functions
                if 'method' in data and 'params' in data and 'sender' in data['params'] and data['params']['sender'] == 'xbmc':
                    if data['method'] == 'Player.OnStop':
                        Debug("[HATrigger] Stopped Playback")
                        trigger.playbackEnded()
                    elif data['method'] == 'Player.OnPlay':
                        if 'data' in data['params'] and 'item' in data['params']['data'] and 'id' in data['params']['data']['item'] and 'type' in data['params']['data']['item']:
                            Debug("[HATrigger] Started Playback")
                            trigger.playbackStarted(data['params']['data'])
                    elif data['method'] == 'Player.OnPause':
                        Debug("[HATrigger] Paused Playback")
                        trigger.playbackPaused()
                    elif data['method'] == 'System.OnQuit':
                        self.abortRequested = True
                
            time.sleep(1)
        tn.close()
        trigger.abortRequested = True
            