import logging
import requests
import threading
import time
import os

try:
    from xml.etree import cElementTree as et
except:
    from xml.etree import ElementTree as et

from io import BytesIO

from .conf import settings
from .subscribers import remoteSubscriberManager
from .utils import Timer

log = logging.getLogger("timeline")

class TimelineManager(threading.Thread):
    def __init__(self):
        self.currentItems   = {}
        self.currentStates  = {}
        self.idleTimer      = Timer()
        self.subTimer       = Timer()
        self.serverTimer    = Timer()
        self.stopped        = False
        self.halt           = False
        self.trigger        = threading.Event()
        self.is_idle        = True
        self.player         = None

        threading.Thread.__init__(self)

    def set_player(self, player):
        self.player = player

    def stop(self):
        self.halt = True
        self.join()

    def run(self):
        force_next = False
        while not self.halt:
            if (self.player is not None and self.player.has_media_item()) or force_next:
                # playerManager.update()
                if self.player.is_playing() or force_next:
                    self.SendTimelineToSubscribers()
                self.delay_idle()
            force_next = False
            if self.idleTimer.elapsed() > settings.idle_cmd_delay and not self.is_idle and settings.idle_cmd:
                os.system(settings.idle_cmd)
                self.is_idle = True
            if self.trigger.wait(1):
                force_next = True
                self.trigger.clear()

    def delay_idle(self):
        self.idleTimer.restart()
        self.is_idle = False

    def SendTimelineToSubscribers(self):
        log.debug("TimelineManager::SendTimelineToSubscribers updating all subscribers")
        for sub in list(remoteSubscriberManager.subscribers.values()):
            self.SendTimelineToSubscriber(sub)


    def SendTimelineToSubscriber(self, subscriber):
        subscriber.set_poll_evt()
        if subscriber.url == "":
            return True

        timelineXML = self.GetCurrentTimeLinesXML(subscriber)
        url = "%s/:/timeline" % subscriber.url

        log.debug("TimelineManager::SendTimelineToSubscriber sending timeline to %s" % url)

        tree = et.ElementTree(timelineXML)
        tmp  = BytesIO()
        tree.write(tmp, encoding="utf-8", xml_declaration=True)

        tmp.seek(0)
        xmlData = tmp.read()

        # TODO: Abstract this into a utility function and add other X-Plex-XXX fields
        try:
            requests.post(url, data=xmlData, headers={
                "Content-Type":             "application/x-www-form-urlencoded",
                "Connection":               "keep-alive",
                "Content-Range":            "bytes 0-/-1",
                "X-Plex-Client-Identifier": settings.client_uuid
            }, timeout=5)
            return True
        except requests.exceptions.ConnectTimeout:
            log.warning("TimelineManager::SendTimelineToSubscriber timeout sending to %s" % url)
            return False
        except Exception:
            log.warning("TimelineManager::SendTimelineToSubscriber error sending to %s" % url)
            return False

    def WaitForTimeline(self, subscriber):
        subscriber.get_poll_evt().wait(30)
        return self.GetCurrentTimeLinesXML(subscriber)

    def GetCurrentTimeLinesXML(self, subscriber):
        tlines = self.GetCurrentTimeline()

        #
        # Only "video" is supported right now
        #
        mediaContainer = et.Element("MediaContainer")
        if subscriber.commandID is not None:
            mediaContainer.set("commandID", str(subscriber.commandID))
        mediaContainer.set("location", tlines["location"])

        lineEl = et.Element("Timeline")
        for key, value in list(tlines.items()):
            lineEl.set(key, str(value))
        mediaContainer.append(lineEl)

        return mediaContainer

    def GetCurrentTimeline(self):
        # https://github.com/plexinc/plex-home-theater-public/blob/pht-frodo/plex/Client/PlexTimelineManager.cpp#L142
        # Note: location is set to "" to avoid pop-up of navigation menu. This may be abuse of the API.
        options = {
            "location": "",
            "state":    self.player.get_state(),
            "type":     self.player.get_type()
        }
        controllable = []

        # The playback_time value can take on the value of none, probably
        # when playback is complete. This avoids the thread crashing.
        if self.player.has_media_item():

            options["location"]          = "fullScreenVideo"
            options["time"]              = int(self.player.get_play_time())
            options["autoPlay"]          = '1' if settings.auto_play else '0'

            aid, sid = self.player.get_track_ids()

            if aid:
                options["audioStreamID"] = aid
            if sid:
                options["subtitleStreamID"] = sid

            options["ratingKey"]         = self.player.get_ratingKey()
            options["key"]               = self.player.get_key()
            options["containerKey"]      = self.player.get_key()
            options["guid"]              = self.player.get_guid()
            options["duration"]          = self.player.get_duration()
            options["address"]           = self.player.get_hostname()
            options["protocol"]          = self.player.get_scheme()
            options["port"]              = self.player.get_port()
            options["machineIdentifier"] = self.player.get_machine_identifier()
            options["seekRange"]         = "0-%s" % options["duration"]

            if self.player.has_play_queue():
                options["playQueueID"] = int(self.player.get_playQueueID())
                options["playQueueVersion"] = int(self.player.get_playQueueVersion())
                options["playQueueItemID"] = int(self.player.get_playQueueItemID())
                options["containerKey"] = self.player.get_playQueueKey()

            controllable.append("playPause")
            controllable.append("stop")
            controllable.append("stepBack")
            controllable.append("stepForward")
            controllable.append("seekTo")
            controllable.append("skipTo")
            controllable.append("autoPlay")

            controllable.append("subtitleStream")
            controllable.append("audioStream")

            if self.player.has_next():
                controllable.append("skipNext")
            
            if self.player.has_prev():
                controllable.append("skipPrevious")

            # If the duration is unknown, disable seeking
            if options["duration"] == "0":
                options.pop("duration")
                options.pop("seekRange")
                controllable.remove("seekTo")

            controllable.append("volume")
            options["volume"] = str(self.player.get_volume())

            options["controllable"] = ",".join(controllable)
        else:
            options["time"] = 0

        return options


timelineManager = TimelineManager()
