import matlab.engine
import numpy as np

import MLC.Log.log as lg
from MLC.Log.log import set_logger
from MLC.Population.Population import Population


class Application(object):
    def __init__(self, eng, config, log_mode='default'):
        self._eng = eng
        # Parameters class like in Python
        self._config = config

        # Set logger mode of the App
        set_logger(log_mode)

        self._mlc = self._eng.eval('wmlc')
        self._params = self._eng.eval('wmlc.parameters')
        self._pop = None

        # print "Selection method: " + self.eng.eval("wparams.selectionmethod")

        # self.eng.workspace["wtable"] = self.table
        # print "Table number: " + self.eng.eval("wtable.number")

    def go(self, ngen, fig):
        # self.eng.go(self.mlc, generations, fig

        if ngen <= 0:
            lg.logger_.error('The amounts of generations must be a '
                             'positive decimal number. Value provided: ' + ngen)
            return

        # curgen=length(mlc.population);
        if Population.get_actual_pop_number() == 0:
            # population is empty, we have to create it
            Population.inc_pop_number()
            self.generate_population()
            # self.eng.generate_population(self.mlc) #mlc.generate_population;

        while Population.get_actual_pop_number() <= ngen:
            # ok we can do something
            state = self._eng.get_population_state(self._mlc,
                                                   Population.
                                                   get_actual_pop_number())
            if state == 'init':
                if Population.get_actual_pop_number() == 1:
                    self.generate_population()
                else:
                    self.evolve_population()

            elif state == 'created':
                self.evaluate_population()

            elif state == 'evaluated':
                if fig > 0:
                    self._eng.show_best(self._mlc)

                # if (fig > 1):
                #    self.eng.show_convergence(self.mlc)

                if Population.get_actual_pop_number() <= ngen:
                    self.evolve_population()

    def generate_population(self):
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
        lg.logger_.debug('[EV_POP] ' + self._eng.eval("wpopulation.state"))

        self._eng.add_population(self._mlc, population,
                                 Population.get_actual_pop_number())

    def evaluate_population(self):
        params = self._eng.eval('wmlc.parameters')
        table = self._eng.eval('wmlc.table')

        # First evaluation
        pop_index = int(self._eng.eval('length(wmlc.population)'))
        string_pop = 'wmlc.population(' + str(pop_index) + ')'
        actual_pop = self._eng.eval(string_pop)

        # indiv_len = \
        #     int(self._eng.eval('length(' + string_pop + '.individuals)'))
        # idx = matlab.int32(np.arange(1, indiv_len + 1).tolist())
        # self._eng.evaluate(actual_pop, table, params, idx)
        self._pop.evaluate()

        # Remove bad individuals
        elim = False
        bad_values = self._config.get('EVALUATOR', 'badvalues_elim')
        if bad_values == 'all':
            elim = True
        elif bad_values == 'first':
            if pop_index == 1:
                elim = True

        if elim:
            ret = self._pop.remove_bad_individuals()
            while ret:
                # There are bad individuals, recreate the population
                self._pop.create()
                self._pop.evaluate()
                ret = self._pop.remove_bad_individuals()

        self._eng.sort(actual_pop, params)

        # Enforce reevaluation
        if self._config.getboolean('EVALUATOR', 'ev_again_best'):
            ev_again_times = self._config.getint('EVALUATOR', 'ev_again_times')
            for i in range(1, ev_again_times):
                ev_again_nb = self._config.getint('EVALUATOR', 'ev_again_nb')
                idx = matlab.int32(np.arange(1, ev_again_nb + 1).tolist())
                self._eng.evaluate(actual_pop, table, params, idx)
                self._eng.sort(actual_pop, params)

        self._eng.set_state(actual_pop, 'evaluated')

    def evolve_population(self):
        # Evolve the current population and add it to the MLC MATLAB object
        n = self._eng.eval('length(wmlc.population)')
        table = self._eng.eval('wmlc.table')
        current_pop = self._eng.eval('wmlc.population(' + str(n) + ')')

        next_pop = self._eng.evolve(current_pop, self._params, table, nargout=1)

        # Increase both counters. MATLAB and Python pops counters
        n += 1
        Population.inc_pop_number()

        self._eng.add_population(self._eng.eval('wmlc'), next_pop, n)

        # Remove duplicates
        look_for_dup = self._config.getboolean('OPTIMIZATION',
                                               'lookforduplicates')

        if look_for_dup:
            self._eng.remove_duplicates(next_pop)
            indivs = self._eng.eval(
                'wmlc.population(' + str(n) + ').individuals')

            nulls = []
            for idx in xrange(len(indivs[0])):
                if indivs[0][idx] == -1:
                    nulls.append(idx + 1)

            while len(nulls):
                self._eng.evolve(current_pop, self._params,
                                 table, next_pop, nargout=0)
                self._eng.remove_duplicates(next_pop)
                indivs = self._eng.eval(
                    'wmlc.population(' + str(n) + ').individuals')

                nulls = []
                for idx in xrange(len(indivs[0])):
                    if indivs[0][idx] == -1:
                        nulls.append(idx + 1)

            self._eng.set_state(next_pop, 'created')
            self._set_pop_new_individuals()

    def _set_pop_new_individuals(self):
        next_gen = Population.get_actual_pop_number()
        indivs = \
            self._eng.eval('wmlc.population(' + str(next_gen) + ').individuals')

        # Create a new population with the indexes updated
        self._pop = Population(self._eng,
                               self._config,
                               Population.get_actual_pop_number())

        self._pop.set_individuals(
            [(x, indivs[0][x]) for x in xrange(len(indivs[0]))])
