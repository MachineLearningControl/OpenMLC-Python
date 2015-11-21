from MLC.Log.log import logger
from MLC.Population import Population
import numpy as np
import matlab.engine

class Application(object):
    def __init__(self, eng, config):
        self._eng = eng
        # Parameters class like in Python
        self._config = config

        self._mlc = self._eng.eval('wmlc')
        self._params = self._eng.eval('wmlc.parameters')

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
                self._eng.evaluate_population(self._mlc)

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
        py_pop = Population(self._eng, self._config)

        self._eng.workspace["wpopulation"] = population
        print self._eng.eval("wpopulation.state")

        py_pop.create()
        # Table created inside population create
        self._eng.set_table(self._mlc, self._eng.eval('wtable'))

        matlab_array = matlab.double(py_pop.get_individuals().tolist())
        self._eng.set_individuals(population,
                                  matlab_array,
                                  nargout=0)

        self._eng.set_state(population, 'created')
        print self._eng.eval("wpopulation.state")

        self._eng.add_population(self._mlc, population, gen_number)

        # mlc.population=MLCpop(mlc.parameters);
        # [mlc.population(1),mlc.table]=mlc.population.create(mlc.parameters);

    def evolve_population(self):
        n = self._eng.get_current_generation(self._mlc)
        current_pop = self._eng.get_population(self._mlc, n)

        next_pop = self._eng.MLCpop(self._params)
        table = self._eng.eval('wmlc.table')
        self._eng.evolve(current_pop, self._params, table, next_pop)

        self._eng.set_state(next_pop, 'created')
        self._eng.add_population(self._mlc, next_pop, n + 1)

        '''
        self.eng.workspace["wparams"] = self.params
        if (self.eng.eval("wparams.lookforduplicates")):
            self.eng.remove_duplicates(next_pop)
            %% Remove duplicates

        if mlc.parameters.lookforduplicates
            mlc.population(n+1).remove_duplicates;
            idx=find(mlc.population(n+1).individuals==-1);
            while ~isempty(idx);
                [mlc.population(n+1),mlc.table]=mlc.population(n).evolve(mlc.parameters,mlc.table,mlc.population(n+1));
                mlc.population(n+1).remove_duplicates;
                idx=find(mlc.population(n+1).individuals==-1);
            end
        end
        mlc.population(n+1).state='created';
        '''