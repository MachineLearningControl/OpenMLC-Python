function mlcpop=remove_individual(mlcpop,idx_to_remove)
    mlcpop.individuals(idx_to_remove)=-1;
    mlcpop.costs(idx_to_remove)=-1;
    mlcpop.gen_method(idx_to_remove)=-1;
    mlcpop.parents(idx_to_remove)=cell(1,length(idx_to_remove));
    