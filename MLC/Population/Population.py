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
        self._gen_size = cascade[1] if (self._gen > 1 and len(size) > 1) else size[0]
        self._individuals = np.zeros(self._gen_size, dtype=int)
        self._state = 'init'

        lg.logger_.debug("Population created. Number: %s - Size: %s" % (self._gen, self._gen_size))

    def create(self, table=None):
        if table is None:
            self._eng.workspace['wtable'] = self._eng.MLCtable(self._gen_size * 50)

        gen_method = self._config.get_param('GP', 'generation_method')
        lg.logger_.info("Using %s to generate population" % gen_method)
        gen_creator = CreationFactory.make(self._eng, self._config, gen_method)
        gen_creator.create(self._gen_size)

        self.set_individuals(gen_creator.individuals())

    def evaluate(self, eval_idx):
        """
        Evaluates cost of individuals and update the MLC object MLC_OBJ. All options are set in the MLC object.
        Implemented:
            - evaluation with m-file function (standalone and multihread), external evaluation with file exchange.
            - detection of bad individuals (above a threshold) and their replacement.
            - evaluation or not of already evaluated individuals.
            - averaging of all past cost values for a given individual if evaluation are repeated (for experiments or
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

            if str(jj[index]) == 'nan' or str(jj[index]) == 'inf' or jj[index] > bad_value:
                lg.logger_.debug(   '[POP][EVALUATE] Individual N#: {0}. Invalid value found: {1}'.format(
                                    self._individuals[index],
                                    jj[index]))

                jj[index] = bad_value

            lg.logger_.debug(   '[POP][EVALUATE] Idx: {0} - Indiv N#: {1} - Cost: {2}'.format(
                                index, self._individuals[index], jj[index]))

            self._eng.update_individual(table, self._individuals[index], jj[index])
            self._eng.set_cost(matlab_pop, mlab_index, jj[index])

        self._costs = jj

    def remove_bad_individuals(self):
        bad_value = self._config.getfloat('EVALUATOR', 'badvalue')
        bad_list = [x for x in xrange(len(self._costs)) if self._costs[x] == bad_value]

        if len(bad_list) > 0.4 * len(self._individuals):
            lg.logger_.info('[POP][BAD_INDIVS] %s individuals will be removed.' % len(bad_list))
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
        return MatlabEngine.engine().eval('wmlc.population(' + str(generation_id) + ')')

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

        return MatlabEngine.engine().eval('wmlc.population(%s).individuals' % generation_id)

    @staticmethod
    def inc_pop_number():
        Population.amount_population += 1

    @staticmethod
    def get_actual_pop_number():
        return Population.amount_population

    @staticmethod
    def evolve(mlcpop, mlc_parameters, mlctable, mlcpop2=None):
        if mlcpop2 is None:
            return MatlabEngine.engine().evolve(mlcpop, mlc_parameters, mlctable, nargout=1)
        else:
            return MatlabEngine.engine().evolve(mlcpop, mlc_parameters, mlctable, mlcpop2, nargout=0)

    """
        ngen=mlcpop.gen;
        verb=mlc_parameters.verbose;
        if nargin<4
            mlcpop2=MLCpop(mlc_parameters,ngen+1);
        end
        if verb>0;fprintf('Evolving population\n');end
        idxsubgen=subgen(mlcpop,mlc_parameters);
        idxsubgen2=subgen(mlcpop2,mlc_parameters);

        for i=1:length(idxsubgen2);
            idxsubgen2{i}=idxsubgen2{i}(mlcpop2.individuals(idxsubgen2{i})==-1);
            if verb>0;fprintf('Evolving sub-population %i/%i\n',i,mlcpop2.subgen);end
            if length(idxsubgen)==1
                idx_source_pool=idxsubgen{1};
            else
                idx_source_pool=idxsubgen{i};
            end
            individuals_created=0;
            %% elitism
            if nargin < 4
                for i_el=1:ceil(mlc_parameters.elitism/length(idxsubgen2));
                    idv_orig=idx_source_pool(i_el);
                    idv_dest=idxsubgen2{i}(individuals_created+1);

                    % fprintf('ELITISM - IDV_ORIG: %d - IDV_DEST: %d \n', idv_orig, idv_dest);
                    mlcpop2.individuals(idv_dest)=mlcpop.individuals(idv_orig);
                    mlcpop2.costs(idv_dest)=mlcpop.costs(idv_orig);
                    mlcpop2.parents{idv_dest}=idv_orig;
                    mlcpop2.gen_method(idv_dest)=4;
                    mlctable.individuals(mlcpop.individuals(idv_orig)).appearences=mlctable.individuals(mlcpop.individuals(idv_orig)).appearences+1;
                    individuals_created=individuals_created+1;
                end
            end

            %% completing population
            while individuals_created<length(idxsubgen2{i})
                % fprintf('LEN idx_sub: %d\n', length(idxsubgen2{i})-individuals_created');
                op=choose_genetic_op(mlc_parameters,length(idxsubgen2{i})-individuals_created);
                switch op
                    case 'replication'
                        idv_orig=choose_individual(mlcpop,mlc_parameters,idx_source_pool);
                        idv_dest=idxsubgen2{i}(individuals_created+1);
                        % fprintf('REPLICATION - IDV_ORIG: %d - IDV_DEST: %d \n', idv_orig, idv_dest);
                        mlcpop2.individuals(idv_dest)=mlcpop.individuals(idv_orig);
                        mlcpop2.costs(idv_dest)=mlcpop.costs(idv_orig);
                        mlcpop2.parents{idv_dest}=idv_orig;
                        mlcpop2.gen_method(idv_dest)=1;
                        mlctable.individuals(mlcpop.individuals(idv_orig)).appearences=mlctable.individuals(mlcpop.individuals(idv_orig)).appearences+1;
                        individuals_created=individuals_created+1;

                    case 'mutation'
                        fail=1;
                        while fail==1
                            idv_orig=choose_individual(mlcpop,mlc_parameters,idx_source_pool);
                            idv_dest=idxsubgen2{i}(individuals_created+1);
                            % fprintf('MUTATION - IDV_ORIG: %d - IDV_DEST: %d \n', idv_orig, idv_dest);
                            old_ind=mlctable.individuals(mlcpop.individuals(idv_orig));
                            [new_ind,fail]=old_ind.mutate(mlc_parameters);
                        end
                        [mlctable,number]=add_individual(mlctable,new_ind);
                        mlcpop2.individuals(idv_dest)=number;
                        mlcpop2.costs(idv_dest)=-1;
                        mlcpop2.parents{idv_dest}=idv_orig;
                        mlcpop2.gen_method(idv_dest)=2;
                        mlctable.individuals(number).appearences=mlctable.individuals(number).appearences+1;
                        individuals_created=individuals_created+1;

                    case 'crossover'
                        fail=1;
                        while fail==1
                            idv_orig=choose_individual(mlcpop,mlc_parameters,idx_source_pool);
                            idv_orig2=idv_orig;
                            while idv_orig2==idv_orig;
                                idv_orig2=choose_individual(mlcpop,mlc_parameters,idx_source_pool);
                            end
                            idv_dest=idxsubgen2{i}(individuals_created+1);
                            idv_dest2=idxsubgen2{i}(individuals_created+2);
                            % fprintf('CROSSOVER - IDV_ORIG 1 : %d - IDV_DEST 1 : %d - IDV_ORIG 2 : %d - IDV_DEST 2 : %d\n', idv_orig, idv_dest, idv_orig2, idv_dest2);
                            old_ind=mlctable.individuals(mlcpop.individuals(idv_orig));
                            old_ind2=mlctable.individuals(mlcpop.individuals(idv_orig2));
                            [new_ind,new_ind2,fail]=old_ind.crossover(old_ind2,mlc_parameters);
                        end

                        [mlctable,number]=add_individual(mlctable,new_ind);
                        mlcpop2.individuals(idv_dest)=number;
                        mlcpop2.costs(idv_dest)=-1;
                        mlcpop2.parents{idv_dest}=[idv_orig idv_orig2];
                        mlcpop2.gen_method(idv_dest)=3;
                        mlctable.individuals(number).appearences=mlctable.individuals(number).appearences+1;
                        individuals_created=individuals_created+1;

                        [mlctable,number2]=add_individual(mlctable,new_ind2);
                        mlcpop2.individuals(idv_dest2)=number2;
                        mlcpop2.costs(idv_dest2)=-1;
                        mlcpop2.parents{idv_dest2}=[idv_orig idv_orig2];
                        mlcpop2.gen_method(idv_dest2)=3;
                        mlctable.individuals(number2).appearences=mlctable.individuals(number2).appearences+1;
                        individuals_created=individuals_created+1;
                end
            end
        end
    """