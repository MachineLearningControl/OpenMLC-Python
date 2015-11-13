function [mlctable,number,already_exist]=add_individual(mlctable,mlcind);
    idx=find_individual(mlctable,mlcind);
    if isempty(idx)
        mlctable.individuals(mlctable.number+1)=mlcind;
        mlctable.hashlist(mlctable.number+1)=mlcind.hash;
        mlctable.number=mlctable.number+1;
        number=mlctable.number;
        already_exist=0;
    else
        number=idx;
        already_exist=1;
    end
        
end