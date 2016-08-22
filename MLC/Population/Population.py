import numpy as np
import math

import MLC.Log.log as lg
from MLC.Population.Creation.CreationFactory import CreationFactory
from MLC.Population.Evaluation.EvaluatorFactory import EvaluatorFactory
from MLC.matlab_engine import MatlabEngine

from MLC.individual.Individual import Individual
from MLC.mlc_table.MLCTable import MLCTable


class Population(object):
    amount_population = 0

    def __init__(self, config, gen=1):
        self._eng = MatlabEngine.engine()

        self._config = config
        self._gen = gen
        self._costs = []

        cascade = config.get_list('OPTIMIZATION', 'cascade')
        size = config.get_list('POPULATION', 'size')

        self._subgen = 1 if cascade[1] == 0 else cascade[1]
        self._gen_size = cascade[1] if (self._gen > 1 and len(size) > 1) else size[0]
        self._individuals = np.zeros(self._gen_size, dtype=int)
        self._state = 'init'

        lg.logger_.debug("Population created. Number: %s - Size: %s" % (self._gen, self._gen_size))

    def create(self, table=None):
        if table is None:
            self._eng.workspace['wtable'] = self._eng.MLCtable(int(self._gen_size) * 50)

        gen_method = self._config.get('GP', 'generation_method')
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
                             .format(index, self._individuals[index], jj[index]))

            self._eng.update_individual(table, int(self._individuals[index]), jj[index])
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
            self._individuals[x[0]] = int(x[1])

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
    def evolve(mlcpop, mlc_parameters, matlab_mlctable, mlcpop2=None):
        """
        # uncomment this section to use MLC original evolve implementation
        from matlab
        if mlcpop2 is None:
            return MatlabEngine.engine().evolve(mlcpop,
                                                mlc_parameters,
                                                matlab_mlctable,
                                                nargout=1)
        else:
            return MatlabEngine.engine().evolve(mlcpop,
                                                mlc_parameters,
                                                matlab_mlctable,
                                                mlcpop2,
                                                nargout=1)
        """
        # wrap matlab MLCtable in a python object
        mlctable = MLCTable(matlab_mlctable)

        eng = MatlabEngine.engine()
        ngen = eng.get_gen(mlcpop)

        # verb = mlc_parameters.verbose;
        verb = True

        new_mlcpop2 = mlcpop2 is None
        if new_mlcpop2:
            mlcpop2 = eng.MLCpop(mlc_parameters.get_matlab_object(), ngen + 1)

        if verb:
            lg.logger_.info('Evolving population')

        idxsubgen = eng.subgen(mlcpop, mlc_parameters.get_matlab_object())[0]
        cell_idxsubgen2 = eng.subgen(mlcpop2, mlc_parameters.get_matlab_object())
        idxsubgen2 = cell_idxsubgen2[0]

        for i in range(0, len(idxsubgen2)):

            # TODO: Implements this strange line in python and remove
            # @MLCpop::init_generation method
            # idxsubgen2{i}=idxsubgen2{i}(mlcpop2.individuals(
            #   idxsubgen2{i})==-1);
            idxsubgen2 = eng.init_generation(mlcpop2, cell_idxsubgen2, i + 1)[0]
            # if len(idxsubgen2) == 1, matlab return a float object instead
            # of an array
            if type(idxsubgen2) == float:
                idxsubgen2 = [[idxsubgen2]]

            if verb:
                lg.logger_.info('Evolving sub-population %s/%s' % (i, eng.get_subgen(mlcpop2)))

            if len(idxsubgen) == 1:
                idx_source_pool = idxsubgen[0]
            else:
                idx_source_pool = idxsubgen[i]

            individuals_created = 0

            param_elitism = mlc_parameters.getint('OPTIMIZATION', 'elitism')

            # elitism
            if new_mlcpop2:
                for i_el in range(0, int(math.ceil(param_elitism / len(idxsubgen2)))):
                    idv_orig = idx_source_pool[i_el]
                    idv_dest = idxsubgen2[i][individuals_created]
                    # print 'ELITISM - IDV_ORIG: %s - IDV_DEST: %s'
                    # % (idv_orig, idv_dest)
                    eng.set_individual(mlcpop2, idv_dest, eng.get_individual(mlcpop, idv_orig))
                    eng.set_cost(mlcpop2, idv_dest, eng.get_cost(mlcpop, idv_orig))
                    eng.set_parent(mlcpop2, idv_dest, idv_orig)
                    eng.set_gen_method(mlcpop2, idv_dest, 4)
                    # TODO: mlctable.individuals(mlcpop.individuals(
                    #           idv_orig)).appearences=
                    #       mlctable.individuals(mlcpop.individuals(
                    #           idv_orig)).appearences+1;
                    individuals_created += 1

            # completing population
            while individuals_created < len(idxsubgen2[i]):
                lg.logger_.debug('LEN idx_sub: %s' % (len(idxsubgen2[i]) - individuals_created))
                op = eng.choose_genetic_operation(mlcpop, mlc_parameters.get_matlab_object(),
                                                  len(idxsubgen2[i]) - individuals_created)

                if op == 'replication':
                    idv_orig = eng.choose_individual_(mlcpop, mlc_parameters.get_matlab_object(), idx_source_pool)
                    idv_dest = idxsubgen2[i][individuals_created]

                    # print 'REPLICATION - IDV_ORIG: %s - IDV_DEST: %s' %
                    # (idv_orig, idv_dest)
                    eng.set_individual(mlcpop2, idv_dest, eng.get_individual(mlcpop, idv_orig))
                    eng.set_cost(mlcpop2, idv_dest, eng.get_cost(mlcpop, idv_orig))
                    eng.set_parent(mlcpop2, idv_dest, idv_orig)
                    eng.set_gen_method(mlcpop2, idv_dest, 1)
                    # TODO: mlctable.individuals(mlcpop.individuals(
                    #           idv_orig)).appearences=
                    #       mlctable.individuals(mlcpop.individuals(
                    #           idv_orig)).appearences+1;
                    individuals_created += 1

                elif op == 'mutation':
                    new_ind = None
                    fail = True
                    while fail:
                        idv_orig = eng.choose_individual_(mlcpop, mlc_parameters.get_matlab_object(), idx_source_pool)
                        idv_dest = idxsubgen2[i][individuals_created]
                        # print 'MUTATION - IDV_ORIG: %s - IDV_DEST: %s' %
                        # (idv_orig, idv_dest)
                        old_individual = eng.get_individual(mlcpop, idv_orig)
                        old_ind = mlctable.individuals(old_individual)
                        new_ind, fail = old_ind.mutate(mlc_parameters)

                    mlctable, number = mlctable.add_individual(new_ind)
                    eng.set_individual(mlcpop2, idv_dest, number)
                    eng.set_cost(mlcpop2, idv_dest, -1)
                    eng.set_parent(mlcpop2, idv_dest, idv_orig)
                    eng.set_gen_method(mlcpop2, idv_dest, 2)
                    # mlctable.individuals(number).appearences =
                    #   mlctable.individuals(number).appearences+1;
                    individuals_created += 1

                elif op == 'crossover':
                    fail = True
                    while fail:
                        idv_orig = eng.choose_individual_(mlcpop, mlc_parameters.get_matlab_object(), idx_source_pool)
                        idv_orig2 = idv_orig

                        while idv_orig2 == idv_orig:
                            idv_orig2 = eng.choose_individual_(mlcpop, mlc_parameters.get_matlab_object(), idx_source_pool)

                        idv_dest = idxsubgen2[i][individuals_created]
                        idv_dest2 = idxsubgen2[i][individuals_created + 1]
                        lg.logger_.debug('CROSSOVER - IDV_ORIG 1 : %s - '
                                         'IDV_DEST 1 : %s'
                                         % (idv_orig, idv_dest) +
                                         '- IDV_ORIG 2 : %s - IDV_DEST 2 : %s'
                                         % (idv_orig2, idv_dest2))
                        old_individual = eng.get_individual(mlcpop, idv_orig)
                        old_ind = mlctable.individuals(old_individual)
                        old_individual = eng.get_individual(mlcpop, idv_orig2)
                        old_ind2 = mlctable.individuals(old_individual)
                        new_ind, new_ind2, fail = old_ind.crossover(old_ind2, mlc_parameters)

                    mlctable, number = mlctable.add_individual(new_ind)
                    eng.set_individual(mlcpop2, idv_dest, number)
                    eng.set_cost(mlcpop2, idv_dest, -1)
                    eng.set_parent(mlcpop2, idv_dest, [idv_orig, idv_orig2])
                    eng.set_gen_method(mlcpop2, idv_dest, 3)
                    # TODO:
                    # mlctable.individuals(number).appearences =
                    #   mlctable.individuals(number).appearences+1;
                    individuals_created += 1

                    mlctable, number2 = mlctable.add_individual(new_ind2)
                    eng.set_individual(mlcpop2, idv_dest2, number2)
                    eng.set_cost(mlcpop2, idv_dest2, -1)
                    eng.set_parent(mlcpop2, idv_dest2, [idv_orig, idv_orig2])
                    eng.set_gen_method(mlcpop2, idv_dest2, 3)
                    # TODO:
                    # mlctable.individuals(number2).appearences =
                    # mlctable.individuals(number2).appearences+1;
                    individuals_created += 1

        return mlcpop2
