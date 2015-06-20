
from __future__ import division

import parameters
import players2 as players
import random
import networkx as nx
import sys
import numpy as np
import scipy.stats
import csv
import zmq
import json


class SeriesInstance(object):
    def __init__(self, num_states, num_players):
        self.numStates = num_states
        self.numPlayers = num_players
        self.proportion_Players=parameters.proportion_Players
        self.epsilon=parameters.epsilon
        self.proportion = 1 - self.epsilon
        self.players_every_round=0
        self.networkType = 'scaleFree'
        self.playersList = []
        self.playerNetwork = 0
        self.meanDegree = parameters.meanDegree
        self.systemState_measure_frequency = parameters.measureSystem_state_frequency
        self.timeSteps = parameters.timeSteps
        self.numGames=parameters.numGames
        self.convergence_sequence = []
        self.timeSteps_to_convergence=[]
        self.converged=False
        # proportion of players playing each state
        self.states_dynamics=dict((i,[]) for i in range(self.numStates))
        self.number_of_non_convergences = 0

    def createPlayers_list(self):
        """ creates players """
        self.playersList = [players.player() for count in xrange(self.numPlayers)]

    def assignAttributes(self):
        """ every agent gets a number of options, to choose his nash strategy from """
        for player in self.playersList:
            player.numStates = self.numStates
            player.state = random.choice(range(self.numStates))

    def createNetwork(self):
        """ self.playerNetwork, is a network of players, which refer to Player instances
            every agent gets the number of his agents """
        mapping = dict(enumerate(self.playersList))

        if self.networkType == 'scaleFree':
            G = nx.barabasi_albert_graph(self.numPlayers, self.meanDegree)
            #G = nx.watts_strogatz_graph(self.numPlayers, self.meanDegree,1)
            self.playerNetwork = nx.relabel_nodes(G, mapping)

    def update_players_every_round(self):
        a = int(self.numPlayers * self.proportion_Players)
        if a % 2 == 0:
            return a
        else:
            return a - 1


    def sample_players(self):
        return random.sample(self.playersList, self.players_every_round)

    def collect_neighbor_states(self, players):
        """ each of the two players collects the states of his neighbors """
        for player in players:
            neighbors = self.playerNetwork.neighbors(player)
            neighbors_states = []
            for j in neighbors:
                state = j.state
                neighbors_states.append(state)
            player.update_neighbors_states(neighbors_states)

    def update_state(self, players):
        for player in players:
            player.update_state()

    def return_system_convergence(self):
        states = [0] * self.numStates
        for player in self.playersList:
            states[player.state] += 1
        states = [state / self.numPlayers for state in states]
        highest = max(states)
        return highest

    def update_convergence_sequence(self):
        a = self.return_system_convergence()
        self.convergence_sequence.append(a)

    def is_converged(self):
        return self.return_system_convergence() > self.proportion


    def update_states_dynamics(self):
        states = [0] * self.numStates
        for i in self.playersList:
            states[i.state] += 1
        states = [x / self.numPlayers for x in states]

        for i in range(self.numStates):
            self.states_dynamics[i].append(states[i])


    def round(self):
        players=self.sample_players()
        self.collect_neighbor_states(players)
        self.update_state(players)


    def game(self):
        self.createPlayers_list()
        self.assignAttributes()
        self.createNetwork()
        self.players_every_round = self.update_players_every_round()
        for step in range(self.timeSteps):
            self.round()
            if step % self.systemState_measure_frequency == 0:
                if self.is_converged():
                    self.timeSteps_to_convergence.append(step)
                    return
        self.number_of_non_convergences += 1


    def run(self):
        for _ in range(self.numGames):
            self.game()

def simulate_one_parameter_set(name, num_states, num_players):
    series_instance = SeriesInstance(num_states, num_players)
    series_instance.run()
    mean = np.mean(series_instance.timeSteps_to_convergence)
    var = np.std(series_instance.timeSteps_to_convergence)
    print('players: %d, strategies: %d, mean: %.0f, non convergences: %d' % (
    num_players, num_states, mean, series_instance.number_of_non_convergences))
    with open(name, 'ab') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow([num_players, num_states, mean, var,
                     series_instance.number_of_non_convergences,
                     parameters.timeSteps,
                     parameters.measureSystem_state_frequency,
                     parameters.meanDegree,
                     parameters.numGames,
                     parameters.epsilon,
                     parameters.proportion_Players])

def parameter_sweep():
    if sys.argv[1] == 's':
        assert sys.argv[5] == 'p'
        range_strategies = np.arange(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
        range_players = [int(sys.argv[6])]
    elif sys.argv[1] == 'p':
        assert sys.argv[5] == 's'
        range_players = np.arange(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
        range_strategies = [int(sys.argv[6])]
    elif sys.argv[1] == 'z':
        pass
    else:
        print("python main.py s 1 100 10 p 1000")
        print("python main.py s from strategy to step p number of players")
        print("python main.py p 1 10000 100 s 100")
        print("python main.py p from number of players to step s number of strategies")
        return

    if sys.argv[1] == 's' or sys.argv[1] == 'p':
        name = 'final%s_%06d_%06d_%06d_%s_%06d.csv' % (
                   sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]),
                   sys.argv[5], int(sys.argv[6]))
        for num_players in range_players:
            for num_states in range_strategies:
                simulate_one_parameter_set(name, num_states, num_players)
    elif sys.argv[1] == 'z':

        offset = int(sys.argv[3])

        address_task = 5557 + offset
        address_result = 5558 + offset
        address_kill = 5559 + offset

        address_prefix = sys.argv[2]

        print("address_prefix: %s, address_task: %d, address_result %d, address_kill: %d" % (
            address_prefix, address_task, address_result, address_kill))

        context = zmq.Context(1)

        receiver = context.socket(zmq.REQ)
        print("tcp://%s:%i" % (address_prefix, address_task))
        receiver.connect("tcp://%s:%i" % (address_prefix, address_task))

        sender = context.socket(zmq.PUSH)
        sender.connect("tcp://%s:%i" % (address_prefix, address_result))


        while True:
            print("Receiving")
            receiver.send("ready")
            message = receiver.recv()
            try:
                param = json.loads(message)
            except:
                sender.send("message not parsed")
            name = param['name']
            num_players = int(param['num_players'])
            num_states = int(param['num_states'])
            print("Received and Working," , message)
            simulate_one_parameter_set(name, num_states, num_players)
            print("Worked and Send:")
            sender.send(json.dumps({'finished': True}))
    print('done')

parameter_sweep()
