#!/usr/bin/env python2

# TODO (big)
#   Settings management
#   Event Timeline / Time Managements
#   Tech Tree visualization
# TODO (small)
#   Change the base notation of coordinates from pixel/pixel to uv
#     Change the whole bases.py to a YAML file
#   Mouse to rotate geosphere
#   Oh my god, so much cleanup...
# TODO (later)
#   Finish Music Player





import sys
import yaml
import datetime
import networkx as nx
import pprint

from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from panda3d.core import NodePath

from geosphere import Geosphere
from bases import base_id, coords, name, active
from music import MusicPlayer
from mechanics import GameState

# Load base definitions
f = open('bases.yml', 'r')
bases = yaml.load(f.read())
f.close()

default_settings = {'music': {'volume': 0.6,
                              'fade_time': 0.5,
                              'playlists': {'intro': ['Awakening.ogg'],
                                            'ingame': ['Advanced Simulacra.ogg',
                                                       'Apex Aleph.ogg',
                                                       'Coherence.ogg',
                                                       'By-Product.ogg',
                                                       'Chimes They Fade.ogg',
                                                       'Deprecation.ogg',
                                                       'Inevitable.ogg',
                                                       'March Thee to Dis.ogg',
                                                       'Media Threat.ogg'],
                                           },
                             },
                   }

class Settings(DirectObject):
    def __init__(self, settings_file = 'settings.yml'):
        DirectObject.__init__(self)
        self.settings_file = settings_file
        self.load_settings()
        
    def save_settings(self):
        # FIXME: Implement
        f = open(self.settings_file, 'w')
        f.write(yaml.dump(self.settings_file))
        f.close()
        
    def load_settings(self):
        self.settings = default_settings
        # FIXME: This is actually completely untested.
        #try:
        #    f = open(self.settings_file, 'r')
        #    self.settings = yaml.dump(f.read())
        #    f.close()
        #except: # FIXME: What's the actual exception when the file can't be opened?
        #    self.create_settings()
            
    def create_settings(self):
        self.settings = default_settings
        self.save_settings()
        
    def get_setting_variable(self, name):
        treeway = name.split('.')
        variables = self.settings
        for tw in treeway:
            variables = variables[tw]
        return variables
        
    def register_value(self, obj, value):
        # FIXME: Implement
        pass
        
    def unregister_value(self, obj):
        # FIXME: Implement
        pass
        
    def toggle_pause(self):
        pass
        

class Game(ShowBase, Settings):
    def __init__(self):
        # Basics
        ShowBase.__init__(self)
        # settings = Settings()
        base.disableMouse()
        base.setFrameRateMeter(True)
        base.camLens.set_near(0.1)
        base.setBackgroundColor(0, 0, 0)
        self.accept("escape", sys.exit)
        # Create the geometry
        self.geosphere = Geosphere()
        t1 = datetime.datetime.now()
        self.geosphere_np = self.geosphere.create_node()
        t2 = datetime.datetime.now()
        print(t2-t1)
        self.geosphere_np.reparent_to(self.render)
        self.bases = nx.Graph()
        self.add_bases()
        # Music
        self.music_player = MusicPlayer(self)
        # Game state
        self.game_state = GameState()
        self.game_state.start()
        # Controls
        self.accept("m", self.toggle_geosphere_unwrapping)
        self.accept("arrow_right", self.move_camera, [1, 0, 0])
        self.accept("arrow_left", self.move_camera, [-1, 0, 0])
        self.accept("arrow_up", self.move_camera, [0, 1, 0])
        self.accept("arrow_down", self.move_camera, [0, -1, 0])
        self.accept("wheel_up", self.move_camera, [0, 0, -1])
        self.accept("wheel_down", self.move_camera, [0, 0, 1])
        self.accept("c", self.game_state.set_clock_factor, [0.0])
        self.accept("v", self.game_state.set_clock_factor, [1.0])
        self.accept("b", self.game_state.set_clock_factor, [60.0])
        self.accept("n", self.game_state.set_clock_factor, [3600.0])
        self.accept("j", self.game_state.skip_to_next_event)
        self.accept("l", self.load, ["savegame.yml"])
        self.accept("s", self.save, ["savegame.yml"])

    def load(self, filename):
        self.game_state.shutdown()
        f = open(filename, 'r')
        state = yaml.load(f.read())
        f.close()
        self.game_state = GameState(state)
        self.accept("c", self.game_state.set_clock_factor, [0.0])
        self.accept("v", self.game_state.set_clock_factor, [1.0])
        self.accept("b", self.game_state.set_clock_factor, [60.0])
        self.accept("n", self.game_state.set_clock_factor, [3600.0])
        self.accept("j", self.game_state.skip_to_next_event)
        self.game_state.start()
    
    def save(self, filename):
        f = open(filename, 'w')
        f.write(yaml.dump(self.game_state.get_state()))
        f.close()

    def toggle_geosphere_unwrapping(self):
        self.geosphere.toggle_unwrap()
    
    def add_bases(self):
        # All your bases are belong to me.
        for base_id, base_def in bases.iteritems():
            if base_def['active']:
                u, v = base_def['coords']
                game_base = Base(u, v)
                self.bases.add_node(base_id)
                self.geosphere.add_base(game_base)
        # Now for a connection
        for b1, b2 in [(22, 3), (3, 135), (135, 112), (112, 54)]:
            self.bases.add_edge(b1, b2)
            c1, c2 = bases[b1]['coords'], bases[b2]['coords']
            self.geosphere.add_connection(c1, c2)
    
    def move_camera(self, x, y, zoom):
        self.geosphere.move_camera(x*0.05, y*0.05, zoom*0.5)

class Base:
    def __init__(self, u, v):
        self.coords = (u, v)
        model = base.loader.loadModel("./assets/models/base")
        self.np = NodePath(model)
        
    def get_nodepath(self):
        return self.np
        
    def get_coordinates(self):
        return self.coords

game = Game()
game.run()

