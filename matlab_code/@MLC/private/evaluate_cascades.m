function mlc=evaluate_cascades(mlc,~)
%PARETO_SORT    Hidden Method of the MLC class. This splits the population
%  into several cascades (determined by parameters.no_of_cascades) which are
%  evolved indipendent from each other for a given number of generations
%  (parameters.no_of_gen_per_cascade)
%   MLC_OBJ.EVALUATE_CASCADES can not be called by user. 
%
%   All options are set in the MLC object (See <a href="matlab:help MLC">MLC</a>). 
%
%   Implemented: - Pareto aware sorting
%
%   See also MLC, EVALUATE_POPULATION
%
%   Copyright (C) 2014 Kai von Krbek (Kai.von.Krbek@krbek.de)
%   This file is part of the TUCOROM MLC Toolbox

noc  = mlc.parameters.no_of_cascades;
nogc = mlc.parameters.no_of_gen_per_cascade;
ngen = length(mlc.population);                                          %% number of current generation
nind = length(mlc.population(ngen).individuals);                        %% number of individuals
verb = mlc.parameters.verbose;

%% Randomize the population for the cascading
idx = randperm(nind);
mlc.population(ngen).individuals  = mlc.population(ngen).individuals(idx);
mlc.population(ngen).fitnesses    = mlc.population(ngen).fitnesses(idx);
mlc.population(ngen).occurence    = mlc.population(ngen).occurence(idx);
mlc.population(ngen).generatedfrom= mlc.population(ngen).generatedfrom(idx);
mlc.population(ngen).selected     = mlc.population(ngen).selected(idx);
if strcmp(mlc.parameters.selectionmethod,'pareto')
   mlc.population(ngen).complexity= mlc.population(ngen).complexity(idx);
end

% The parameters will be overwritten, since it is not a copy but a
% reference mlcint.parameters=mlc.parameters
size=mlc.parameters.size;
elitism=mlc.parameters.elitism;
archive_size=mlc.parameters.archive_size;

cascade_population = floor(nind/noc);
if verb>1; fprintf('Evaluating cascades for generation \n',ngen); end
for i=1:noc
    if verb>1; fprintf('Evaluating cascade no. %i \n',i); end
    
    if i<noc
        idx = (i-1)*cascade_population+1:i*cascade_population;
    else
        idx = (i-1)*cascade_population+1:nind;
    end
    if i==noc
        cascade_population = nind - (i-1)*cascade_population;
    end
    %Create internal MLC Handle and call the mlc function
    mlcint = MLC();
    mlcint.parameters = mlc.parameters;
    mlcint.parameters.size = cascade_population;
    mlcint.parameters.no_of_cascades = 0;
    mlcint.parameters.no_of_gen_per_cascade = 0;
    %mlcint.parameters.verbose = 0;
    % Not using an archive in the cascades evalutation:
    mlc.parameters.archive_size=0;
    % Elitism shan't be greater than 10% of the cascade population
    if strcmp(mlc.parameters.selectionmethod,'pareto') && elitism>0.1*cascade_population
        mlcint.parameters.elitism=floor(0.1*cascade_population);
    end  
    %Get subpopulation
    mlcint.population(1).individuals   = mlc.population(ngen).individuals(idx);
    mlcint.population(1).fitnesses     = mlc.population(ngen).fitnesses(idx);
    mlcint.population(1).occurence     = mlc.population(ngen).occurence(idx);
    mlcint.population(1).generatedfrom = mlc.population(ngen).generatedfrom(idx);
    mlcint.population(1).selected      = mlc.population(ngen).selected(idx);
    if strcmp(mlc.parameters.selectionmethod,'pareto')
        mlcint.population(1).complexity= mlc.population(ngen).complexity(idx);
    end
    mlcint.individual_table.individuals= cell(mlcint.parameters.size*mlcint.parameters.fgen,1);
    mlcint.individual_table.occurence  = zeros(mlcint.parameters.size*mlcint.parameters.fgen,1);
    mlcint.individual_table.fitnesses  = zeros(mlcint.parameters.size*mlcint.parameters.fgen,1);
    mlcint.individual_table.nb=0;
    
    
    %Evaluate for nogc generations:
    mlcint.go(nogc+1);
    %% Replace the old individuals by the new individuals
    % First inflate the not created individuals cascade_population size with the
    % standard dummy value -- Bullshit
    %if length(mlcint.population(nogc).individuals)<length(idx)
    %    mlcint=mlcint.evolve_population;    
    %end
    mlc.population(ngen).individuals(idx)   = mlcint.population(nogc+1).individuals;
    mlc.population(ngen).fitnesses(idx)     = mlcint.population(nogc+1).fitnesses;
    mlc.population(ngen).occurence(idx)     = mlcint.population(nogc+1).occurence;
    mlc.population(ngen).generatedfrom(idx) = mlcint.population(nogc+1).generatedfrom;
    %mlc.population(ngen).selected(idx)=mlcint.population(nogc).selected{:};
    if strcmp(mlc.parameters.selectionmethod,'pareto')
        mlc.population(ngen).complexity(idx)= mlcint.population(nogc+1).complexity;
    end
    clear mlcint
end


% Restore initial parameters of mlc.
mlc.parameters.size=size;
mlc.parameters.no_of_cascades=noc;
mlc.parameters.no_of_gen_per_cascade=nogc;
mlc.parameters.elitism=elitism;
mlc.parameters.verbose=verb;
mlc.parameters.archive_size=archive_size;

end
