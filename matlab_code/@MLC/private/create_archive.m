function mlc=create_archive(mlc,~)
%SORT_POPULATION    Hidden Method of the MLC class. Sorts population
% and creates an archive.
%   MLC_OBJ.PARETO_SORT can not be called by user. 
%
%   All options are set in the MLC object (See <a href="matlab:help MLC">MLC</a>). 
%
%   Implemented: 
%               - Pareto aware sorting
%               - Standard sort
%               - creates archive
%
%   See also MLC, EVALUATE_POPULATION
%
%   Copyright (C) 2014 Kai von Krbek (Kai.von.Krbek@krbek.de)
%   This file is part of the TUCOROM MLC Toolbox

%% Utility
verb=mlc.parameters.verbose;
ngen=length(mlc.population);                                          %% number of current generation
nind=length(mlc.population(ngen).individuals);                        %% number of individuals


%[~,idx]=sort(mlc.population(ngen).fitnesses,'ascend');
%mlc.population(ngen).individuals=mlc.population(ngen).individuals(idx);
%mlc.population(ngen).fitnesses=mlc.population(ngen).fitnesses(idx);
%mlc.population(ngen).occurence=mlc.population(ngen).occurence(idx);
%mlc.population(ngen).generatedfrom=mlc.population(ngen).generatedfrom(idx);
%mlc.population(ngen).selected=mlc.population(ngen).selected(idx);
%if strcmp(mlc.parameters.selectionmethod,'pareto')
%    mlc.population(ngen).complexity=mlc.population(ngen).complexity(idx);
%    mlc = pareto_sort(mlc);
%end
%if verb>0;fprintf('Population successfully sorted\n');end



%% Update archive iff existent
if mlc.parameters.archive_size>0 && ngen==1
    narch=mlc.parameters.archive_size;
    mlc.archive.individuals=mlc.population(ngen).individuals(1:narch,1);
    mlc.archive.fitnesses=mlc.population(ngen).fitnesses(1:narch,1);
    mlc.archive.occurence=mlc.population(ngen).occurence(1:narch,1);
    if strcmp(mlc.parameters.selectionmethod,'pareto')
        mlc.archive.complexity=mlc.population(ngen).complexity(1:narch,1);
    end
end


if mlc.parameters.archive_size>0 && ngen>1% if nargin < 2 then we are in the original call,
    % not a call from remove_badvalues or this loop.
    narch=mlc.parameters.archive_size;
    
    % Initialize
    individuals=cell(nind+narch,1);
    occurence=zeros(nind+narch,1)*0;
    fitnesses=zeros(nind+narch,1)*0;
    if strcmp(mlc.parameters.selectionmethod,'pareto')
        complexity=zeros(nind+narch,1)*0;
    end
    for i=1:nind
        individuals{i,1}=mlc.population(ngen).individuals{i,1};
        occurence(i,1)=mlc.population(ngen).occurence(i,1);
        fitnesses(i,1)=mlc.population(ngen).fitnesses(i,1);
        if strcmp(mlc.parameters.selectionmethod,'pareto')
            complexity(i,1)=mlc.population(ngen).complexity(i,1);
        end
    end
    for i=1:narch
        individuals{i+nind,1}=mlc.archive.individuals{i,1};
        occurence(i+nind,1)=mlc.archive.occurence(i,1)+1;
        fitnesses(i+nind,1)=mlc.archive.fitnesses(i,1);
        if strcmp(mlc.parameters.selectionmethod,'pareto')
            complexity(i+nind,1)=mlc.archive.complexity(i,1);
        end
    end
    %individuals=cat(1,mlc.population(ngen).individuals,mlc.archive.individuals);%{mlc.population(ngen).individuals{:,1},mlc.archive.individuals{:,1}};
    
    %occurence(1:nind)=mlc.population(ngen).occurence;
    %fitnesses(1:nind)=mlc.population(ngen).fitnesses;
    %if strcmp(mlc.parameters.selectionmethod,'pareto')
    %    complexity=mlc.population(ngen).complexity;
    %end
    % The individuals in the archive occur once more
    %occurence(nind+1:nind+narch)=mlc.archive.occurence+1;
    %fitnesses(nind+1:nind+narch)=mlc.archive.fitnesses;
    %if strcmp(mlc.parameters.selectionmethod,'pareto')
    %    complexity(nind+1:nind+narch)=mlc.archive.complexity;
    %end
    
    % Sorting the archive together with the population to determine the
    % best individuals
    [~,idx]=sort(fitnesses,'ascend');
    individuals=individuals(idx);
    fitnesses=fitnesses(idx);
    occurence=occurence(idx);
    if strcmp(mlc.parameters.selectionmethod,'pareto')
        complexity=complexity(idx);
        %Pareto-sort
        i=2;
        j=2;
        idx = 1:nind+narch;
        complexity_=complexity(1);
        while complexity_>= mlc.parameters.mindepth && j<nind+narch
            if complexity(j) < complexity_ && fitnesses(j)<mlc.parameters.badvalue
                complexity_ = complexity(i);
                % exchange the values of i and j
                idx(i)=j;
                idx(j)=i;
                i=i+1;
            elseif fitnesses(j)>=mlc.parameters.badvalue
                j=nind+narch-1;
            end
            j=j+1;
        end
        % Sort the not pareto optimal indeces by ascending fitness
        [~,idx(i+1:nind+narch)]=sort(idx(i+1:nind+narch),'ascend');
        individuals=individuals(idx);
        fitnesses=fitnesses(idx);
        occurence=occurence(idx);
        complexity=complexity(idx);
    end
    
    
    % Creating the archive from the best individuals
    for i=1:narch
        mlc.archive.individuals{i,1}=individuals{i,1};
        mlc.archive.occurence(i,1)=occurence(i,1);
        mlc.archive.fitnesses(i,1)=fitnesses(i,1);
        if strcmp(mlc.parameters.selectionmethod,'pareto')
            mlc.archive.complexity(i,1)=complexity(i,1);
        end
    end
    %mlc.archive.individuals=individuals(1:narch,1);
    %mlc.archive.fitnesses=fitnesses(1:narch);
    %mlc.archive.occurence=occurence(1:narch);
    %if strcmp(mlc.parameters.selectionmethod,'pareto')
    %    mlc.archive.complexity=complexity(1:narch);
    %end
end
end