function [mlcpop,idx]=remove_bad_indivs(mlcpop,mlc_parameters)
    idx=find(mlcpop.costs==mlc_parameters.badvalue);
    
    if length(idx)>0.4*length(mlcpop.individuals)
        fprintf('%i individuals to remove\n',length(idx));
        mlcpop.remove_individual(idx);
        idx=find(mlcpop.costs==-1);
    else
        idx=[];
    end
    