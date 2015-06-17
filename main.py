
from __future__ import division

import parameters
import players
import random
import matplotlib.pyplot as plt
import networkx as nx
import copy
import numpy as np
import scipy.stats
import csv


class SimulationInstance(object):
    def __init__(self):
        self.timeSteps = parameters.timeSteps
        self.numStrategies = parameters.numStrategies
        self.numPlayers = parameters.numPlayers
        self.network = 0
        self.playersList = []
        self.networkType = 'scaleFree'
        self.meanDegree = parameters.meanDegree
        self.playerNetwork = 0
        self.WattsStrogatz_rewiringProb = parameters.WattsStrogatz_rewiringProb
        self.systemState_measure_frequency = parameters.measureSystem_state_frequency
        self.convergence_sequence = []
        self.networkState = False
        self.timeSteps_to_convergence = []
        self.numGames = parameters.numGames


    def createPlayers_list(self):
        self.playersList = [players.Player() for count in range(self.numPlayers)]

    def assignAttributes(self):
        strategies = range(0, self.numStrategies)
        for i in self.playersList:
            i.strategies = strategies

    def createNetwork(self):
        mapping = dict(enumerate(self.playersList))

        if self.networkType == 'scaleFree':
            G = nx.barabasi_albert_graph(self.numPlayers, self.meanDegree)
            #G = nx.watts_strogatz_graph(self.numPlayers, self.meanDegree, 0.5)
            self.playerNetwork = nx.relabel_nodes(G, mapping)

        for player in self.playersList:
            player.numberNeighbors = len(self.playerNetwork.neighbors(player))


    def sampleTwo_players(self):
        players = random.sample(self.playersList, 2)
        return players

    def communicate(self, players):
        for player in players:
            neighbors = self.playerNetwork.neighbors(player)
            neighborsStates = [neighbor.returnState() for neighbor in neighbors]
            player.update_neighborsStates(neighborsStates)

    def compute(self,players):
        for i in players:
            i.compute_conditional_probabilities()

    def returnMoves(self,players):
        moves=[]
        for i in players:
            moves.append(i.returnMove())
        return moves

    def play(self):
        players = self.sampleTwo_players()
        self.communicate(players)
        self.compute(players)
        moves = self.returnMoves(players)

        if moves[0]==moves[1]:
            players[0].updateResult(1)
            players[1].updateResult(1)
        else:
            players[0].updateResult(0)
            players[1].updateResult(0)

	# this part of the code is definitely doing too much work because
    # all we want to know if all agents have the same state
	# as soon as we find two agents don't have same state we can exit, and keep running the code
    def compute_stateNetwork(self):
        states = [0] * self.numStrategies
        for i in self.playersList:
            player_state = i.returnState()[0]
            states[player_state]+=1

        states_normalized = []
        for i in states:
            states_normalized.append(i / self.numPlayers)

        if max(states_normalized)==1:
            self.networkState=True

        #return states_normalized

    def checkNetwork_convergence(self,state,count):
        if count == (self.numPlayers):
            return True
        else:
            if self.playersList[count].returnState()[0] == state:
                count=count+1
                return self.checkNetwork_convergence(state,count)
            else:

                return False

    def game(self):
        self.createPlayers_list()
        self.assignAttributes()
        self.createNetwork()
        self.networkState = False

        for i in range(self.timeSteps):
             if self.networkState is False:
                 self.play()
                 if i % self.systemState_measure_frequency == 0 and i < (self.timeSteps - 1):
                     #state=self.playersList[0].returnState()[0]
                     #self.networkState=self.checkNetwork_convergence(state,0)
                     self.compute_stateNetwork()
                     if self.networkState is True:
                         self.timeSteps_to_convergence.append(i)
                 elif i==(self.timeSteps-1):
                    self.timeSteps_to_convergence.append(False)

    def games(self):
        for i in range(self.numGames):
            self.game()



#instanceDo = do()
#instanceDo.games()


#plt.plot(instanceDo.timeSteps_to_convergence)
#plt.show()


class ParameterSweep(object):
    incrementPlayers = 100
    range_players = np.arange(90, 91, incrementPlayers)
    with open('data19.csv', 'wb') as csvfile:
        for num_player in range_players:
            print('players', num_player)
            simulation_instance = SimulationInstance()
            simulation_instance.numPlayers = num_player
            simulation_instance.games()
            mean = np.mean(simulation_instance.timeSteps_to_convergence)
            var = scipy.stats.variation(simulation_instance.timeSteps_to_convergence)
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([num_player, mean, var])
    print('done')


ParameterSweep()
