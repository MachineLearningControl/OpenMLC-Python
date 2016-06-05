classdef MLCpop < handle
    
    properties
        individuals
        costs
        gen_method
        parents
        state
        gen
        subgen
    end
    
    methods
        [obj,mlctable]=create(obj,mlc_parameters,mlctable);
        [obj2,mlctable]=evolve(obj,mlc_parameters,mlctable,mlcpop2);
  %      indexes=select(obj,mlc_parameters);
        [obj,mlctable]=evaluate(obj,mlctable,mlc_parameters,idx);
        obj=sort(obj,mlc_parameters);        
        [obj,idx]=remove_bad_indivs(obj,mlc_parameters);
        [obj]=remove_duplicates(obj);
        obj=remove_individual(obj,idx);
        op=choose_genetic_op(obj, mlc_parameters,n);

        % Constructor
        function obj=MLCpop(mlc_parameters,gen)
            if nargin<2
                gen=1;
            end
            obj.gen=gen;
            if mod(gen,mlc_parameters.cascade(2))==0
                obj.subgen=1;
            else
                obj.subgen=mlc_parameters.cascade(1);
            end
            if length(mlc_parameters.size)>1 && gen>1
                gensize=mlc_parameters.size(2);
            else
                gensize=mlc_parameters.size(1);
            end    
            obj.individuals=zeros(1,gensize)-1;
            obj.costs=zeros(1,gensize)-1;
            obj.gen_method=zeros(1,gensize)-1;
            obj.parents=cell(1,gensize);
            obj.state='init';
        end

        % FOR PYTHON COMPATIBILITY ONLY
        function obj=set_individuals(obj, individuals)
            obj.individuals = individuals;
        end

        % Helper methods
        function obj=set_state(obj,new_state)
            obj.state = new_state;
        end

        % Helper methods
        function obj=set_cost(obj, index, cost)
            obj.costs(index) = cost;
        end

        function obj=dump(obj)
            obj.individuals
            obj.costs
        end

        function obj=print_individual(obj, individual_id)
            fprintf('Ind id : %d', individual_id)
            fprintf('   COST %d', obj.costs(individual_id));
            fprintf('   GEN_METHOD %d', obj.gen_method(individual_id));
            fprintf('   PARENT %d', obj.parents{individual_id});
            fprintf('\n')
        end

        function obj=set_individual(obj, individual_id, individual)
            obj.individuals(individual_id) = individual;
        end

        function individual=get_individual(obj, individual_id)
            individual = obj.individuals(individual_id);
        end

        function cost=get_cost(obj, individual_id)
            cost = obj.costs(individual_id);
        end

        function obj=set_parent(obj, individual_id, parent)
            obj.parents{individual_id} = parent;
        end

        function parent=get_parent(obj, individual_id)
            parent = obj.parents{individual_id};
        end

        function obj=set_gen_method(obj, individual_id, gen_method)
            obj.gen_method(individual_id) = gen_method;
        end

        function gen=get_gen(obj)
            gen = obj.gen;
        end

        function subgen=get_subgen(obj)
            subgen = obj.subgen;
        end

        function op=choose_genetic_operation(obj,mlc_parameters,n)
            op = choose_genetic_op(mlc_parameters,n);
        end

        function idv_orig=choose_individual_(mlcpop, mlc_parameters, idx_source_pool)
            idv_orig = mlcpop.choose_individual(mlc_parameters, idx_source_pool);
        end

        function idxsubgen=init_generation(mlcpop, idxsubgen2, i)
            idxsubgen2{i}=idxsubgen2{i}(mlcpop.individuals(idxsubgen2{i})==-1);
            idxsubgen = idxsubgen2;
        end
    end
end
        
    