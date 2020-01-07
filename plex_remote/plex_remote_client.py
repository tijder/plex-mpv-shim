#!/usr/bin/env python3

import logging
import sys
import time
import os.path

from . import conffile
from .client import HttpServer
from .conf import settings
from .gdm import gdm
from .timeline import timelineManager

HTTP_PORT = 3000
APP_NAME = 'plex-remote'

log = logging.getLogger('')


class PlexRemoteClient:
    player = None
    server = None

    def __init__(self, player):
        self.player = player

    def start(self):
        conf_file = conffile.get(APP_NAME, 'conf.json')
        if os.path.isfile('settings.dat'):
            settings.migrate_config('settings.dat', conf_file)
        settings.load(conf_file)
        settings.add_listener(self.update_gdm_settings())

        self.update_gdm_settings()
        gdm.start_all()

        log.info("Started GDM service")

        self.server = HttpServer(int(settings.http_port))
        self.server.start()

        timelineManager.start()
        timelineManager.set_player(self.player)
        self.player.set_timeline_trigger(timelineManager.trigger)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("")
            log.info("Stopping services...")
        finally:
            self.stop()

    def stop(self):
        self.server.stop()
        timelineManager.stop()
        gdm.stop_all()

    def update_gdm_settings(self, name=None, value=None):
        gdm.clientDetails(settings.client_uuid, settings.player_name,
                          settings.http_port, "Plex MPV Shim", "1.0")
