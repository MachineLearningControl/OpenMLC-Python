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

        % Helper methods
        function obj=set_state(obj,new_state)
            obj.state = new_state;
        end
    end
end
        
    