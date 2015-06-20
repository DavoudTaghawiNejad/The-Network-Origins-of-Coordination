#pylint: disable=C0103, C0111, C0301, C0325, E1101
from __future__ import division
import zmq
import json
from time import time
import logging
import sys



class ConnectRemote(object):
    def __init__(self, adress_offset, task=5557, result=5558, address_prefix="tcp://*:"):
        self.context = zmq.Context()
        self.sender = self.context.socket(zmq.REP)
        self.sender.bind(address_prefix + str(task + adress_offset))
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.bind(address_prefix + str(result + adress_offset))

    def vent(self, jobs):
        i = 0
        for job in jobs:
            print(job)
            self.sender.recv()
            self.sender.send_string(json.dumps(job))
            i += 1
            print('\rout: %i/%i  ' % (i, len(jobs))),
            sys.stdout.flush()

    def sink(self, total_tasks):
        done_tasks = 0
        timeout = 0
        results = []
        while done_tasks < total_tasks:
            msg = self.receiver.recv()
            done_tasks += 1
            element = json.loads(msg)
            results.append(element)
            print('\rdone: %i/%i timeout: %i  ' % (done_tasks, total_tasks, timeout)),
            sys.stdout.flush()
        return results

    def run(self, jobs):
        t = time()
        print("going to vent"),
        self.vent(jobs)
        work_done = self.sink(len(jobs))
        print("finished in: %f" % (time() - t))
        return work_done

