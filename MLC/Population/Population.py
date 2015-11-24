import numpy as np

import MLC.Log.log as lg
from MLC.Population.Creation.CreationFactory import CreationFactory


class Population(object):
    amount_population = 0

    @staticmethod
    def inc_pop_number():
        Population.amount_population += 1

    @staticmethod
    def get_actual_pop_number():
        return Population.amount_population

    def __init__(self, eng, config, gen=None):
        self._eng = eng
        self._config = config

        if gen:
            self._gen = gen

        cascade = config.get_param('OPTIMIZATION', 'cascade', type='array')
        size = config.get_param('POPULATION', 'size', type='array')

        self._gen = 1 if cascade[1] == 0 else cascade[1]
        self._gen_size = cascade[1] \
            if (self._gen > 1 and len(size) > 1) else size[0]
        self._individuals = np.zeros(self._gen_size, dtype=int)
        self._state = 'init'

        lg.logger_.debug("Population created. Number: " +
                         str(self._gen) + " - Size: " +
                         str(self._gen_size))

    def create(self, table=None):
        if table is None:
            self._eng.workspace['wtable'] = \
                self._eng.MLCtable(self._gen_size * 50)

        gen_method = self._config.get_param('GP', 'generation_method')
        lg.logger_.info("Using " + gen_method + " to generate population")
        gen_creator = CreationFactory.make(self._eng, self._config, gen_method)
        gen_creator.create(self._gen_size)

        self.set_individuals(gen_creator.individuals())

    def evaluate(self, eval_idx):
        # TODO: Serialization of the population
        a = 1

    def set_individuals(self, indiv_list):
        for x in indiv_list:
            self._individuals[x[0]] = x[1]

    def get_individuals(self):
        return self._individuals

