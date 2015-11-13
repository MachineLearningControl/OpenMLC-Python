function [mlcpop]=remove_duplicates(mlcpop)
    idx_to_remove=find_duplicates(mlcpop.individuals);
    fprintf('%i individuals to remove\n',length(idx_to_remove));
    mlcpop.remove_individual(idx_to_remove);
        