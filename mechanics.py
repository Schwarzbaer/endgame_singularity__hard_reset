# A GameSetup is a configuration of a game session. It is generated
#   at the beginning of a session and is immutable during the game.
# A GameState is the state of the game at a fixed point in game time.
#   It too is technically immutable. Player interaction and events
#   cause new GameStates to be created, representing the point in
#   game time at which a change took place. They are generated
#   solely by extrapolation, making it unneccessary to recalculate
#   them every frame or set unit of time. They should keep track of
#   what exactly has been changed to minimize processing during
#   Event updates.
# Events are points in time at which a change in GameState takes
#   place, or which serve as alerts for the player that a certain
#   set limit would be reached in an extrapolation of the GameState.
#   They consist of their planned point in time, relevant data and
#   an underlying GameState.
# A Timeline is a collection of Events. Every time a new GameState is
#   created, all Events in the Timelime update themselves to using
#   the new GameState as their new underlying one.

import datetime
import yaml

from direct.task import Task

class GameSetup:
    def __init__(self):
        self.setup = {'players': [0],
                      'iron_man': {'active': False,
                                   'savefile': '',
                                  },
                     }
                     
    def get_setup(self):
        return self.setup

class GameState:
    def __init__(self, game_setup, load_file = False):
        self.game_setup = game_setup
        self.game_state = {'time': 0.0,
                           'entity': {'ISA': {'detection': 10.0,
                                              'suspicion': 20.0,
                                             },
                                     },
                          }
        if load_file: # Load gamestate from file
            pass
        else: # Create new game
            self.time = datetime.datetime.utcnow() + datetime.timedelta(seconds = 1200)
            self.iron_man = False # FIXME: If in Iron Man mode, use the savegames file name here
            
    def get_state_var(self, var_name):
        subtree = self.game_state
        var_path = var_name.split('.')
        try:
            for sub_var_name in var_path:
                subtree = subtree[sub_var_name]
            return subtree
        except KeyError:
            print("Unknown token "+sub_var_name+" in variable name "+var_name)
            
class Timeline:
    def __init__(self, game_state):
        self.game_state = game_state
        self.events = []
        self.timeline.add_event(Event(datetime.datetime.max, False, False))
        self.next_event_time = False
        
    def add_event(self, event):
        self.events.append(event)
        self.determine_next_event()
        
    def pop_event(self):
        event_pos = [e.get_time() for e in self.events].index(self.next_event_time)
        event = self.events[event_pos]
        del self.events[event_pos]
        self.determine_next_event()
        return event
    
    #def project_update(self, new_gamestate):
    #    """Determine what the timeline would look like if a new GameState would be applied."""
    #    return [e.project_update(new_gamestate) for e in self.events]
    #    
    #def update(self, new_gamestate):
    #    """Update the timeline based on a new gamestate."""
    #    self.events = self.project_update(new_gamestate)

    def process_next_event(self):
        event = self.pop_event()
        event_time = event.get_time()
        # FIXME: Do the actual processing
        # FIXME: update the event list
        return event
        
    def determine_next_event(self):
        """When will the next event take place?"""
        self.next_event_time = min([e.get_time() for e in self.events])
    
    def get_next_event_time(self):
        return self.next_event_time

class Event:
    def __init__(self, time, new_gamestate, stopping = False):
        """stopping: True if this events allows the player to react,
                     which stops the game clock."""
        self.time = time
        self.base_gamestate = new_gamestate
        self.stopping = stopping
        
    def __repr__(self):
        return str(self.time) + ": Base Event"
        
    def reschedule(self, new_gamestate):
        # FIXME: Magic here
        self.base_gamestate = new_gamestate

    def get_time(self):
        return self.time
    
    def get_stopping(self):
        return self.stopping

# The Game Clock

class GameClock:
    def __init__(self, timeline):
        self.timeline = timeline
        self.time = False # This is game time
        self.last_time = False # This is real time, used to determine game time elapsed per frame
        self.factor = 4.0
        
    def set_time(self, time):
        self.time = time
        
    def set_factor(self,factor):
        self.factor = factor
        
    def start(self):
        base.taskMgr.add(self.tick, "Game Clock")
        self.last_time = datetime.datetime.utcnow()
    
    def skip_clock_to_next_event(self):
        self.factor = 0.0 # There WILL be a stopping event here!
        stop_for_interaction = False
        while (not stop_for_interaction):
            event = self.timeline.process_next_event()
            print("Event happening: " + str(event.get_time()))
            if event.get_stopping():
                stop_for_interaction = True
        self.time = event.get_time()

    def tick(self, task):
        now = datetime.datetime.utcnow()
        dt = now - self.last_time
        new_time = self.time + datetime.timedelta(seconds = dt.total_seconds() * self.factor)
        print(new_time)
        # Check for events that should have taken place
        stop_for_interaction = False
        while (not stop_for_interaction) and new_time >= self.timeline.get_next_event_time():
            event = self.timeline.process_next_event()
            print("Event happening: " + str(event.get_time()))
            if event.get_stopping():
                stop_for_interaction = True
        if stop_for_interaction:
            self.factor = 0.0
            self.time = event.get_time()
        else:
            self.time = new_time
        self.last_time = now
        return Task.cont


# import mechanics
# game_setup = mechanics.GameSetup()
# game_state = mechanics.GameState(game_setup)
# timeline = mechanics.Timeline()
# timeline.add_event(mechanics.Event(10, game_state))

