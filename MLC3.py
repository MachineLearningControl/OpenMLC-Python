        #mlc.population(1).state='created';
import matlab.engine

from MLCpop import MLCpop

class MLC3(object):

    def __init__(self, configFile):
        self.eng = matlab.engine.start_matlab()
        # Add path
        self.eng.addpath("./matlab_code")
        self.eng.addpath("./matlab_code/MLC_tools")
        self.eng.addpath("./matlab_code/MLC_tools/Demo")

        self.mlc = self.eng.MLC2()
        self.params = self.eng.get_params(self.mlc)

        self.eng.workspace["wparams"] = self.params
        self.table = self.eng.MLCtable(self.eng.eval("wparams.size")*50)
        self.eng.set_table(self.mlc,self.table)

        #print "Selection method: " + self.eng.eval("wparams.selectionmethod")

        #self.eng.workspace["wtable"] = self.table
        #print "Table number: " + self.eng.eval("wtable.number")


    def go(self, ngen, fig):
        #self.eng.go(self.mlc, generations, fig

        if (ngen<=0):
            print('Once you tell me how I can compute %f generations, I''ll consider doing it\n',ngen)
            print('Please provide an integer, stupid!\n')
            return

        #curgen=length(mlc.population);
        curgen=0
        if (curgen==0): #%% population is empty, we have to create it
            self.generate_population()
            #self.eng.generate_population(self.mlc) #mlc.generate_population;
            curgen=1

        while (curgen<=ngen): #%% ok we can do something
            state = self.eng.get_population_state(self.mlc,curgen)
            if (state == 'init'):
                 if (curgen==1):
                     self.generate_population()
                     #self.eng.generate_population(self.mlc)
                 else:
                     self.evolve_population()
                     #self.eng.evolve_population(self.mlc)

            elif (state == 'created'):
                self.eng.evaluate_population(self.mlc)

            elif (state == 'evaluated'):
                curgen=curgen+1

                if (fig>0):
                    self.eng.show_best(self.mlc)

                if (fig>1):
                    self.eng.show_convergence(self.mlc)

                if (curgen<=ngen):
                    self.eng.show_best(self.mlc)
                    self.evolve_population()
                    #self.eng.evolve_population(self.mlc)

    def generate_population(self):

        %pop = MLCpop(self.params)

        population = self.eng.MLCpop(self.params)
        self.eng.workspace["wpopulation"] = population
        print self.eng.eval("wpopulation.state")

        self.eng.create(population, self.params, self.table)
        self.eng.set_state(population, 'created')
        print self.eng.eval("wpopulation.state")
        self.eng.add_initial_population(self.mlc,population)

        #mlc.population=MLCpop(mlc.parameters);
        #[mlc.population(1),mlc.table]=mlc.population.create(mlc.parameters);


    def evolve_population(self):

        n=self.eng.get_current_gen(self.mlc)

        currentPopulation = self.eng.get_population(self.mlc,n)

        nextPopulation = self.eng.MLCpop(self.params)
        self.eng.evolve(currentPopulation,self.params,self.table,nextPopulation)
        #[mlc.population(n+1),mlc.table]=mlc.population(n).evolve(mlc.parameters,mlc.table);

        '''
        self.eng.workspace["wparams"] = self.params
        if (self.eng.eval("wparams.lookforduplicates")):
            self.eng.remove_duplicates(nextPopulation)
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
