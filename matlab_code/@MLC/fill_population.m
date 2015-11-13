function mlc=fill_population(mlc)
%FILL_POPULATION    Hidden Method of the MLC class. Fills population using replication, crossover and mutation.
%   MLC_OBJ.FILL_POPULATION can not be called by user. It is called by
%   <a href="matlab:help remove_badvalues">remove_badvalues</a> to replace bad individuals and by <a href="matlab:help evolve_population">evolve_population</a> to
%   create a new generation.
%
%   All options are set in the MLC object (See <a href="matlab:help MLC">MLC</a>). 
%
%   Implemented: - replication, crossover, mutation.
%                - tournament for parent individual selection.
%                - detection of replicate individuals (keep or discard is
%                  optional).
%                - detection of past occurences and cost value.
%
%   See also MLC, EVOLVE_POPULATION, REMOVE_BADVALUES
%
%   Copyright (C) 2013-2014 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox


verb=mlc.parameters.verbose;
% This function can be called by evolve_population or remove_badvalues
% In both cases the population for the current generation is creates but
% some individuals are empty. 
% This function fills these empty individuals using the GP parameters.

ngen=length(mlc.population);
nind=length(mlc.population(ngen).individuals);
to_fill=zeros(1,nind);
for i=1:nind
    to_fill(i)=isempty(mlc.population(ngen).individuals{i});
end
ngen=ngen-1;
idx_tofill=find(to_fill);
    %% Fill population
    i=0;
    if verb>1;fprintf('%i individuals to generate\n',length(idx_tofill));end
    while i<length(idx_tofill)
       
        if length(idx_tofill)-i>1
            dice=rand;
        else
            dice=rand*(mlc.parameters.probrep+mlc.parameters.probmut);
        end
        if dice <= mlc.parameters.probrep;
            channel=1;
        elseif (dice > mlc.parameters.probrep) && (dice <= mlc.parameters.probmut+mlc.parameters.probrep)
            channel=2;
        else
            channel=3;
        end
        i=i+1;
        switch channel
        case 1
            %% replication
            if verb>2;fprintf('Generating individual(s) %i\n',idx_tofill(i));end
            if verb>3;fprintf('Replication of:\n');end
            same=1;
            while same==1
                idx=choose_individual(mlc,1);                             % choose one individual
                if verb>3;fprintf('%s',mlc.population(ngen).individuals{idx(1),1});end
                mlc.population(ngen+1).individuals{idx_tofill(i),1}=mlc.population(ngen).individuals{idx(1),1};       % copy individual
                mlc.population(ngen+1).occurence(idx_tofill(i),1)=mlc.population(ngen).occurence(idx(1),1)+1;         % one more occurence
                mlc.population(ngen+1).fitnesses(idx_tofill(i),1)=mlc.population(ngen).fitnesses(idx(1),1);           % fitness is copied  
                mlc.population(ngen+1).selected{idx_tofill(i)}=idx(1);                                     % keep track of the index of previous ind
                k=find(strcmp(mlc.population(ngen+1).individuals{idx_tofill(i),1},mlc.population(ngen+1).individuals));
                if length(k)<2
                    same=0;
                else
                    same=mlc.parameters.lookforduplicates;
                    %fprintf('Duplicate found\n')
                    
                end
            end
            mlc.population(ngen+1).generatedfrom(idx_tofill(i),1)=1;
        case 2
            %% mutation
            same=1;fail=1;
            if verb>2;fprintf('Generating individual(s) %i\n',idx_tofill(i));end
            if verb>3;fprintf('Mutation of:\n');end
            while same==1 || fail==1;
                idx=choose_individual(mlc,1);                                             %% choose one individual
                if verb>3;fprintf('%s\n',mlc.population(ngen).individuals{idx(1),1});end
                [new_ind,fail]=mutate(mlc.population(ngen).individuals{idx(1),1},mlc.parameters);     %% Creates mutated individual
                mlc.population(ngen+1).individuals{idx_tofill(i),1}=new_ind;
                if mlc.parameters.simplify
                    mlc.population(ngen+1).individuals{idx_tofill(i),1}=simplify_my_LISP(mlc.population(ngen+1).individuals{idx_tofill(i),1},mlc.parameters);
                end 
                
                
                k=find(strcmp(mlc.population(ngen+1).individuals{idx_tofill(i),1},mlc.population(ngen+1).individuals));
                if length(k)<2
                    same=0;
                else
                    same=mlc.parameters.lookforduplicates;
                    %fprintf('Duplicate found\n')
                    
                end
            end
            k=find(strcmp(mlc.population(ngen+1).individuals{idx_tofill(i),1},mlc.individual_table.individuals));
            if isempty(k)
                mlc.population(ngen+1).occurence(idx_tofill(i),1)=1;                               %% initialize fitness and occurence
                mlc.population(ngen+1).fitnesses(idx_tofill(i),1)=-1;
            else
                mlc.population(ngen+1).occurence(idx_tofill(i),1)=mlc.individual_table.occurence(k)+1;
                mlc.population(ngen+1).fitnesses(idx_tofill(i),1)=mlc.individual_table.fitnesses(k);
            end
            if verb>3;fprintf('result:\n%s\n',mlc.population(ngen+1).individuals{idx_tofill(i),1});end
            mlc.population(ngen+1).selected{idx_tofill(i)}=idx(1);                                 % keep track of the index of previous ind
            mlc.population(ngen+1).generatedfrom(idx_tofill(i),1)=2;
          
            case 3
            %% crossover
            same=1;fail=1;
            if verb>2;fprintf('Generating individual(s) %i and %i\n',idx_tofill(i),idx_tofill(i+1));end
            if verb>3;fprintf('Crossover of:\n');end
            iinit=i;
            while same==1 || fail==1
                
                idx=choose_individual(mlc,2);                         %% choose two individuals
                if verb>3;fprintf('%s\n',mlc.population(ngen).individuals{idx(1),1});fprintf('and\n');end
                if verb>3;fprintf('%s\n',mlc.population(ngen).individuals{idx(2),1});end
                if mlc.parameters.archive_size>0 && ngen>2
                    [m1,m2,fail]=crossover(mlc.population(ngen).individuals{idx(1),1},mlc.archive.individuals{idx(2),1},mlc.parameters); % cross individuals with archive
                else
                    [m1,m2,fail]=crossover(mlc.population(ngen).individuals{idx(1),1},mlc.population(ngen).individuals{idx(2),1},mlc.parameters); % cross individuals
                end
                mlc.population(ngen+1).individuals{idx_tofill(i),1}=m1;
                i=i+1;
                mlc.population(ngen+1).individuals{idx_tofill(i),1}=m2;
                if mlc.parameters.simplify
                    mlc.population(ngen+1).individuals{idx_tofill(i),1}=simplify_my_LISP(mlc.population(ngen+1).individuals{idx_tofill(i),1},mlc.parameters);
                    mlc.population(ngen+1).individuals{idx_tofill(i-1),1}=simplify_my_LISP(mlc.population(ngen+1).individuals{idx_tofill(i-1),1},mlc.parameters);
                end
                
                
                
                
                k1=find(strcmp(mlc.population(ngen+1).individuals{idx_tofill(i-1),1},mlc.population(ngen+1).individuals));
                k2=find(strcmp(mlc.population(ngen+1).individuals{idx_tofill(i),1},mlc.population(ngen+1).individuals));
                if length(k1)<2 && length(k2)<2 
                    same=0;
                else
                    same=mlc.parameters.lookforduplicates;
                    %fprintf('Duplicate found\n')
                    i=i-mlc.parameters.lookforduplicates;
                end
                if fail==1
                    i=iinit;
                end
                
            end
            
            k1=find(strcmp(mlc.population(ngen+1).individuals{idx_tofill(i-1),1},mlc.individual_table.individuals),1);
            if isempty(k1) %% Detects previous occurences, assign fitness and occurence.
               mlc.population(ngen+1).occurence(idx_tofill(i-1),1)=1;                               %% initialize fitness and occurence
                mlc.population(ngen+1).fitnesses(idx_tofill(i-1),1)=-1;
            else
                 mlc.population(ngen+1).occurence(idx_tofill(i-1),1)=mlc.individual_table.occurence(k1)+1;
                mlc.population(ngen+1).fitnesses(idx_tofill(i-1),1)=mlc.individual_table.fitnesses(k1);
            end
            
            k2=find(strcmp(mlc.population(ngen+1).individuals{idx_tofill(i),1},mlc.individual_table.individuals),1);
            if isempty(k2) %% Detects previous occurences, assign fitness and occurence.
               mlc.population(ngen+1).occurence(idx_tofill(i),1)=1;                               %% initialize fitness and occurence
                mlc.population(ngen+1).fitnesses(idx_tofill(i),1)=-1;
            else
                 mlc.population(ngen+1).occurence(idx_tofill(i),1)=mlc.individual_table.occurence(k2)+1;
                mlc.population(ngen+1).fitnesses(idx_tofill(i),1)=mlc.individual_table.fitnesses(k2);
            end
            
            if verb>3;fprintf('result:\n%s\n',mlc.population(ngen+1).individuals{idx_tofill(i-1),1});fprintf('and\n');end
            if verb>3;fprintf('%s\n',mlc.population(ngen+1).individuals{idx_tofill(i),1});end
            

            mlc.population(ngen+1).selected{idx_tofill(i-1)}=[idx(1) idx(2)];
            mlc.population(ngen+1).selected{idx_tofill(i)}=[idx(1) idx(2)];
            mlc.population(ngen+1).generatedfrom(idx_tofill(i-1),1)=3;
            mlc.population(ngen+1).generatedfrom(idx_tofill(i),1)=3;
                
        end
      
    end
end
