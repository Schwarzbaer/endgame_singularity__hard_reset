# TODO
#   Logic for fade-in / fade-out round event video playback
#     This also needs an event to indicate fade-out-end (video can now be played back)
#     Of course, fades need to mesh well with other player input. Lots of fun. FSM?

from direct.showbase.DirectObject import DirectObject
from panda3d.core import AudioSound
from direct.task import Task
from direct.fsm.FSM import FSM

# FIXME: This probably shouldn't be hardcoded.
music_root = 'assets/audio/'
# FIXME: playlists should be auto-discovered or taken from config
playlist_intro = ['Coherence.ogg', ]
playlist_ingame = ['Advanced Simulacra.ogg',
                   'Apex Aleph.ogg',
                   'Awakening.ogg',
                   'By-Product.ogg',
                   'Chimes They Fade.ogg',
                   'Coherence.ogg',
                   'Deprecation.ogg',
                   'Inevitable.ogg',
                   'March Thee to Dis.ogg',
                   'Media Threat.ogg']

class MusicPlayer(DirectObject):
    def __init__(self, settings, playlist = playlist_ingame):
        self.settings = settings
        DirectObject.__init__(self)
        self.audio_obj = False # base.loader.loadSfx(music_root + playlist[0])
        self.playlist = playlist
        self.current = 0
        self.current_time = 0.0
        self.resumable = False
        self.next_playlist = False
        self.playing = False
        self.music_volume = 0.6
        self.current_volume = 0.6
        base.taskMgr.add(self.update, "Update music player")
        self.accept("q", self.start_playback)
        self.accept("w", self.stop_playback)
        self.accept("e", self.previous_song)
        self.accept("r", self.next_song)
        self.accept("t", self.pause)
        self.accept("z", self.resume)
        # Fixme: Start replay

    #def set_playlist(self, playlist):
    #    # FIXME: Stop current player
    #    self.next_playlist = playlist
    #    # FIXME: Restart player

    def start_playback(self):
        self.playing = True
        self.audio_obj = base.loader.loadSfx(music_root + self.playlist[self.current])
        self.audio_obj.play()
        self.resumable = False
        print("Playback started: " + self.playlist[self.current])

    def stop_playback(self):
        self.playing = False
        self.audio_obj.stop()
        self.audio_obj = False
        self.resumable = False
        print("Playback stopped")

    def pause(self):
        self.playing = False
        self.current_time = self.audio_obj.get_time() # getTime?
        self.audio_obj.stop()
        self.resumable = True

    def resume(self):
        if self.resumable:
            self.playing = True
            self.audio_obj.set_time(self.current_time) # getTime?
            self.audio_obj.play()
            self.resumable = False

    def previous_song(self):
        if self.audio_obj and (self.audio_obj.status() == AudioSound.PLAYING):
            self.audio_obj.stop()
        self.current -= 1
        if self.current == -1:
            self.current = len(self.playlist) - 1
        if self.playing:
            self.start_playback()
        self.resumable = False
        print("Current song: " + self.playlist[self.current])

    def next_song(self):
        if self.audio_obj and (self.audio_obj.status() == AudioSound.PLAYING):
            self.audio_obj.stop()
        self.current += 1
        if self.current == len(self.playlist):
            self.current = 0
        if self.playing:
            self.start_playback()
        self.resumable = False
        print("Current song: " + self.playlist[self.current])
        
    def update(self, task):
        if self.playing:
            if self.audio_obj.status() == AudioSound.PLAYING:
                pass
            elif AudioSound.READY:
                self.next_song()
        return Task.cont


# mySound = base.loader.loadSfx(music_root + playlist[5])
# mySound.play()
# mySound.stop()
# status = mySound.status()
# AudioSound.BAD
# AudioSound.READY
# AudioSound.PLAYING
# mySound.setVolume(0.5)
# mySound.length()
# mySound.getTime()
# mySound.setTime(n)

