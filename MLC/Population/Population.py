import numpy as np
import math
import MLC.Log.log as lg

from MLC.individual.Individual import Individual
from MLC.matlab_engine import MatlabEngine
from MLC.mlc_table.MLCTable import MLCTable
from MLC.Population.Creation.CreationFactory import CreationFactory
from MLC.Population.Evaluation.EvaluatorFactory import EvaluatorFactory
from MLC.mlc_parameters.mlc_parameters import Config


class Population(object):
    amount_population = 0
    GEN_METHOD_ELITISM = 4

    def __init__(self):
        Population.inc_pop_number()
        # Set global parameters as variables for easier use in the class
        self._eng = MatlabEngine.engine()
        self._config = Config.get_instance()

        cascade = self._config.get_list('OPTIMIZATION', 'cascade')
        size = self._config.get_list('POPULATION', 'size')

        self._gen = Population.get_current_pop_number()
        self._size = cascade[1] if (self._gen > 1 and len(size) > 1) else size[0]
        self._state = 'init'
        self._subgen = 1 if cascade[1] == 0 else cascade[1]

        # Declare MATLAB attributes
        self._individuals = [-1] * self._size
        self._costs = [-1] * self._size
        self._gen_method = [-1] * self._size

        # TODO: Parents impl
        self._parents = [-1] * self._size

        lg.logger_.debug("Population created. Number: %s - Size: %s" % (self._gen, self._size))

    def create(self, table=None):
        gen_method = self._config.get('GP', 'generation_method')
        lg.logger_.info("Using %s to generate population" % gen_method)
        gen_creator = CreationFactory.make(self._eng, self._config, gen_method)
        gen_creator.create(self._size)
        self.set_individuals(gen_creator.individuals())

    def evaluate(self):
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
        gen = Population.get_current_pop_number()
        lg.logger_.info('Evaluation of generation %s' % gen)

        ev_method = self._config.get('EVALUATOR', 'evaluation_method')
        lg.logger_.info('Evaluation method: ' + ev_method)

        evaluator = EvaluatorFactory.make(ev_method)
        jj = evaluator.evaluate(self._individuals, gen)

        # Update table individuals and MATLAB Population indexes and costs
        # matlab_pop = Population.population(gen)
        bad_value = self._config.getfloat('EVALUATOR', 'badvalue')

        for i in xrange(self._size):
            index = i
            # mlab_index = eval_idx[i]

            if str(jj[index]) == 'nan' or \
               str(jj[index]) == 'inf' or \
               jj[index] > bad_value:
                lg.logger_.debug(('[POP][EVALUATE] Individual N#: {0}.'
                                  ' Invalid value found: {1}')
                                 .format(self._individuals[index], jj[index]))

                jj[index] = bad_value

            lg.logger_.debug('[POP][EVALUATE] Idx: {0} '
                             '- Indiv N#: {1} - Cost: {2}'
                             .format(index, self._individuals[index], jj[index]))

            MLCTable.get_instance().update_individual(int(self._individuals[index] - 1), jj[index])
            # self._eng.set_cost(matlab_pop, mlab_index, jj[index])

        self._costs = jj

    def remove_bad_individuals(self):
        # Get the individuals which value is the same as the
        # badvalue defined in the configuration
        bad_value = self._config.getfloat('EVALUATOR', 'badvalue')
        bad_list = [x for x in xrange(len(self._costs)) if self._costs[x] == bad_value]

        if len(bad_list) > 0.4 * len(self._individuals):
            lg.logger_.info('[POP][BAD_INDIVS] %s '
                            'individuals will be removed.' % len(bad_list))

            # The threshold was surpassed. Remove the individuals and return the
            # list of individuals removed
            for indiv_index in bad_list:
                self._remove_individual(indiv_index)

            return bad_list
        else:
            return []

    def remove_duplicates(self):
        # Sort the individual array and get the indexes of every element
        # in the original list
        indexes = [i[0] for i in sorted(enumerate(self._individuals), key=lambda x:x[1])]
        sorted_indivs = sorted(self._individuals)

        # Compare every element in the list with the following one. If they are the same,
        # remove the individual
        i = 0
        amount_indivs_removed = 0
        while i < (self._size - 1):
            if sorted_indivs[i] == sorted_indivs[i + 1]:
                lg.logger_.debug("[POPULATION] Proceed to remove Individual "
                                 "N#{indiv} from Population N#{pop_number})"
                                 .format(indiv=indexes[i], pop_number=self._gen))
                amount_indivs_removed += 1
                self._remove_individual(indexes[i])
            i += 1

        lg.logger_.info("[POPULATION] Individuals removed: ", amount_indivs_removed)

    def _remove_individual(self, index):
        self._individuals[index] = -1
        self._costs[index] = -1
        self._gen_method[index] = -1
        # TODO: Parents impl
        self._parents[index] = -1

    def update_individual(self, dest_index, rhs_pop, rhs_index, gen_method):
        """
        Replace one individual with another.
        """
        self._individuals[dest_index] = rhs_pop.get_individuals()[rhs_index]
        self._costs[dest_index] = rhs_pop.get_costs()[rhs_index]
        self._gen_method[dest_index] = gen_method
        # TODO: Parents logical
        # self._parents[dest_index] = rhs_pop.get_parents()[rhs_index]

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
    def inc_pop_number():
        Population.amount_population += 1

    @staticmethod
    def get_current_pop_number():
        return Population.amount_population

    def evolve(self, mlcpop2=None):
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
        ngen = Population.get_current_pop_number()

        new_pop = mlcpop2
        if new_pop is None:
            new_pop = Population()

        lg.logger_.info('[POPULATION] Evolving population N#: ' + str(self._gen))

        # FIXME: It's not necessary to compute the creation of both subgenerations
        # The ranges of both of them will be the same
        pop_subgen = self.create_subgen()
        pop_subgen2 = new_pop.create_subgen()
        subgen_amount = len(pop_subgen)

        for i in range(len(pop_subgen)):
            lg.logger_.info("[POPULATION] Evolving subpopulation {0} of {1}".format(i + 1, subgen_amount))
            # Get the indexes of the non valid elements in this subpopulation
            subgen_begin = pop_subgen[i][0]
            subgen_end = pop_subgen[i][1]

            subgen2_begin = pop_subgen2[i][0]
            subgen2_end = pop_subgen2[i][1]

            # IMPORTANT: Before the first evolution of the new Population, all the elements are invalid. In the
            # second evolution of Population is when all this algorithm will have any sense
            not_valid_indexes = [x[0] + subgen2_begin
                                 for x in enumerate(new_pop.get_individuals()[subgen2_begin:subgen2_end])
                                 if x[1] == -1]

            individuals_created = 0
            param_elitism = self._config.getint('OPTIMIZATION', 'elitism')

            # Apply the elitism algorithm only if we're not modifying a previously evolved population
            if not mlcpop2:
                try:
                    elitism_indivs_per_subgen = int(math.ceil(param_elitism / subgen_amount))
                    for j in range(elitism_indivs_per_subgen):
                        subgen_indexes = range(subgen2_begin, subgen2_end)

                        pop_idv_index_orig = subgen_indexes[j]
                        # This could cause a IndexError
                        pop_idv_index_dest = not_valid_indexes[individuals_created]
                        lg.logger_.debug("[POPULATION] Elitism - Destination individual: " + str(pop_idv_index_dest))

                        # Update the individual in the new population with the first param_elitism
                        new_pop.update_individual(pop_idv_index_dest, self,
                                                  pop_idv_index_orig, Population.GEN_METHOD_ELITISM)
                        MLCTable.get_instance().get_individual(new_pop.get_individuals()[pop_idv_index_dest]).inc_appearences()
                        individuals_created += 1
                except IndexError:
                    lg.logger.error("[POPULATION] Elitism - More individuals to replace than empty ones."
                                    "Stop elitism algorithm")

            print self.get_individuals()
            print new_pop.get_individuals()
            exit(-1)

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
                        old_ind = mlctable.get_individual(old_individual)
                        new_ind, fail = old_ind.mutate(mlc_parameters)

                    mlctable, number, repeated = mlctable.add_individual(new_ind)
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

                    mlctable, number, repeated = mlctable.add_individual(new_ind)
                    eng.set_individual(mlcpop2, idv_dest, number)
                    eng.set_cost(mlcpop2, idv_dest, -1)
                    eng.set_parent(mlcpop2, idv_dest, [idv_orig, idv_orig2])
                    eng.set_gen_method(mlcpop2, idv_dest, 3)
                    # TODO:
                    # mlctable.individuals(number).appearences =
                    #   mlctable.individuals(number).appearences+1;
                    individuals_created += 1

                    mlctable, number2, repeated = mlctable.add_individual(new_ind2)
                    eng.set_individual(mlcpop2, idv_dest2, number2)
                    eng.set_cost(mlcpop2, idv_dest2, -1)
                    eng.set_parent(mlcpop2, idv_dest2, [idv_orig, idv_orig2])
                    eng.set_gen_method(mlcpop2, idv_dest2, 3)
                    # TODO:
                    # mlctable.individuals(number2).appearences =
                    # mlctable.individuals(number2).appearences+1;
                    individuals_created += 1

        return mlcpop2

    def sort(self):
        # Calculate subgenerations
        subgens = self.create_subgen()

        indivs = []
        costs = []
        gen_method = []
        parents = []

        # Order the MATLAB population attributes per subgeneration
        for subgen in subgens:
            # Sort the population by intervals. Reorder the population arrays
            indexes = [i[0] for i in sorted(enumerate(self._costs[subgen[0]:subgen[1] + 1]), key=lambda x:x[1])]

            for i in xrange(subgen[1] - subgen[0] + 1):
                indivs.append(self._individuals[indexes[i]])
                costs.append(self._costs[indexes[i]])
                gen_method.append(self._gen_method[indexes[i]])
                parents.append(self._parents[indexes[i]])

        self._individuals = indivs
        self._costs = costs
        self._gen_method = gen_method
        self._parents = parents

    def create_subgen(self):
        # Create subgenerations from the actual Population
        subgens = []
        indivs_per_subgen = math.floor(float(self._size) / self._subgen)
        begin = 0
        end = int(indivs_per_subgen)
        i = 1

        # Create the subgen as intervals of the full list of indivis
        # Example: If size = 100 and subgen = 3, then 3 subgenerations will be
        # created. [1:33] [34:66] [67:100]
        while i < self._subgen:
            subgen = (begin, end - 1)
            subgens.append(subgen)
            begin = end + 1
            end += indivs_per_subgen
            i += 1

        subgens.append((begin, int(self._size - 1)))
        return subgens

    def get_state(self):
        return self._state

    def set_state(self, rhs_state):
        self._state = rhs_state

    def get_size(self):
        return self._size

    def get_individuals(self):
        return self._individuals

    def set_individuals(self, indiv_list):
        for x in indiv_list:
            self._individuals[x[0]] = int(x[1])

    def get_costs(self):
        return self._costs

    """
    def set_indiv_index(self, index, new_indiv_index):
        try:
            self._individuals[index] = new_indiv_index
            return True
        except IndexError:
            lg.logger_.error("[POPULATION] set_indiv_index - Index out of bounds.")

        return False

    def set_indiv_cost(self, index, new_cost):
        try:
            self._costs[index] = new_cost
            return True
        except IndexError:
            lg.logger_.error("[POPULATION] set_indiv_cost - Index out of bounds.")

        return False

    def set_indiv_gen_method(self, index, gen_method):
        try:
            self._gen_method[index] = gen_method
            return True
        except IndexError:
            lg.logger_.error("[POPULATION] set_indiv_gen_method - Index out of bounds.")

        return False
    """
