function show_best_indiv(mlc,ngen)

if mlc.parameters.show_best
    if nargin<2
    ngen=length(mlc.population);
    end
    if min(mlc.population(ngen).fitnesses)==-1
        ngen=ngen-1;
    end
    [~,k]=min(mlc.population(ngen).fitnesses);
    figure(999)
    eval([mlc.parameters.evaluation_function '(mlc.population(ngen).individuals{k},mlc.parameters,1,1);']);
end
