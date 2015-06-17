
from __future__ import division

import parameters
import players
import random
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import csv


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
        for i in self.playersList:
            i.strategies = strategies

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


    def sampleTwo_players(self):
        """ returns two random players """
        players = random.sample(self.playersList, 2)
        return players

    def communicate(self, players):
        """ each of the (two) players in players gets to negotiate with its neighbors """
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
        """ plays one round """
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

    def is_converged(self):
        """ tests whether all players have the same state """
        move = self.playersList[0].lastMove
        for player in self.playersList:
            if player.lastMove != move:
                return False

    def game(self):
        """ creates the players, strategies and network; runs the simulation until convergence
            is achieved; time of convergence or in case of non-convergence False is appended """
        self.createPlayers_list()
        self.assignAttributes()
        self.createNetwork()
        self.networkState = False

        for i in range(self.timeSteps):
             self.one_round()
             if self.is_converged():
                 self.timeSteps_to_convergence.append(i)
                 return
        self.number_of_non_convergences += 1

    def series_with_same_parameter(self):
        """ runs the game self.numGames times """
        for i in range(self.numGames):
            self.game()


class ParameterSweep(object):
    incrementPlayers = 100
    range_players = np.arange(90, 91, incrementPlayers)
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
