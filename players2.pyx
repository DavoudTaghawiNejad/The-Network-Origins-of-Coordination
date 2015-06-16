
# cython: profile=True
from __future__ import division
import random
import parameters as parameters
import numpy as np
# create a class of players

class Player(object):
    def __init__(self):
        # set of strategies to choose from
        self.strategies = []
        # two state variables: last move and last result
        self.lastMove = random.choice(xrange(parameters.numStrategies))
        self.lastResult = 0
        # the states of neighbors
        # this list will be populated with tuples where fist element is the strategy, second element is outcome
        self.neighborsStates = []
        self.numberNeighbors = 0 ## needs to be cdef

        # a list of probabilities of coordination associated with each strategy
        self.conditional_coordinationProb = [0.0] * len(self.strategies)

    # compute the conditional probability of coordinating by playing a given strategy s
    def compute_prob_strategy(self, s):
        """ P(c|s)=P(s|c)*P(c)/P(s) """

        # P(c)
        cdef int numberNeighbors = self.numberNeighbors
        cdef int total_coordinations = 0
        cdef float prob_C

        for i in self.neighborsStates:
            if i[1] == 1:
                total_coordinations += 1

        prob_C = total_coordinations / numberNeighbors


        # P(s)
        cdef int total_neigh_S = 0
        cdef float prob_S

        total_neigh_S = 0
        for i in self.neighborsStates:
            if i[0] == s:
                total_neigh_S += 1

        prob_S = total_neigh_S / numberNeighbors

        # P(s|c)
        cdef int temp
        cdef float prob_S_given_C
        cdef float prob_C_given_S


        temp = 0

        for i in self.neighborsStates:
            if i[1] == 1 and i[0] == s:
                temp += 1

        if total_coordinations != 0:
            prob_S_given_C = temp / total_coordinations
        else:
            prob_S_given_C = 0

        if prob_S != 0:
            prob_C_given_S = prob_S_given_C * prob_C / prob_S
        else:
            prob_C_given_S = 0

        return prob_C_given_S

    # a player can return a move
    def compute_conditional_probabilities(self):
        self.conditional_coordinationProb = np.empty(len(self.strategies), dtype=float)
        for s in self.strategies:
            self.conditional_coordinationProb[s] = self.compute_prob_strategy(s)

    def returnMove(self):
        m = max(self.conditional_coordinationProb)
        moves = [i for i, x in enumerate(self.conditional_coordinationProb) if x == m]
        move = random.choice(moves)
        self.lastMove = move
        return move

    def updateResult(self, result):
        self.lastResult = result

    def update_neighborsStates(self, states):
        self.neighborsStates = states

    def returnState(self):
        return [self.lastMove, self.lastResult]


