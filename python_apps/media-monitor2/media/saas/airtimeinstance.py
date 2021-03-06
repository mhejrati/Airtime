import os
from os.path import join, basename, dirname

from media.monitor.exceptions import NoConfigFile
from media.monitor.pure import LazyProperty
from media.monitor.config import MMConfig
from media.monitor.owners import Owner
from media.monitor.events import EventRegistry
from media.monitor.listeners import FileMediator
from api_clients.api_client import AirtimeApiClient

# poor man's phantom types...
class SignalString(str): pass

class AirtimeInstance(object):
    """ AirtimeInstance is a class that abstracts away every airtime
    instance by providing all the necessary objects required to interact
    with the instance. ApiClient, configs, root_directory """

    @classmethod
    def root_make(cls, name, root):
        cfg = {
                'api_client' : join(root, 'etc/airtime/api_client.cfg'),
                'media_monitor' : join(root, 'etc/airtime/media-monitor.cfg'),
        }
        return cls(name, root, cfg)

    def __init__(self,name, root_path, config_paths):
        """ name is an internal name only """
        for cfg in ['api_client','media_monitor']:
            if cfg not in config_paths: raise NoConfigFile(config_paths)
            elif not os.path.exists(config_paths[cfg]):
                raise NoConfigFile(config_paths[cfg])
        self.name         = name
        self.config_paths = config_paths
        self.root_path    = root_path

    def signal(self, sig):
        if isinstance(sig, SignalString): return sig
        else: return SignalString("%s_%s" % (self.name, sig))

    def touch_file_path(self):
        """ Get the path of the touch file for every instance """
        touch_base_path = self.mm_config['index_path']
        touch_base_name = basename(touch_base_path)
        new_base_name   = self.name + touch_base_name
        return join(dirname(touch_base_path), new_base_name)


    def __str__(self):
        return "%s,%s(%s)" % (self.name, self.root_path, self.config_paths)

    @LazyProperty
    def api_client(self):
        return AirtimeApiClient(config_path=self.config_paths['api_client'])

    @LazyProperty
    def mm_config(self):
        return MMConfig(self.config_paths['media_monitor'])

    # NOTE to future code monkeys:
    # I'm well aware that I'm using the shitty service locator pattern
    # instead of normal constructor injection as I should be. The reason
    # for this is that I found these issues a little too close to the
    # end of my tenure. It's highly recommended to rewrite this crap
    # using proper constructor injection if you ever have the time

    @LazyProperty
    def owner(self): return Owner()

    @LazyProperty
    def event_registry(self): return EventRegistry()

    @LazyProperty
    def file_mediator(self): return FileMediator()

