from direct.showbase import DirectObject

playlist = ['Advanced Simulacra.ogg', 'Apex Aleph.ogg', 'Awakening.ogg', 'By-Product.ogg', 'Chimes They Fade.ogg', 'Coherence.ogg', 'Deprecation.ogg', 'Inevitable.ogg', 'March Thee to Dis.ogg', 'Media Threat.ogg']

class MusicPlayer(DirectObject):
    pass

mySound = base.loader.loadSfx("audio/Coherence.ogg")
mySound.play()
mySound.stop()
status = mySound.status()
AudioSound.BAD
AudioSound.READY
AudioSound.PLAYING
mySound.setVolume(0.5)
mySound.length()
