classdef MLCtable < handle
    properties
        individuals
        hashlist
        costlist
        number
    end
    
    methods
        [obj,number,already_exist]=add_individual(obj,mlcind)
        idx=find_individual(obj,mlcind)
        obj=update_individual(obj,idx,J);
  
        function obj=MLCtable(Nind)
            if nargin<1
                Nind=50*1000;
            end
            ind=MLCind;
            obj.individuals=repmat(ind,[1,Nind]);
            obj.hashlist=zeros(1,Nind);
            obj.costlist=zeros(1,Nind);
            obj.number=0;
        end

        function obj=print_indivs(obj)
            for i=1:obj.number
                fprintf('INDIVIDUAL N#%d - Cost: %f\n', i, obj.individuals(i).cost);
            end
        end

        function obj=print_formal(obj)
            for i=1:obj.number
                fprintf('INDIVIDUAL N#%d - Value: %f\n', i, obj.individuals(i).value);
            end
        end

        function individual=get_individual(obj, individual_id)
            individual = obj.individuals(individual_id);
        end
    end
end