from abc import ABC, abstractmethod


class PlayerAbstract(ABC):
    timeline_trigger = None

    def set_timeline_trigger(self, timeline_trigger):
        self.timeline_trigger = timeline_trigger

    @abstractmethod
    def get_state(self):
        pass

    @abstractmethod
    def get_type(self):
        pass

    @abstractmethod
    def is_playing(self):
        pass

    @abstractmethod
    def has_media_item(self):
        pass

    @abstractmethod
    def get_play_time(self):
        pass

    @abstractmethod
    def get_ratingKey(self):
        pass

    @abstractmethod
    def get_key(self):
        pass

    @abstractmethod
    def get_guid(self):
        pass

    @abstractmethod
    def get_duration(self):
        pass

    @abstractmethod
    def get_hostname(self):
        pass

    @abstractmethod
    def get_scheme(self):
        pass

    @abstractmethod
    def get_port(self):
        pass

    @abstractmethod
    def get_machine_identifier(self):
        pass

    @abstractmethod
    def has_play_queue(self):
        pass

    @abstractmethod
    def get_playQueueID(self):
        pass

    @abstractmethod
    def get_playQueueVersion(self):
        pass

    @abstractmethod
    def get_playQueueItemID(self):
        pass

    def get_playQueueKey(self):
        pass

    @abstractmethod
    def has_next(self):
        pass

    @abstractmethod
    def has_prev(self):
        pass

    @abstractmethod
    def get_volume(self):
        pass

    @abstractmethod
    def handle_play(self, address, protocol, port, key, offset, playQueue, token):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def toggle_pause(self):
        pass

    @abstractmethod
    def play_next(self):
        pass

    @abstractmethod
    def play_prev(self):
        pass

    @abstractmethod
    def step_forward(self):
        pass

    @abstractmethod
    def step_back(self):
        pass

    @abstractmethod
    def seek(self, seek):
        pass

    @abstractmethod
    def skip_to(self, key):
        pass

    @abstractmethod
    def set_volume(self, percent):
        pass

    @abstractmethod
    def update_play_queue(self):
        pass

    @abstractmethod
    def get_product_name(self):
        pass
