function mlc=evolve_population(mlc,i)
%EVOLVE_POPULATION    Method of the MLC class. Computes next population.
%
%   MLC_OBJ.EVOLVE_POPULATION computes the next generation of the MLC 
%   object MLC_OBJ if the last generation is evaluated.
%
%   MLC_OBJ.EVOLVE_POPULATION(n) Computes the n+1 generation of the MLC 
%   object MLC_OBJ if its population is at least of generation n. All
%   further generations will be discarded.
%
%   All options are set in the MLC object (See <a href="matlab:help MLC">MLC</a>). 
%
%   Implemented: - elitism, replication, crossover, mutation.
%                - tournament or fitness proportional for parent individual
%                  selection.
%                - detection of replicate individuals (keep or discard is
%                  optionnal).
%                - detection of past occurences and cost value.
%                - simplification of LISP expressions.
%
%   See also MLC, GENERATE_POPULATION, EVALUATE_POPULATION, FILL_POPULATION
%
%   Copyright (C) 2013 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox

    %% initialisation
    if nargin>1
        mlc.population=mlc.population(1:i);
    end
    
    ngen=length(mlc.population);          
    verb=mlc.parameters.verbose;
    
    if isempty(mlc.population)
        display('Population is empty')
        display(['Run ' inputname(1) '.generate_population'])
        return
    end
    
    if min(mlc.population(length(mlc.population)).fitnesses)==-1
        display('Population not evaluated');
        display(['Run ' inputname(1) '.evaluate_population'])
        return
    end
    
    %% Allocation of next generation
    
    mlc.population(ngen+1).individuals=cell(mlc.parameters.size,1);            
	mlc.population(ngen+1).occurence=zeros(mlc.parameters.size,1)*0;
	mlc.population(ngen+1).fitnesses=zeros(mlc.parameters.size,1)*0-1;
    if strcmp(mlc.parameters.selectionmethod,'pareto')
        mlc.population(ngen+1).complexity=zeros(mlc.parameters.size,1)*0+100;
    end
    
    if verb>0;fprintf('Breeding generation %i\n',ngen+1);end
    
    
    
  
  
 
    %% Elitism
    if mlc.parameters.elitism==0;
        if verb>1;fprintf('No elitism used\n');end
    else
        if verb>1;fprintf('Elitism :%i\n',mlc.parameters.elitism);end
        %[~,idx]=sort(mlc.population(ngen).fitnesses,'ascend');   % get ordered index of last generation in idx
        for i=1:mlc.parameters.elitism
            %mlc.population(ngen+1).individuals{i,1}=mlc.population(ngen).individuals{idx(i),1};
            %mlc.population(ngen+1).occurence(i,1)=mlc.population(ngen).occurence(idx(i),1)+1;
            %mlc.population(ngen+1).fitnesses(i,1)=mlc.population(ngen).fitnesses(idx(i),1);
            %mlc.population(ngen+1).selected{i}=idx(i);
            mlc.population(ngen+1).individuals{i,1}=mlc.population(ngen).individuals{i,1};
            mlc.population(ngen+1).occurence(i,1)=mlc.population(ngen).occurence(i,1)+1;
            mlc.population(ngen+1).fitnesses(i,1)=mlc.population(ngen).fitnesses(i,1);
            if strcmp(mlc.parameters.selectionmethod,'pareto')
                mlc.population(ngen+1).complexity(i,1)=mlc.population(ngen).complexity(i,1);
            end
            mlc.population(ngen+1).selected{i}=i;
            
            mlc.population(ngen+1).generatedfrom(i,1)=4;
        end
    end
    %% Fill the population with crossover, mutation and replication.
    mlc.fill_population;
end
            
