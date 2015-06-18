# cython: profile=True
from __future__ import division
import random
import parameters as parameters
# create a class of players

cdef class Player(object):
    cdef public object strategies
    cdef public int lastMove
    cdef int lastResult
    cdef object neighborsStates
    cdef object conditional_coordinationProb
    cdef public int numberNeighbors

    def __cinit__(self):
        # set of strategies to choose from
        self.strategies = []
        # two state variables: last move and last result
        self.lastMove = random.randrange(parameters.numStrategies)
        self.lastResult = 0
        # the states of neighbors
        # this list will be populated with tuples where fist element is the strategy, second element is outcome
        self.neighborsStates = []
        self.numberNeighbors = 0

        # a list of probabilities of coordination associated with each strategy
        self.conditional_coordinationProb = [0.0] * len(self.strategies)

    # compute the conditional probability of coordinating by playing a given strategy s

    cdef compute_prob_strategy(self, int s):
        # P(s)
        cdef int total_neigh_S = 0
        cdef float prob_S
        cdef float prob_S_given_C
        cdef float prob_C_given_S

        for i in self.neighborsStates:
            if i[0] == s:
                total_neigh_S += 1
        if total_neigh_S != 0:
            prob_S = total_neigh_S / self.numberNeighbors

            prob_S_given_C = 0

            # P(s|c)
            for i in self.neighborsStates:
                if i[1] == 1 and i[0] == s:
                    prob_S_given_C += 1

            prob_C_given_S = prob_S_given_C / prob_S

            return prob_C_given_S

        else:
            return 0

    # a player can return a move
    def compute_conditional_probabilities(self):
        self.conditional_coordinationProb = [self.compute_prob_strategy(s) for s in self.strategies]

    def move(self):
        cdef int move
        m = max(self.conditional_coordinationProb)
        moves = [i for i, x in enumerate(self.conditional_coordinationProb) if x == m]
        move = random.choice(moves)
        self.lastMove = move
        return move

    def updateResult(self, int result):
        self.lastResult = result

    def update_neighborsStates(self, states):
        self.neighborsStates = states

    def returnState(self):
        return [self.lastMove, self.lastResult]


