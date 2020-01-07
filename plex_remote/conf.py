import logging
import os
import uuid
import pickle as pickle
import socket
import json
import os.path

log = logging.getLogger('conf')

class Settings(object):
    _listeners = []

    _path = None
    _data = {
        "player_name":          socket.gethostname(),
        "http_port":            "3000",
        "audio_output":         "hdmi",
        "audio_ac3passthrough": False,
        "audio_dtspassthrough": False,
        "client_uuid":          str(uuid.uuid4()),
        "enable_play_queue":    True,
        "allow_http":           False,
        "media_ended_cmd":      None,
        "pre_media_cmd":        None,
        "stop_cmd":             None,
        "auto_play":            True,
        "progress_save_delay":  90,
        "idle_cmd":             None,
        "idle_cmd_delay":       60,
        "always_transcode":     False,
        "remote_transcode":     True,
        "remote_kbps_thresh":   5000,
        "transcode_kbps":       2000,
        "transcode_res":        "720p",
    }

    def __getattr__(self, name):
        return self._data[name]

    def __setattr__(self, name, value):
        if name in self._data:
            self._data[name] = value
            self.save()

            for callback in self._listeners:
                try:
                    callback(name, value)
                except:
                    pass
        else:
            super(Settings, self).__setattr__(name, value)

    def __get_file(self, path, mode="r", create=True):
        created = False

        if not os.path.exists(path):
            try:
                fh = open(path, mode)
            except IOError as e:
                if e.errno == 2 and create:
                    fh = open(path, 'w')
                    json.dump(self._data, fh, indent=4, sort_keys=True)
                    fh.close()
                    created = True
                else:
                    raise e
            except Exception as e:
                log.error("Error opening settings from path: %s" % path)
                return None

        # This should work now
        return open(path, mode), created

    def migrate_config(self, old_path, new_path):
        fh, created = self.__get_file(old_path, "rb+", False)
        if not created:
            try:
                data = pickle.load(fh)
                self._data.update(data)
            except Exception as e:
                log.error("Error loading settings from pickle: %s" % e)
                fh.close()
                return False
        
        os.remove(old_path)
        self._path = new_path
        fh.close()
        self.save()
        return True


    def load(self, path, create=True):
        fh, created = self.__get_file(path, "r", create)
        self._path = path
        if not created:
            try:
                data = json.load(fh)
                self._data.update(data)
                log.info("Loaded settings from json: %s" % path)
                if len(data) < len(self._data):
                    self.save()
            except Exception as e:
                log.error("Error loading settings from json: %s" % e)
                fh.close()
                return False

        fh.close()
        return True

    def save(self):
        fh, created = self.__get_file(self._path, "w", True)

        try:
            json.dump(self._data, fh, indent=4, sort_keys=True)
            fh.flush()
            fh.close()
        except Exception as e:
            log.error("Error saving settings to json: %s" % e)
            return False

        return True

    def add_listener(self, callback):
        """
        Register a callback to be called anytime a setting value changes.
        An example callback function:

            def my_callback(key, value):
                # Do something with the new setting ``value``...

        """
        if callback not in self._listeners:
            self._listeners.append(callback)

settings = Settings()
