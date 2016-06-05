import numpy as np

import MLC.Log.log as lg
from MLC.Population.Creation.CreationFactory import CreationFactory
from MLC.Population.Evaluation.EvaluatorFactory import EvaluatorFactory
from MLC.matlab_engine import MatlabEngine


class Population(object):
    amount_population = 0

    def __init__(self, config, gen=1):
        self._eng = MatlabEngine.engine()

        self._config = config
        self._gen = gen
        self._costs = []

        cascade = config.get_param('OPTIMIZATION', 'cascade', type='array')
        size = config.get_param('POPULATION', 'size', type='array')

        self._subgen = 1 if cascade[1] == 0 else cascade[1]
        self._gen_size = cascade[1] if (
            self._gen > 1 and len(size) > 1) else size[0]
        self._individuals = np.zeros(self._gen_size, dtype=int)
        self._state = 'init'

        lg.logger_.debug("Population created. Number: %s - Size: %s" %
                         (self._gen, self._gen_size))

    def create(self, table=None):
        if table is None:
            self._eng.workspace['wtable'] = self._eng.MLCtable(
                self._gen_size * 50)

        gen_method = self._config.get_param('GP', 'generation_method')
        lg.logger_.info("Using %s to generate population" % gen_method)
        gen_creator = CreationFactory.make(self._eng, self._config, gen_method)
        gen_creator.create(self._gen_size)

        self.set_individuals(gen_creator.individuals())

    def evaluate(self, eval_idx):
        """
        Evaluates cost of individuals and update the MLC object MLC_OBJ.
        All options are set in the MLC object.
        Implemented:
            - evaluation with m-file function (standalone and multihread),
                external evaluation with file exchange.
            - detection of bad individuals (above a threshold) and their
                replacement.
            - evaluation or not of already evaluated individuals.
            - averaging of all past cost values for a given individual if
                evaluation are repeated (for experiments or
                numerics with random noise).
        """
        gen = Population.get_actual_pop_number()
        lg.logger_.info('Evaluation of generation %s' % gen)

        ev_method = self._config.get('EVALUATOR', 'evaluation_method')
        lg.logger_.info('Evaluation method: ' + ev_method)

        # TODO: Serialization of the population.

        evaluator = EvaluatorFactory.make(self._eng, self._config, ev_method)
        jj = evaluator.evaluate(eval_idx, self._individuals, gen)

        # Update table individuals and MATLAB Population indexes and costs
        table = self._eng.eval('wtable')
        matlab_pop = Population.population(gen)
        bad_value = self._config.getfloat('EVALUATOR', 'badvalue')

        for i in xrange(len(eval_idx)):
            index = eval_idx[i] - 1
            mlab_index = eval_idx[i]

            if str(jj[index]) == 'nan' or \
               str(jj[index]) == 'inf' or \
               jj[index] > bad_value:
                lg.logger_.debug(
                    ('[POP][EVALUATE] Individual N#: {0}.'
                     ' Invalid value found: {1}')
                    .format(self._individuals[index], jj[index]))

                jj[index] = bad_value

            lg.logger_.debug('[POP][EVALUATE] Idx: {0} '
                             '- Indiv N#: {1} - Cost: {2}'
                             .format(index,
                                     self._individuals[index], jj[index]))

            self._eng.update_individual(
                table, self._individuals[index], jj[index])
            self._eng.set_cost(matlab_pop, mlab_index, jj[index])

        self._costs = jj

    def remove_bad_individuals(self):
        bad_value = self._config.getfloat('EVALUATOR', 'badvalue')
        bad_list = [x for x in xrange(len(self._costs)) if self._costs[
            x] == bad_value]

        if len(bad_list) > 0.4 * len(self._individuals):
            lg.logger_.info(
                '[POP][BAD_INDIVS] %s '
                'individuals will be removed.' % len(bad_list))
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

    @staticmethod
    def population(generation_id):
        """
        Return a generation object from the list (index starts from 1)
        """
        if generation_id > Population.generations():
            raise IndexError('generation index out of range')
        return MatlabEngine.engine().eval('wmlc.population(' +
                                          str(generation_id) + ')')

    @staticmethod
    def generations():
        """
        Return the total amount of generations.
        """
        return int(MatlabEngine.engine().eval('length(wmlc.population)'))

    @staticmethod
    def get_gen_individuals(generation_id):
        if generation_id > Population.generations():
            raise IndexError('generation index out of range')

        return MatlabEngine.engine().eval('wmlc.population(%s).individuals'
                                          % generation_id)

    @staticmethod
    def inc_pop_number():
        Population.amount_population += 1

    @staticmethod
    def get_actual_pop_number():
        return Population.amount_population

    @staticmethod
    def evolve(mlcpop, mlc_parameters, mlctable, mlcpop2=None):
        if mlcpop2 is None:
            return MatlabEngine.engine().evolve(mlcpop,
                                                mlc_parameters,
                                                mlctable,
                                                nargout=1)
        else:
            return MatlabEngine.engine().evolve(mlcpop,
                                                mlc_parameters,
                                                mlctable,
                                                mlcpop2,
                                                nargout=0)
