# -*- coding: utf-8 -*-
# 

import xbmc,xbmcaddon,xbmcgui
from notification_service import *
from utilities import *

__author__ = "Ross Glass"
__credits__ = ["Ross Glass"]
__license__ = "GPL"
__maintainer__ = "Ross Glass"
__email__ = "rglass@entropism.org"
__status__ = "Production"

__settings__ = xbmcaddon.Addon( "script.HATrigger" )
__language__ = __settings__.getLocalizedString

Debug("service: " + __settings__.getAddonInfo("id") + " - version: " + __settings__.getAddonInfo("version"))

# starts update/sync
def autostart():
    if checkSettings(True):
        notificationThread = NotificationService()
        notificationThread.start()                 
        notificationThread.join()

autostart()
