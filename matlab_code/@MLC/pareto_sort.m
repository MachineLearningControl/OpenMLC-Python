function mlc=pareto_sort(mlc,~)
%PARETO_SORT    Hidden Method of the MLC class. Sorts population
% according to the pareto paradigm, with the pareto best individuals first,
% the other individuals are sorted according to their fitness.
%   MLC_OBJ.PARETO_SORT can not be called by user. 
%
%   All options are set in the MLC object (See <a href="matlab:help MLC">MLC</a>). 
%
%   Implemented: - Pareto aware sorting
%
%   See also MLC, EVALUATE_POPULATION
%
%   Copyright (C) 2014 Kai von Krbek (Kai.von.Krbek@krbek.de)
%   This file is part of the TUCOROM MLC Toolbox

verb=mlc.parameters.verbose;
ngen=length(mlc.population);                                          %% number of current generation
nind=length(mlc.population(ngen).individuals);                        %% number of individuals

complexity = mlc.population(ngen).complexity(1);
mlc.population(ngen).pareto_best(1).individual = mlc.population(ngen).individuals(1);
mlc.population(ngen).pareto_best(1).complexity = mlc.population(ngen).complexity(1);
mlc.population(ngen).pareto_best(1).fitness    = mlc.population(ngen).fitnesses(1);

%% Using the fact that the population is already presorted by fitness
if verb>4
    fprintf('Pareto-aware sort taking place');
end

i=2;
j=2;
idx = 1:nind;
while complexity>= mlc.parameters.mindepth && j<nind
    if mlc.population(ngen).complexity(j) < complexity && mlc.population(ngen).fitnesses(j)<mlc.parameters.badvalue
        complexity = mlc.population(ngen).complexity(j);
        mlc.population(ngen).pareto_best(i).individual = mlc.population(ngen).individuals(j);
        mlc.population(ngen).pareto_best(i).complexity = mlc.population(ngen).complexity(j);
        mlc.population(ngen).pareto_best(i).fitness    = mlc.population(ngen).fitnesses(j);
        % exchange the values of i and j
        idx(i)=j;
        idx(j)=i;
        i=i+1;
    elseif mlc.population(ngen).fitnesses(j)>=mlc.parameters.badvalue
        j=nind-1;
    end
    j=j+1;
end
% Sort the not pareto optimal indeces by ascending fitness
[~,idx(i+1:nind)]=sort(idx(i+1:nind),'ascend');

%Apply new sorting
mlc.population(ngen).individuals=mlc.population(ngen).individuals(idx);
mlc.population(ngen).fitnesses=mlc.population(ngen).fitnesses(idx);
mlc.population(ngen).occurence=mlc.population(ngen).occurence(idx);
mlc.population(ngen).generatedfrom=mlc.population(ngen).generatedfrom(idx);
mlc.population(ngen).selected=mlc.population(ngen).selected(idx);
mlc.population(ngen).complexity=mlc.population(ngen).complexity(idx);


%% Redefine the elitism parameter that the pareto-best individuals will be carried on to the next generation
% Ensure that not more than 20% of the population are used for elitism.
if i>0.2*nind
    mlc.parameters.elitism=floor(0.2*nind);
else
    mlc.parameters.elitism=i; 
end    

end