import math
import MLC.Log.log as lg
import sys

from MLC.Common.RandomManager import RandomManager
from MLC.individual.Individual import OperationOverIndividualFail
from MLC.mlc_table.MLCTable import MLCTable
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Population.Evaluation.EvaluatorFactory import EvaluatorFactory
from MLC.Simulation import Simulation


class Population(object):
    GEN_METHOD_REPLICATION = 1
    GEN_METHOD_MUTATION = 2
    GEN_METHOD_CROSSOVER = 3
    GEN_METHOD_ELITISM = 4

    def __init__(self, size, sub_generations, gen):
        self._config = Config.get_instance()

        self._gen = gen
        self._size = size
        self._subgen = sub_generations

        # Declare MATLAB attributes
        self._individuals = [-1] * self._size
        self._costs = [-1] * self._size
        self._gen_method = [-1] * self._size
        self._parents = [[]] * self._size

        # lg.logger_.debug("Population created. Number: %s - Size: %s" % (self._gen, self._size))

    @staticmethod
    def gen_method_description(method_type):
        gen_method = ["REPLICATION", "MUTATION", "CROSSOVER", "ELITISM"]
        try:
            return gen_method[method_type - 1]
        except IndexError:
            return "ERROR"

    def is_complete(self):
        return -1 not in self._individuals

    def fill(self, gen_creator):
        gen_creator.create(self._size)
        self.set_individuals(gen_creator.individuals())

    def evaluate(self, evaluator):
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
        # Update table individuals and MATLAB Population indexes and costs
        bad_value = self._config.getfloat('EVALUATOR', 'badvalue')
        costs = evaluator.evaluate(self._individuals)

        for i in xrange(self._size):
            new_cost = costs[i]

            if new_cost > bad_value or str(new_cost) in ('nan', 'inf'):
                lg.logger_.debug('Evaluate, invalid value found:%s for individual:%s' % (self._individuals[i], new_cost))
                new_cost = costs[i] = bad_value

            lg.logger_.debug('Evaluate Idx: %s - Indiv N#: %s - Cost: %s' % (i, self._individuals[i], new_cost))

            if new_cost != self._costs[i]:
                MLCTable.get_instance().update_individual(self._individuals[i], new_cost)

        self._costs = costs

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
                self._remove_individual(indexes[i + 1])
            i += 1

        lg.logger_.info("[POPULATION] Duplicated Individuals removed: " + str(amount_indivs_removed))
        return amount_indivs_removed

    def _remove_individual(self, index):
        self._individuals[index] = -1
        self._costs[index] = -1
        self._gen_method[index] = -1
        self._parents[index] = []

    def update_individual(self, *a, **kw):
        """
        Replace one individual with another.
        dest_index: Index of the individual in the population container
        rhs_pop: Population used to evolve the present Population
        parent_index: Individual index of the parent of the individual
        parent_index_2: In case of crossover, the second parent of the individual
        indiv_index: Index in the Individuals container of the individual
        gen_method: Generation method used to create the individual. Could be one of the following:
            GEN_METHOD_REPLICATION = 1
            GEN_METHOD_MUTATION = 2
            GEN_METHOD_CROSSOVER = 3
            GEN_METHOD_ELITISM = 4
        cost: Cost asociated with the individual. If the cost is not included in the function,
        the program assumes the individual will have the ssame cost than it's father
        """
        self._individuals[kw['dest_index']] = kw['indiv_index']
        if not 'cost' in kw:
            self._costs[kw['dest_index']] = kw['rhs_pop'].get_costs()[kw['parent_index']]
        else:
            self._costs[kw['dest_index']] = kw['cost']
        self._gen_method[kw['dest_index']] = kw['gen_method']

        if kw['gen_method'] == Population.GEN_METHOD_CROSSOVER:
            self._parents[kw['dest_index']] = [kw['parent_index'] + 1, kw['parent_index_2'] + 1]
        else:
            self._parents[kw['dest_index']] = [kw['parent_index'] + 1]

    def get_best_index(self):
        """
        Return the index of the best individual
        """
        best_indivs = [x[0] for x in sorted(enumerate(self._costs), key=lambda x:x[1])]
        return self._individuals[best_indivs[0]]

    def get_best_individual(self):
        return MLCTable.get_instance().get_individual(self.get_best_index())

    def evolve(self, mlcpop2=None):
        mlctable = MLCTable.get_instance()

        new_pop = mlcpop2
        if new_pop is None:
            new_pop = Simulation.create_empty_population_for(generation=self._gen + 1)

        lg.logger_.info('Evolving population N#' + str(self._gen))

        # FIXME: It's not necessary to compute the creation of both subgenerations
        # The ranges of both of them will be the same
        pop_subgen = self.create_subgen()
        pop_subgen2 = new_pop.create_subgen()
        subgen_amount = len(pop_subgen)

        for i in range(len(pop_subgen)):
            lg.logger_.info("Evolving subpopulation {0}/{1} of population N#{2}".format(i + 1, subgen_amount, str(self._gen)))
            # Get the indexes of the non valid elements in this subpopulation
            subgen_begin = pop_subgen[i][0]
            subgen_end = pop_subgen[i][1]

            subgen2_begin = pop_subgen2[i][0]
            subgen2_end = pop_subgen2[i][1]

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

                        indiv_index = self._individuals[pop_idv_index_orig]
                        lg.logger_.info("Individual {0}/{1}: Elitism - Orig indiv {2} - Dest indiv {3}"
                                        .format(individuals_created + 1, len(not_valid_indexes),
                                                indiv_index, pop_idv_index_dest + 1))

                        # Update the individual in the new population with the first param_elitism
                        new_pop.update_individual(dest_index=pop_idv_index_dest, rhs_pop=self,
                                                  parent_index=pop_idv_index_orig, indiv_index=indiv_index,
                                                  gen_method=Population.GEN_METHOD_ELITISM)

                        mlctable.get_individual(new_pop.get_individuals()[pop_idv_index_dest]).inc_appearences()
                        individuals_created += 1
                except IndexError:
                    lg.logger_.error("[POPULATION] Elitism - More individuals to replace than empty ones."
                                     "Stop elitism algorithm")

            # completing population
            indivs_to_be_completed = len(not_valid_indexes)
            lg.logger_.info("Elitism finished, number of Individuals to be completed: " + str(indivs_to_be_completed))
            while individuals_created < indivs_to_be_completed:
                indivs_left = indivs_to_be_completed - individuals_created
                op = Population.choose_genetic_operation(indivs_left)
                # lg.logger_.info("[POPULATION] Indivs left in subgen {0}: {1} "
                #                 "- Operation chosen: {2}".format(i + 1, indivs_left, op))

                if op == "replication":
                    pop_idv_index_orig = self._choose_individual(pop_subgen[i])
                    pop_idv_index_dest = not_valid_indexes[individuals_created]

                    indiv_index = self._individuals[pop_idv_index_orig]
                    lg.logger_.info("Individual {0}/{1}: Replication - Orig indiv {2} - Dest indiv {3}"
                                    .format(individuals_created + 1, len(not_valid_indexes),
                                            indiv_index, pop_idv_index_dest + 1))

                    new_pop.update_individual(dest_index=pop_idv_index_dest, rhs_pop=self,
                                              parent_index=pop_idv_index_orig, indiv_index=indiv_index,
                                              gen_method=Population.GEN_METHOD_REPLICATION)

                    mlctable.get_individual(new_pop.get_individuals()[pop_idv_index_dest]).inc_appearences()
                    individuals_created += 1

                elif op == "mutation":
                    new_ind = None
                    while new_ind is None:
                        try:
                            pop_idv_index_orig = self._choose_individual(pop_subgen[i])
                            pop_idv_index_dest = not_valid_indexes[individuals_created]

                            indiv_index = self._individuals[pop_idv_index_orig]
                            lg.logger_.info("Individual {0}/{1}: Mutation - Orig indiv {2} - Dest indiv {3}"
                                             .format(individuals_created+1, len(not_valid_indexes),
                                                     indiv_index, pop_idv_index_dest + 1))

                            old_indiv = MLCTable.get_instance().get_individual(indiv_index)
                            new_ind = old_indiv.mutate()

                        except OperationOverIndividualFail, ex:
                            pass

                    number, repeated = MLCTable.get_instance().add_individual(new_ind)
                    new_pop.update_individual(dest_index=pop_idv_index_dest, rhs_pop=self,
                                              parent_index=pop_idv_index_orig, indiv_index=number,
                                              gen_method=Population.GEN_METHOD_MUTATION, cost=-1)
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

                        indiv_index = self._individuals[pop_idv_index_orig]
                        indiv_index2 = self._individuals[pop_idv_index_orig2]
                        lg.logger_.info("Individual {0}/{1}: Crossover (Pair 1) - Orig indiv {2} - Dest index {3} - "
                                        "Crossover (Pair 2) - Orig indiv {4} - Dest index {5}"
                                        .format(individuals_created + 1, len(not_valid_indexes),
                                                indiv_index, pop_idv_index_dest + 1,
                                                indiv_index2, pop_idv_index_dest2 + 1))

                        # Get the two individuals involved and call the crossover function
                        old_indiv = MLCTable.get_instance().get_individual(indiv_index)
                        old_indiv2 = MLCTable.get_instance().get_individual(indiv_index2)
                        try:
                            new_ind, new_ind2 = old_indiv.crossover(old_indiv2)
                            fail = False
                        except OperationOverIndividualFail, ex:
                            lg.logger_.debug(str(ex))

                    number, repeated = MLCTable.get_instance().add_individual(new_ind)
                    new_pop.update_individual(dest_index=pop_idv_index_dest, rhs_pop=self,
                                              parent_index=pop_idv_index_orig, parent_index_2=pop_idv_index_orig2,
                                              indiv_index=number, cost=-1,
                                              gen_method=Population.GEN_METHOD_CROSSOVER)

                    number, repeated = MLCTable.get_instance().add_individual(new_ind2)
                    new_pop.update_individual(dest_index=pop_idv_index_dest2, rhs_pop=self,
                                              parent_index=pop_idv_index_orig, parent_index_2=pop_idv_index_orig2,
                                              indiv_index=number, cost=-1,
                                              gen_method=Population.GEN_METHOD_CROSSOVER)
                    individuals_created += 2

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
        rand_prob = RandomManager.rand()
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
                    random_indiv = math.ceil(RandomManager.rand() * subgen_len) - 1
                indivs_chosen.append(int(random_indiv))

            # Got the random indivs. Grab the one with the minor cost
            cost = float('inf')
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

    def get_size(self):
        return self._size

    def get_individuals(self):
        return self._individuals

    def set_individuals(self, indiv_list):
        for x in indiv_list:
            self._individuals[x[0]] = int(x[1])

    def get_costs(self):
        return self._costs

    def get_gen_methods(self):
        return self._gen_method

    def get_parents(self):
        return self._parents
