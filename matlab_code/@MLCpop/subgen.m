function idxsubgen=subgen(mlcpop,mlc_parameters)
    nsubgen=mlcpop.subgen;
%% determination of subpopulation composition
    nind=length(mlcpop.individuals);
    nindsub=floor(nind/nsubgen);
    idxstart=1;
    i=1;
    idxsubgen=cell(1,nsubgen);
    while i<nsubgen;
        
        idxsubgen{i}=[idxstart:idxstart-1+nindsub];
        idxstart=idxsubgen{i}(end)+1;
        i=i+1;
    end
    idxsubgen{i}=[idxstart:nind];