
from __future__ import division
import random

# create a class of players
class player(object):
    def __init__(self):
        self.numberNeighbors = 0
        self.numStates = 0
        self.state = 0
        # how many neighbors have each of the possible states
        self.frequency_neighborsStates = [0] * self.numStates

    def update_neighbors_states(self,states):
        self.frequency_neighborsStates = [0] * self.numStates
        for i in states:
            self.frequency_neighborsStates[i] += 1

    def update_state(self):
        m = max(self.frequency_neighborsStates)
        states = [i for i, x in enumerate(self.frequency_neighborsStates) if x == m]
        state = random.choice(states)
        self.state=state

