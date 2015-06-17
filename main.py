
from __future__ import division

import parameters
import players
import random
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import csv
import sys


class SeriesInstance(object):
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
        self.convergence_sequence = []
        self.networkState = False
        self.timeSteps_to_convergence = []
        self.numGames = parameters.numGames
        self.number_of_non_convergences = 0


    def createPlayers_list(self):
        """ creates players """
        self.playersList = [players.Player() for count in range(self.numPlayers)]

    def assignAttributes(self):
        """ every agent gets a number of options, to choose his nash strategy from """
        strategies = range(0, self.numStrategies)
        for player in self.playersList:
            player.strategies = strategies

    def createNetwork(self):
        """ self.playerNetwork, is a network of players, which refer to Player instances
            every agent gets the number of his agents """
        mapping = dict(enumerate(self.playersList))

        if self.networkType == 'scaleFree':
            G = nx.barabasi_albert_graph(self.numPlayers, self.meanDegree)
            #G = nx.watts_strogatz_graph(self.numPlayers, self.meanDegree, 0.5)
            self.playerNetwork = nx.relabel_nodes(G, mapping)

        for player in self.playersList:
            player.numberNeighbors = len(self.playerNetwork.neighbors(player))

    def collect_neighbor_states(self, player):
        """ each of the two players collects the states of his neighbors """
        neighbors = self.playerNetwork.neighbors(player)
        neighborsStates = [neighbor.returnState() for neighbor in neighbors]
        player.update_neighborsStates(neighborsStates)

    def one_round(self, player):
        """ plays one round """
        playerA = self.playersList[player]
        playerB = random.sample(self.playersList, 1)[0]
        self.collect_neighbor_states(playerA)
        self.collect_neighbor_states(playerB)
        playerA.compute_conditional_probabilities()
        playerB.compute_conditional_probabilities()


        if playerA.move() == playerB.move():
            playerA.updateResult(1)
            playerB.updateResult(1)
        else:
            playerA.updateResult(0)
            playerB.updateResult(0)

    def is_converged(self):
        """ tests whether all players have the same state """
        move = self.playersList[0].lastMove
        for player in self.playersList:
            if player.lastMove != move:
                return False
        return True

    def game(self):
        """ creates the players, strategies and network; runs the simulation until convergence
            is achieved; time of convergence or in case of non-convergence False is appended """
        self.createPlayers_list()
        self.assignAttributes()
        self.createNetwork()
        self.networkState = False

        player = 0
        for i in range(self.timeSteps):
            self.one_round(player)
            if self.is_converged():
                self.timeSteps_to_convergence.append(i)
                return
            player += 1
            if player == len(self.playersList):
                player = 0
                random.shuffle(self.playersList)
        self.number_of_non_convergences += 1

    def series_with_same_parameter(self):
        """ runs the game self.numGames times """
        for _ in range(self.numGames):
            self.game()


class ParameterSweep(object):
    range_players = np.arange(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    with open('data.csv', 'wb') as csvfile:
        for num_player in range_players:
            print('players', num_player)
            series_instance = SeriesInstance()
            series_instance.numPlayers = num_player
            series_instance.series_with_same_parameter()
            mean = np.mean(series_instance.timeSteps_to_convergence)
            var = np.std(series_instance.timeSteps_to_convergence)
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([num_player, mean, var, series_instance.number_of_non_convergences])
    print('done')


ParameterSweep()
