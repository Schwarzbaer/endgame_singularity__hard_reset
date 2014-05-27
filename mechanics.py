import datetime
import yaml
import pprint
import copy

from direct.task import Task

default_snapshot = {'players': [0],
                    'iron_man': {'active': False,
                                 'savefile': '',
                                 },
                    'time': 0.0,
                    'entity': {'ISA': {'detection': 0.10,
                                       'suspicion': 0.20,
                                       },
                               },
                    }

class GameState:
    def __init__(self, state = False):
        if not state:
            self.snapshot = default_snapshot
            self.timeline = []
            starting_time = datetime.datetime.utcnow() + datetime.timedelta(seconds = 60*20)
            self.add_event({'time': starting_time + datetime.timedelta(seconds = 20),
                            'type': 'inc_isa',
                            'stopping': True})
            self.add_event({'time': starting_time + datetime.timedelta(seconds = 40),
                            'type': 'inc_isa',
                            'stopping': False})
            self.add_event({'time': starting_time + datetime.timedelta(seconds = 60),
                            'type': 'inc_isa',
                            'stopping': True})
            self.add_event({'time': starting_time + datetime.timedelta(seconds = 80),
                            'type': 'inc_isa',
                            'stopping': False})
            self.add_event({'time': datetime.datetime.max,
                            'type': 'end_of_time',
                            'stopping': True})
            self.clock_time = starting_time
        else: 
            self.snapshot = state['snapshot']
            self.timeline = state['timeline']
            self.clock_time = state['clock']
        self.clock_factor = 0.0
        self.find_next_event_time()

    def get_state(self):
        return {'snapshot': self.snapshot,
                'timeline': self.timeline,
                'clock': self.clock_time}
        
    def add_event(self, event):
        self.timeline.append(event)
        
    def find_next_event_time(self):
        self.next_event_time = min([e['time'] for e in self.timeline])
    
    def pop_next_event(self):
        pos = [e['time'] for e in self.timeline].index(self.next_event_time)
        event = self.timeline[pos]
        del self.timeline[pos]
        self.find_next_event_time()
        return event
    
    def set_clock_factor(self, factor):
        self.clock_factor = factor

    def start(self):
        base.taskMgr.add(self.tick, "Game Clock")
        self.last_real_time = datetime.datetime.utcnow()
    
    def shutdown(self):
        base.taskMgr.remove("Game Clock")
    
    def skip_to_next_event(self):
        stop_for_interaction = False
        while (not stop_for_interaction):
            event = self.pop_next_event()
            new_snapshot = process_event(event, self.snapshot)
            self.timeline = [reschedule(e, self.snapshot, new_snapshot) for e in self.timeline]
            if event['stopping']:
                stop_for_interaction = True
            new_snapshot = process_event(event, self.snapshot)
            self.timeline = [reschedule(e, self.snapshot, new_snapshot) for e in self.timeline]
        self.clock_factor = 0.0
        self.clock_time = event['time']
        
    def tick(self, task):
        now = datetime.datetime.utcnow()
        dt = now - self.last_real_time
        new_time = self.clock_time + datetime.timedelta(seconds = dt.total_seconds() * self.clock_factor)
        # Check for events that should have taken place
        stop_for_interaction = False
        while (not stop_for_interaction) and new_time > self.next_event_time:
            event = self.pop_next_event()
            new_snapshot = process_event(event, self.snapshot)
            self.timeline = [reschedule(e, self.snapshot, new_snapshot) for e in self.timeline]
            if event['stopping']:
                stop_for_interaction = True
        if stop_for_interaction:
            self.clock_factor = 0.0
            self.clock_time = event['time']
        else:
            self.clock_time = new_time
        self.last_real_time = now
        return Task.cont

def process_event(event, snapshot):
    print("Processing Event")
    new_snapshot = copy.deepcopy(snapshot)
    if event['type'] == 'inc_isa':
        pass
    return new_snapshot

def reschedule(event, old_snapshot, new_snapshot):
    print("Rescheduling Event")
    new_event = copy.deepcopy(event)
    return new_event
