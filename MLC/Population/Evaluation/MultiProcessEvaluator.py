# -*- coding: utf-8 -*-
# MLC (Machine Learning Control): A genetic algorithm library to solve chaotic problems
# Copyright (C) 2015-2017, Thomas Duriez (thomas.duriez@gmail.com)
# Copyright (C) 2015, Adrian Durán (adrianmdu@gmail.com)
# Copyright (C) 2015-2017, Ezequiel Torres Feyuk (ezequiel.torresfeyuk@gmail.com)
# Copyright (C) 2016-2017, Marco Germano Zbrun (marco.germano@intraway.com)
# Copyright (C) 2016-2017, Raúl Lopez Skuba (raulopez0@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import sys
import MLC.Log.log as lg

from MLC.db.mlc_repository import MLCRepository
from MLC.individual.Individual import Individual
from MLC.mlc_parameters.mlc_parameters import Config

from multiprocessing import Process
from multiprocessing import Queue
from threading import Lock


class StopMonitor(object):

    def __init__(self):
        self._experiment_finished = False
        self._lock = Lock()

    def is_experiment_finished(self):
        with self._lock:
            return self._experiment_finished

    def finish_experiment(self):
        with self._lock:
            self._experiment_finished = True


class Worker(Process):

    def __init__(self, worker_id,
                 input_queue, output_queue,
                 callback, stop_monitor):
        super(Worker, self).__init__()
        self._id = worker_id
        self._callback = callback
        self._input_queue = input_queue
        self._output_queue = output_queue
        self._callback = callback
        self._stop_monitor = stop_monitor
        self._log_prefix = "[WORKER N°{}] ".format(self._id)

    def run(self):
        lg.logger_.info("{}Entering worker process loop.".format(self._log_prefix))
        while not self._stop_monitor.is_experiment_finished():
            data = self._input_queue.get()
            if data is None:
                break

            lg.logger_.info("{}Proceed to evaluate Individual N°{}"
                            .format(self._log_prefix, data["index"]))

            lg.logger_.debug("{}Individual N°{} - Value: {}"
                             .format(self._log_prefix, data["index"],
                                     data["indiv"].get_value()))

            cost = self._callback.cost(data["indiv"])
            lg.logger_.info("{}Indivual N°{} was evaluated. Cost: {}"
                            .format(self._log_prefix,
                                    data["index"],
                                    cost))

            # We return the Individual id and the cost as output
            self._output_queue.put((data["index"], cost))

        lg.logger_.info("{}Exitting worker process loop.".format(self._log_prefix))


class MultiProcessEvaluator(object):

    def __init__(self, callback, callback_manager):
        self._config = Config.get_instance()
        self._input_queue = Queue()
        self._output_queue = Queue()
        self._stop_monitor = StopMonitor()
        self._callback = callback
        self._callback_manager = callback_manager

    def evaluate(self, indivs):
        # Create a list with the capacity of the Individuals to evaluate
        lg.logger_.info("[MULTIPROCESS_EV] Proceed to evaluate {} individuals"
                        .format(len(indivs)))

        # Check if the evaluation function exists before starting
        try:
            indiv = Individual(value="(root 0)")
            self._callback.cost(indiv)
        except KeyError:
            lg.logger_.error("[MULTIPROCESS_EV] Evaluation Function " +
                             "doesn't exists. Aborting progam.")
            sys.exit(-1)

        # The function exists, proceed to calculate the costs of the Individuals
        workers_count = self._config.getint("EVALUATOR",
                                            "multiprocess_workers_count")

        workers = [Worker(index,
                          self._input_queue,
                          self._output_queue,
                          self._callback,
                          self._stop_monitor) for index in range(workers_count)]

        for worker in workers:
            worker.start()

        # Enqueue all the individuals to process in the Thread Pool queue
        for index in indivs:
            # Retrieve the individual to be evaluated
            py_indiv = MLCRepository.get_instance().get_individual(index)
            self._input_queue.put({"index": index, "indiv": py_indiv})

        # Receive the results
        costs_received = 0
        dict_results = {}
        while costs_received < len(indivs):
            result = self._output_queue.get()
            index = result[0]
            cost = result[1]
            dict_results[str(index)] = cost
            costs_received += 1

            from MLC.Application import MLC_CALLBACKS
            self._callback_manager.on_event(MLC_CALLBACKS.ON_EVALUATE, index, cost)

        lg.logger_.info("[MULTIPROCESS_EV] {} Individuals were evaluated"
                        .format(len(indivs)))

        # self._stop_monitor.finish_experiment()
        for _ in range(len(workers)):
            self._input_queue.put(None)

        for worker in workers:
            worker.join()

        # Order the costs obtained as they were put in the input queue
        jj = [dict_results[str(index)] for index in indivs]
        return jj
