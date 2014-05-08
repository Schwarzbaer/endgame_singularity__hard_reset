#!/usr/bin/env python2

# TODO
#   Music Player
#   Change the base notation of coordinates from pixel/pixel to uv
#   Oh my god, so much cleanup...

from direct.showbase.ShowBase import ShowBase
import sys
from geosphere import Geosphere
import datetime
import networkx as nx
from bases import bases, base_id, coords, name, active
from panda3d.core import NodePath

class Game(ShowBase):
    def __init__(self):
        # Basics
        ShowBase.__init__(self)
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
        # Controls
        self.accept("m", self.toggle_geosphere_unwrapping)
        self.accept("b", self.add_base)
        self.accept("arrow_right", self.move_camera, [1, 0, 0])
        self.accept("arrow_left", self.move_camera, [-1, 0, 0])
        self.accept("arrow_up", self.move_camera, [0, 1, 0])
        self.accept("arrow_down", self.move_camera, [0, -1, 0])
        self.accept("wheel_up", self.move_camera, [0, 0, -1])
        self.accept("wheel_down", self.move_camera, [0, 0, 1])
        
    def toggle_geosphere_unwrapping(self):
        self.geosphere.toggle_unwrap()
    
    def add_base(self):
        # All your bases are belong to me.
        for base_def in [b for b in bases if b[active]]:
            u, v = base_def[coords]
            u = float(u)/8192.0
            v = 1.0 - float(v)/4096.0
            game_base = Base(u, v)
            self.bases.add_node(base_def[base_id])
            self.geosphere.add_base(game_base)
        # Now for a connection
        for b1, b2 in [(3,22), (135, 3), (54, 112)]:
            bases_by_id = dict([(b[base_id], b) for b in bases])
            self.bases.add_edge(b1, b2)
            c1, c2 = bases_by_id[b1][coords], bases_by_id[b2][coords]
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

