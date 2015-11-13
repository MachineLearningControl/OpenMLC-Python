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
    end
end