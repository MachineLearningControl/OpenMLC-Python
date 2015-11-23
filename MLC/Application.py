import matlab.engine
import numpy as np
import sys

from MLC.Log.log import logger
from MLC.Population.Population import Population


class Application(object):
    def __init__(self, eng, config):
        self._eng = eng
        # Parameters class like in Python
        self._config = config

        self._mlc = self._eng.eval('wmlc')
        self._params = self._eng.eval('wmlc.parameters')
        self._pop = None

        # print "Selection method: " + self.eng.eval("wparams.selectionmethod")

        # self.eng.workspace["wtable"] = self.table
        # print "Table number: " + self.eng.eval("wtable.number")

    def go(self, ngen, fig):
        # self.eng.go(self.mlc, generations, fig

        if ngen <= 0:
            logger.error('The amounts of generations must be a '
                         'positive decimal number. Value provided: ' + ngen)
            return

        # curgen=length(mlc.population);
        curgen = 0
        if curgen == 0:
            # population is empty, we have to create it
            curgen = 1
            self.generate_population(curgen)
            # self.eng.generate_population(self.mlc) #mlc.generate_population;

        while curgen <= ngen:
            # ok we can do something
            state = self._eng.get_population_state(self._mlc, curgen)
            if state == 'init':
                if curgen == 1:
                    self.generate_population(curgen)
                    # self.eng.generate_population(self.mlc)
                else:
                    self.evolve_population()
                    # self.eng.evolve_population(self.mlc)

            elif state == 'created':
                # self._eng.evaluate_population(self._mlc, curgen)
                self.evaluate_population()

            elif state == 'evaluated':
                curgen += 1

                if fig > 0:
                    self._eng.show_best(self._mlc)

                # if (fig>1):
                    # self.eng.show_convergence(self.mlc)

                if curgen <= ngen:
                    self.evolve_population()
                    # self.eng.evolve_population(self.mlc)

    def generate_population(self, gen_number):
        population = self._eng.MLCpop(self._params)
        self._pop = Population(self._eng, self._config)

        self._eng.workspace["wpopulation"] = population
        print self._eng.eval("wpopulation.state")

        self._pop.create()
        # Table created inside population create
        self._eng.set_table(self._mlc, self._eng.eval('wtable'))

        matlab_array = matlab.double(self._pop.get_individuals().tolist())
        self._eng.set_individuals(population,
                                  matlab_array,
                                  nargout=0)

        self._eng.set_state(population, 'created')
        logger.debug('[EV_POP] ' + self._eng.eval("wpopulation.state"))

        self._eng.add_population(self._mlc, population, gen_number)

        # mlc.population=MLCpop(mlc.parameters);
        # [mlc.population(1),mlc.table]=mlc.population.create(mlc.parameters);

    def evaluate_population(self):
        params = self._eng.eval('wmlc.parameters')
        table = self._eng.eval('wmlc.table')

        # First evaluation
        pop_index = int(self._eng.eval('length(wmlc.population)'))
        string_pop = 'wmlc.population(' + str(pop_index) + ')'
        actual_pop = self._eng.eval(string_pop)

        indiv_len = int(self._eng.eval('length(' + string_pop + '.individuals)'))
        idx = matlab.int32(np.arange(1, indiv_len + 1).tolist())
        self._eng.evaluate(actual_pop, table, params, idx)

        # Remove bad individuals
        elim = False
        bad_values = self._config.get('EVALUATOR', 'badvalues_elim')
        if bad_values == 'all':
            elim = True
        elif bad_values == 'first':
            if pop_index == 1:
                elim = True

        if elim:
            ret = self._eng.remove_bad_indivs(actual_pop, params, nargout=2)
            while len(ret[1]):
                # There are bad individuals, recreate the population
                self._pop.create()
                self._eng.evaluate(actual_pop, table, params, idx)
                ret = self._eng.remove_bad_indivs(actual_pop, params, nargout=2)

        self._eng.sort(actual_pop, params)

        # Enforce reevaluation
        if self._config.getboolean('EVALUATOR', 'ev_again_best'):
            # TODO: In this iteration, this code is not executed. Code it later
            logger.error("[EV_POP] Code not generated yet. " +
                         "This shouldn't be executed")
            sys.exit(-1)

        self._eng.set_state(actual_pop, 'evaluated')

    def evolve_population(self):
        n = self._eng.get_current_generation(self._mlc)
        current_pop = self._eng.get_population(self._mlc, n)

        next_pop = self._eng.MLCpop(self._params)
        table = self._eng.eval('wmlc.table')
        self._eng.evolve(current_pop, self._params, table, next_pop)

        self._eng.set_state(next_pop, 'created')
        self._eng.add_population(self._mlc, next_pop, n + 1)
