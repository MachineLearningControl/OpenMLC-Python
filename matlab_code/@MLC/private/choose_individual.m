function idx=choose_individual(mlc,nindivs)
%CHOOSE_INDIVIVIDUAL    Private function of the MLC CLASS. Implements individual selection.
%    idx=choose_individual(MLC_OBJ,NINDIVS) returns NINDIVS indices
%    corresponding to individuals in the preceding generation. This funtion
%    is called by <a href="matlab:help
%    fill_population">fill_population</a>. 
%
%    Three selection methods are implemented, tournament, pareto, and fitness
%    proportional. See <a href="matlab:help MLC/parameters">MLC parameters</a>.
%    If an archive is present, the second indidvidual will be chosen from
%    the archive.
%
%   Copyright (C) 2013 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox

%% Output initialization and other tiny stuff
    idx=zeros(1,nindivs);
    ngen=length(mlc.population)-1;                      %% the ngen+1 generation is being processed but we work on ngen.
    nind=length(mlc.population(ngen).individuals);      %% number of individuals
    narch=mlc.parameters.archive_size;                  %% Size of the archive

%% Method: Tournament
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% A tournament consist in choosing a number tournamentsize of             %
% individuals by a random process (equal weight for each individual). Out %
% of these individuals the one with the best fitness is chosen. If two are%
% needed two tournaments are performed                                    %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Method: Pareto
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% The pareto selection is based on the tournament selection process. It   %
% consists in choosing a number tournamentsize of individuals by a random %
% process (equal weight for each individual). Out of these individuals    %
% the one with the best fitness is chosen, but with a preference to more  %
% simple individuals if the fitness is only slightly worse.               %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%% Method selection
    switch mlc.parameters.selectionmethod

    case 'tournament'
        selected=zeros(1,mlc.parameters.tournamentsize);  %% initialisation of selected individuals for tournament
        for i=1:mlc.parameters.tournamentsize        %% selecting the individuals
            n=ceil(rand*nind);                   %% random integer between 1 and nind
            while max(n==selected)               %% avoid repetition 
                n=ceil(rand*nind);
            end
            selected(i)=n;
        end
        f=mlc.population(ngen).fitnesses(selected);         %% retrieve individuals fitness
        [~,k]=min(f);                            %% find the MINIMUM
        idx(1)=selected(k);                      %% and here we are

        if nindivs==2                            %% if needed, run another time
            if narch>0 && ngen>1
                selected=zeros(1,mlc.parameters.tournamentsize);
                for i=1:mlc.parameters.tournamentsize
                    n=ceil(rand*narch);
                    while max(n==selected)  %% avoid repetition and selecting the same
                        n=ceil(rand*narch);
                    end
                    selected(i)=n;
                end
                f=mlc.archive.fitnesses(selected);
                [~,k]=min(f);
                idx(2)=selected(k);
            else
                selected=zeros(1,mlc.parameters.tournamentsize);
                for i=1:mlc.parameters.tournamentsize
                    n=ceil(rand*nind);
                    while max(n==[selected idx(1)])  %% avoid repetition and selecting the same
                        n=ceil(rand*nind);
                    end
                    selected(i)=n;
                end
                f=mlc.population(ngen).fitnesses(selected);
                [~,k]=min(f);
                idx(2)=selected(k);
            end
        end
        
    case 'fitness_proportional'
        if narch>0 && ngen>1
            % Get individual from population
            adj_fit=1./(1+mlc.population(ngen).fitnesses); % between 0 and 1
            probs=adj_fit/sum(adj_fit);              % better indices have better probs and sum(probs)=1
            table=cumsum(probs);                     % lookup table for random number between 0 and 1
            [~,idx(1)]=min(abs(repmat(rand(),[nind 1])-repmat(table,[1 1])));
            % Get individual from archive
            if nindivs==2
                adj_fit=1./(1+mlc.archive.fitnesses); % between 0 and 1
                probs=adj_fit/sum(adj_fit);              % better indices have better probs and sum(probs)=1
                table=cumsum(probs);                     % lookup table for random number between 0 and 1
                [~,idx(2)]=min(abs(repmat(rand(),[narch 1])-repmat(table,[1 1])));
            end
        else
            adj_fit=1./(1+mlc.population(ngen).fitnesses); % between 0 and 1
            probs=adj_fit/sum(adj_fit);              % better indices have better probs and sum(probs)=1
            table=cumsum(probs);                     % lookup table for random number between 0 and 1
            n=rand(1,nindivs);
            [~,idx]=min(abs(repmat(n,[nind 1])-repmat(table,[1 nindivs])));
        end
            
    case 'pareto'
        complexities=zeros(1,mlc.parameters.tournamentsize);
        selected=zeros(1,mlc.parameters.tournamentsize);
        select=0;
        j=1;
        while j<3
            if narch>0 && j==2 && ngen>1
                complexity=10000;
                for i=1:mlc.parameters.tournamentsize        %% selecting the individuals
                    n=ceil(rand*narch);
                    while max(n==selected)               %% avoid repetition
                        n=ceil(rand*narch);
                    end
                    selected(i)=n;
                    if length(mlc.archive.complexity)==narch
                        complexities(i)=mlc.archive.complexity(n);
                        if i>1
                            Jquot=mlc.archive.fitnesses(selected(i))/mlc.archive.fitnesses(select);
                            if complexities(i)>10 && complexities(i-1)>10
                                c=complexities(i)/double(complexity);
                                % if the complexity can be reduced relatively much
                                % more than the increase in fitness value,
                                % replace with simpler solution
                                if (c*Jquot<0.9)
                                    select =selected(i);
                                    complexity = complexities(i);
                                end
                                %For each grade of less complexity a malus of 1% is
                                %acceptable. Only for functions of little complexity
                            elseif (Jquot<1+(complexities(i)-complexity)*.01)
                                select =selected(i);
                                complexity = complexities(i);
                            end
                            % If there is at least an improvement of 15%, the
                            % solution is taken regardless of complexity
                            if Jquot<0.85
                                select = selected(i);
                                complexity = complexities(i);
                            end
                        else
                            select=selected(i);
                            complexity = complexities(i);
                        end
                        
                    end
                end
            else
                for i=1:mlc.parameters.tournamentsize        %% selecting the individuals
                    n=ceil(rand*nind);                   %% random integer between 1 and nind
                    while max(n==selected)               %% avoid repetition
                        n=ceil(rand*nind);
                    end
                    selected(i)=n;
                    if length(mlc.population(ngen).complexity)==nind
                        complexities(i)=mlc.population(ngen).complexity(n);
                        if i>1
                            Jquot=mlc.population(ngen).fitnesses(selected(i))/mlc.population(ngen).fitnesses(select);
                            if complexities(i)>10 && complexities(i-1)>10
                                c=complexities(i)/double(complexity);
                                % if the complexity can be reduced relatively much
                                % more than the increase in fitness value,
                                % replace with simpler solution
                                if (c*Jquot<0.9)
                                    select =selected(i);
                                    complexity = complexities(i);
                                end
                                %For each grade of less complexity a malus of 1% is
                                %acceptable. Only for functions of little complexity
                            elseif (Jquot<1+(complexities(i)-complexity)*.01)
                                select =selected(i);
                                complexity = complexities(i);
                            end
                            % If there is at least an improvement of 15%, the
                            % solution is taken regardless of complexity
                            if Jquot<0.85
                                select = selected(i);
                                complexity = complexities(i);
                            end
                        else
                            select=selected(i);
                            complexity = complexities(i);
                        end
                        
                    end
                end
            end
            idx(j)=select;
            j=j+1;
            if nindivs==1; j=3; end
        end
        
    end
end
        
            