
from __future__ import division

import parameters
import players
import random
import networkx as nx
import numpy as np
import csv
import sys


class SeriesInstance(object):
    def __init__(self, num_strategies, num_players):
        self.timeSteps = parameters.timeSteps
        self.numStrategies = num_strategies
        self.numPlayers = num_players
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
        self.playersList = [players.Player(self.num_strategies) for count in range(self.numPlayers)]


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

    def run(self):
        """ runs the game self.numGames times """
        for _ in range(self.numGames):
            self.game()



def parameter_sweep():
    if sys.argv[1] == 's':
        assert sys.argv[5] == 'p'
        range_strategies = np.arange(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
        range_players = [int(sys.argv[6])]
    elif sys.argv[1] == 'p':
        assert sys.argv[5] == 's'
        range_players = np.arange(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
        range_strategies = [int(sys.argv[6])]
    else:
        print("format python main.py s 1 100 10 p 1000")
        print("format python main.py s from strategy to step p number of players")
        print("format python main.py p 1 10000 100 s 100")
        print("format python main.py p from number of players to step s number of strategies")
        return

    with open('data%s_%06d_%06d_%06d_%s_%06d.csv' % (
               sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]),
               sys.argv[5], int(sys.argv[6])), 'wb') as csvfile:
        for num_players in range_players:
            for num_strategies in range_strategies:
                series_instance = SeriesInstance(num_strategies, num_players)
                series_instance.run()
                mean = np.mean(series_instance.timeSteps_to_convergence)
                var = np.std(series_instance.timeSteps_to_convergence)
                print('players: %d, strategies: %d, mean: %d, non convergences: %d' % (
                    num_players, num_strategies, mean, series_instance.number_of_non_convergences))
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow([num_players, num_strategies, mean, var,
                                 series_instance.number_of_non_convergences,
                                 parameters.timeSteps,
                                 parameters.meanDegree,
                                 parameters.WattsStrogatz_rewiringProb,
                                 parameters.numGames])
    print('done')


parameter_sweep()
