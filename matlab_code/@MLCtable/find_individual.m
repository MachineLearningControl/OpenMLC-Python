function index=find_individual(mlctable,mlcind);
    index=[];
    idx=find(mlctable.hashlist==mlcind.hash);
    if ~isempty(idx);
        for i=1:length(idx)
            if mlcind.compare(mlctable.individuals(idx))
                index=idx;
                break
            end
        end
    end
            