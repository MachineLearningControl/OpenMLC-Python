import numpy as np
import math
import MLC.Log.log as lg
import sys

from MLC.individual.Individual import Individual
from MLC.matlab_engine import MatlabEngine
from MLC.mlc_table.MLCTable import MLCTable
from MLC.Population.Creation.CreationFactory import CreationFactory
from MLC.Population.Evaluation.EvaluatorFactory import EvaluatorFactory
from MLC.mlc_parameters.mlc_parameters import Config


class Population(object):
    amount_population = 0
    GEN_METHOD_REPLICATION = 1
    GEN_METHOD_MUTATION = 2
    GEN_METHOD_CROSSOVER = 3
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
            if str(jj[i]) == 'nan' or \
               str(jj[i]) == 'inf' or \
               jj[i] > bad_value:
                lg.logger_.debug(('[POP][EVALUATE] Individual N#: {0}.'
                                  ' Invalid value found: {1}')
                                 .format(self._individuals[i], jj[i]))

                jj[i] = bad_value

            lg.logger_.debug('[POP][EVALUATE] Idx: {0} '
                             '- Indiv N#: {1} - Cost: {2}'
                             .format(i, self._individuals[i], jj[i]))

            MLCTable.get_instance().update_individual(int(self._individuals[i]), jj[i])

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

        lg.logger_.info("[POPULATION] Individuals removed: " + str(amount_indivs_removed))
        return amount_indivs_removed

    def _remove_individual(self, index):
        self._individuals[index] = -1
        self._costs[index] = -1
        self._gen_method[index] = -1
        # TODO: Parents impl
        # self._parents[index] = -1

    def update_individual(self, dest_index, rhs_pop, rhs_index,
                          indiv_index, gen_method, cost=None):
        """
        Replace one individual with another.
        """
        self._individuals[dest_index] = indiv_index
        if not cost:
            self._costs[dest_index] = rhs_pop.get_costs()[rhs_index]
        else:
            self._costs[dest_index] = cost
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
        ngen = Population.get_current_pop_number()
        mlctable = MLCTable.get_instance()

        new_pop = mlcpop2
        if new_pop is None:
            new_pop = Population()

        lg.logger_.info('[POPULATION] Evolving population N#' + str(self._gen))

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

            # Amount of individuals per subgeneration. Take into consideration that
            # the last subgeneration could differ from the others
            # (that's why we're calculating the value on each iteration)
            indivs_per_subgen2 = subgen2_end - subgen2_begin + 1

            # IMPORTANT: Before the first evolution of the new Population, all the elements are invalid. In the
            # second evolution of Population is when all this algorithm will have any sense
            not_valid_indexes = [x[0] + subgen2_begin
                                 for x in enumerate(new_pop.get_individuals()[subgen2_begin:subgen2_end + 1])
                                 if x[1] == -1]

            individuals_created = 0
            param_elitism = self._config.getint('OPTIMIZATION', 'elitism')

            # Apply the elitism algorithm only if we're NOT modifying a previously evolved population
            if not mlcpop2:
                try:
                    elitism_indivs_per_subgen = int(math.ceil(param_elitism / subgen_amount))
                    for j in range(elitism_indivs_per_subgen):
                        subgen_indexes = range(subgen2_begin, subgen2_end)

                        pop_idv_index_orig = subgen_indexes[j]
                        # This could cause a IndexError
                        pop_idv_index_dest = not_valid_indexes[individuals_created]
                        lg.logger_.debug("[POPULATION] Elitism - Orig indiv {0} - Dest indiv {1}"
                                         .format(pop_idv_index_orig, pop_idv_index_dest))

                        # Update the individual in the new population with the first param_elitism
                        indiv_index = self._individuals[pop_idv_index_orig]
                        new_pop.update_individual(pop_idv_index_dest, self,
                                                  pop_idv_index_orig, indiv_index,
                                                  Population.GEN_METHOD_ELITISM)

                        mlctable.get_individual(new_pop.get_individuals()[pop_idv_index_dest]).inc_appearences()
                        individuals_created += 1
                except IndexError:
                    lg.logger.error("[POPULATION] Elitism - More individuals to replace than empty ones."
                                    "Stop elitism algorithm")

            # completing population
            while individuals_created < indivs_per_subgen2:
                indivs_left = indivs_per_subgen2 - individuals_created
                op = Population.choose_genetic_operation(indivs_left)
                lg.logger_.debug("[POPULATION] Indivs left in subgen {0}: {1} "
                                 "- Operation chosen: {2}".format(i + 1, indivs_left, op))

                if op == "replication":
                    pop_idv_index_orig = self._choose_individual(pop_subgen[i])
                    pop_idv_index_dest = not_valid_indexes[individuals_created]
                    lg.logger_.debug("[POPULATION] Replication - Orig indiv {0} - Dest indiv {1}"
                                     .format(pop_idv_index_orig, pop_idv_index_dest))

                    indiv_index = self._individuals[pop_idv_index_orig]
                    new_pop.update_individual(pop_idv_index_dest, self,
                                              pop_idv_index_orig, indiv_index,
                                              Population.GEN_METHOD_REPLICATION)
                    mlctable.get_individual(new_pop.get_individuals()[pop_idv_index_dest]).inc_appearences()
                    individuals_created += 1

                elif op == "mutation":
                    new_ind = None
                    fail = True
                    while fail:
                        pop_idv_index_orig = self._choose_individual(pop_subgen[i])
                        pop_idv_index_dest = not_valid_indexes[individuals_created]

                        lg.logger_.debug("[POPULATION] Mutation - Orig indiv {0} - Dest indiv {1}"
                                         .format(pop_idv_index_orig, pop_idv_index_dest))

                        indiv_index = self._individuals[pop_idv_index_orig]
                        old_indiv = MLCTable.get_instance().get_individual(indiv_index)
                        new_ind, fail = old_indiv.mutate()

                    number, repeated = MLCTable.get_instance().add_individual(new_ind)
                    new_pop.update_individual(pop_idv_index_dest, self,
                                              pop_idv_index_orig, number,
                                              Population.GEN_METHOD_MUTATION, -1)
                    mlctable.get_individual(new_pop.get_individuals()[pop_idv_index_dest]).inc_appearences()
                    individuals_created += 1

                elif op == "crossover":
                    # Boundaries are safe since the choose_op method only return crossover
                    # if there are enough individuals to be replaced
                    fail = True
                    new_ind = None
                    new_ind2 = None

                    while fail:
                        # We need to individuals for the crossover. Get two and check that they are not the same
                        pop_idv_index_orig = self._choose_individual(pop_subgen[i])
                        pop_idv_index_orig2 = pop_idv_index_orig
                        while pop_idv_index_orig == pop_idv_index_orig2:
                            pop_idv_index_orig2 = self._choose_individual(pop_subgen[i])

                        pop_idv_index_dest = not_valid_indexes[individuals_created]
                        pop_idv_index_dest2 = not_valid_indexes[individuals_created + 1]

                        lg.logger_.debug("[POPULATION] Crossover (Pair 1) - Orig indiv {0} - Dest indiv {1}"
                                         .format(pop_idv_index_orig, pop_idv_index_dest))
                        lg.logger_.debug("[POPULATION] Crossover (Pair 2) - Orig indiv {0} - Dest indiv {1}"
                                         .format(pop_idv_index_orig2, pop_idv_index_dest2))

                        # Get the two individuals involved and call the crossover function
                        indiv_index = self._individuals[pop_idv_index_orig]
                        old_indiv = MLCTable.get_instance().get_individual(indiv_index)
                        indiv_index2 = self._individuals[pop_idv_index_orig2]
                        old_indiv2 = MLCTable.get_instance().get_individual(indiv_index2)
                        new_ind, new_ind2, fail = old_indiv.crossover(old_indiv2)

                    number, repeated = MLCTable.get_instance().add_individual(new_ind)
                    new_pop.update_individual(pop_idv_index_dest, self,
                                              pop_idv_index_orig, number,
                                              Population.GEN_METHOD_CROSSOVER, -1)

                    number, repeated = MLCTable.get_instance().add_individual(new_ind2)
                    new_pop.update_individual(pop_idv_index_dest2, self,
                                              pop_idv_index_orig2, number,
                                              Population.GEN_METHOD_CROSSOVER, -1)
                    individuals_created += 2

        print new_pop.get_individuals()
        return new_pop

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

    @staticmethod
    def choose_genetic_operation(amount_indivs_left):
        prob_rep = Config.get_instance().getfloat("OPTIMIZATION", "probrep")
        prob_mut = Config.get_instance().getfloat("OPTIMIZATION", "probmut")
        prob_cro = Config.get_instance().getfloat("OPTIMIZATION", "probcro")

        if (prob_rep + prob_cro + prob_mut) != 1:
            # FIXME: This validation should be done at the beggining of the program
            lg.logger_.error("[POPULATION] Probabilities of genetic operations are not "
                             "equal to one. Please adjust and relaunch")
            sys.exit(-1)

        op = None
        rand_prob = MatlabEngine.rand()
        if amount_indivs_left < 2:
            # Crossover is not possible
            rand_prob *= (prob_rep + prob_mut)
            if rand_prob <= prob_rep:
                op = "replication"
            else:
                op = "mutation"
        else:
            if rand_prob <= prob_rep:
                op = "replication"
            elif rand_prob > prob_rep and (rand_prob <= (prob_mut + prob_rep)):
                op = "mutation"
            else:
                op = "crossover"

        return op

    def _choose_individual(self, subgen_range):
        selection_method = Config.get_instance().get("OPTIMIZATION", "selectionmethod")

        if selection_method == "tournament":
            tournament_size = Config.get_instance().getint("OPTIMIZATION", "tournamentsize")
            # Get randomly as many individuals as tournament_size property is set
            indivs_chosen = []
            subgen_len = subgen_range[1] - subgen_range[0] + 1

            # FIXME: What happen if the size of the tournament is greater
            # than the amount of individuals in the subgeneration?. Ask Thomas

            for i in range(tournament_size):
                # FIXME: This is soooo wrong. The individuals obtained will be always the ones
                # in the first subgeneration. That's because we are working with the length of the
                # subgeneration instead of the indexes
                random_indiv = -1
                while random_indiv == -1 or random_indiv in indivs_chosen:
                    random_indiv = math.ceil(MatlabEngine.rand() * subgen_len) - 1
                indivs_chosen.append(int(random_indiv))

            # Got the random indivs. Grab the one with the minor cost
            cost = 1e36
            indiv_chosen = None
            for index in indivs_chosen:
                if self._costs[index] < cost:
                    cost = self._costs[index]
                    indiv_chosen = index

            return indiv_chosen
        else:
            # FIXME: This validation must be done at the beginning of the program
            lg.logger_.error("[POPULATION] choose_individual: Invalid selection method."
                             "Correct it and relaunch the program.")
            sys.exit(-1)

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
