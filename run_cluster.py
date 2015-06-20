from __future__ import division
from connect_remote import ConnectRemote
import sys
import numpy as np


def main():
    name = 'bigdata%s_%06d_%06d_%06d_%s_%06d.csv' % (
               sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]),
               sys.argv[5], int(sys.argv[6]))

    if sys.argv[1] == 's':
        assert sys.argv[5] == 'p'
        range_strategies = np.arange(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
        num_players = int(sys.argv[6])
        jobs = [{'name': name, 'num_players': num_players, 'num_states': num_states}
                for num_states in range_strategies]

    elif sys.argv[1] == 'p':
        assert sys.argv[5] == 's'
        range_players = np.arange(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
        num_states = int(sys.argv[6])
        jobs = [{'name': name, 'num_players': num_players, 'num_states': num_states}
                for num_players in range_players]
    elif sys.argv[1] == 'z':
        pass
    else:
        print("python main.py s 1 100 10 p 1000")
        print("python main.py s from strategy to step p number of players")
        print("python main.py p 1 10000 100 s 100")
        print("python main.py p from number of players to step s number of strategies")
        print("python main.py z 1")
        print("python main.py z address offset")
        return

    assert sys.argv[7] == 'o'
    connect_remote = ConnectRemote(adress_offset=int(sys.argv[8]))
    connect_remote.run(jobs)

main()
