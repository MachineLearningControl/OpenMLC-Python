import numpy as np

import MLC.Log.log as lg
from MLC.Population.Creation.CreationFactory import CreationFactory
from MLC.Population.Evaluation.EvaluatorFactory import EvaluatorFactory


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
        self._gen = gen if gen else 1
        self._costs = []

        cascade = config.get_param('OPTIMIZATION', 'cascade', type='array')
        size = config.get_param('POPULATION', 'size', type='array')

        self._subgen = 1 if cascade[1] == 0 else cascade[1]
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

    def evaluate(self):
        gen = str(Population.get_actual_pop_number())
        lg.logger_.info('Evaluation of generation ' + gen)

        ev_method = self._config.get('EVALUATOR', 'evaluation_method')
        lg.logger_.info('Evaluation method: ' + ev_method)

        # TODO: Serialization of the population.

        evaluator = EvaluatorFactory.make(self._eng, self._config, ev_method)
        jj = evaluator.evaluate(self._individuals,
                                Population.get_actual_pop_number())

        # Update table individuals and MATLAB Population indexes and costs
        table = self._eng.eval('wtable')
        matlab_pop = self._eng.eval('wmlc.population(' + str(gen) + ')')
        bad_value = self._config.getfloat('EVALUATOR', 'badvalue')

        for idx in xrange(len(jj)):
            self._eng.update_individual(table, self._individuals[idx], jj[idx])

            if str(jj[idx]) == 'nan' or str(jj[idx]) == 'inf':
                lg.logger_.debug('[POP][EVALUATE] Individual N#: ' +
                                 str(self._individuals[idx]) +
                                 '. Invalid value found: ' + str(jj[idx]))
                jj[idx] = bad_value

            lg.logger_.debug('[POP][EVALUATE] Idx: ' + str(idx + 1) +
                             ' - Indiv N#: ' + str(self._individuals[idx]) +
                             ' - Cost: ' + str(jj[idx]))

            self._eng.set_cost(matlab_pop, idx + 1, jj[idx])

        self._costs = jj

    def remove_bad_individuals(self):
        bad_value = self._config.getfloat('EVALUATOR', 'badvalue')
        bad_list = \
            [x for x in xrange(len(self._costs)) if self._costs[x] == bad_value]

        if len(bad_list) > 0.4 * len(self._individuals):
            lg.logger_.info('[POP][BAD_INDIVS] ' + str(len(bad_list)) +
                            ' individuals will be removed.')
            # TODO: Remove the individuals
            return
        else:
            return []

    def remove_duplicates(self):
        # TODO:
        pass

    def _remove_individual(self, index):
        '''
        function mlcpop=remove_individual(mlcpop,idx_to_remove)
        mlcpop.individuals(idx_to_remove)=-1;
        mlcpop.costs(idx_to_remove)=-1;
        mlcpop.gen_method(idx_to_remove)=-1;
        mlcpop.parents(idx_to_remove)=cell(1,length(idx_to_remove));
        '''
        # TODO:
        pass

    def set_individuals(self, indiv_list):
        for x in indiv_list:
            self._individuals[x[0]] = x[1]

    def get_individuals(self):
        return self._individuals
