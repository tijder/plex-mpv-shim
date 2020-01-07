## About
With this library you can create a [remote Plex client](https://github.com/plexinc/plex-media-player/wiki/Remote-control-API). This library is based on [plex-mpv-shim](https://github.com/iwalton3/plex-mpv-shim). 

## How to use
- Implement the abstract class PlayerAbstract. As example you can look at this [file](https://gitlab.gnome.org/tijder/girens/blob/master/src/remote_player.py).  
- Import the program like this:
```python
from plex_remote.plex_remote_client import PlexRemoteClient
```
- Start the remote client like:
```python
self.plexRemoteClient = PlexRemoteClient(remote_player)
thread = threading.Thread(target=self.plexRemoteClient.start)
thread.daemon = True
thread.start()
```
- To stop the remote client:
```python
thread = threading.Thread(target=self.plexRemoteClient.stop)
thread.daemon = True
thread.start()
```

## Where it's used
This library is used in [Girens](https://gitlab.gnome.org/tijder/girens) an GTK Plex Media Player.