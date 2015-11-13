function mlc=evaluate_population(mlc,~)
%EVALUATE_POPULATION    Method of the MLC class. Evaluates population.
%
%   MLC_OBJ.EVALUATE_POPULATION evaluates cost of individuals and update
%   the MLC object MLC_OBJ.
%
%   All options are set in the MLC object (See <a href="matlab:help MLC">MLC</a>).
%
%   Implemented: - evaluation with m-file function (standalone and
%                  multihread), external evaluation with file exchange.
%                - detection of bad individuals (above a threshold) and
%                  their replacement.
%                - evaluation or not of already evaluated individuals.
%                - averaging of all past cost values for a given individual
%                  if evaluation are repeated (for experiments or numerics
%                  with random noise).
%
%   See also MLC, GENERATE_POPULATION, EVOLVE_POPULATION, REMOVE_BADVALUES
%
%   Copyright (C) 2013 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox

%% Start program


%% Utility
verb=mlc.parameters.verbose;
ngen=length(mlc.population);                                          %% number of current generation
nind=length(mlc.population(ngen).individuals);                        %% number of individuals
%% Common variables for every method
if (mlc.parameters.evaluate_all && mlc.parameters.badvalues_elimswitch)
    eval_idx=1:nind;
    if verb>0;fprintf('Starting evaluation of generation %i\n',ngen);end
else
    eval_idx=find(mlc.population(ngen).fitnesses==-1);                %% select individuals with unknown fitness
    if verb>0;fprintf('Completing evaluation of generation %i\n',ngen);end
end
if verb>0;fprintf('%i indivuals to evaluate\n',length(eval_idx));end
idv_to_evaluate=mlc.population(ngen).individuals(eval_idx);
gen_param=mlc.parameters;
JJ=zeros(1,length(eval_idx));
%% Beginning method dependent evaluation
if verb>1;fprintf(['Evaluation method: "' mlc.parameters.evaluation_method '"\n']);end
%% Check if method was interupted
if exist(fullfile(mlc.parameters.savedir,'MLC_incomplete.mat'),'file') && mlc.parameters.saveincomplete==1;
    ic=0;
    load(fullfile(mlc.parameters.savedir,'MLC_incomplete.mat'),'JJ','ic');
    istart=ic;
else
    istart=1;
end

switch mlc.parameters.evaluation_method
    case 'test'
        %% only one evaluator is used, a random number is used as fitness.
        for i=istart:length(eval_idx);
            if mlc.parameters.saveincomplete==1
                ic=i;
                save(fullfile(mlc.parameters.savedir,'MLC_incomplete.mat'),'JJ','ic');
            end
            if verb>1;fprintf('Individual %i from generation %i\n',eval_idx(i),ngen);end
            if verb>2;fprintf('%s\n',mlc.population(ngen).individuals{eval_idx(i)});end
            JJ(i)=rand;
        end
        
        
    case 'standalone_files'
        %% only one evaluator is used. Interaction with files in a folder.
        if ngen==1 && min(mlc.population(1).fitnesses)==-1
            mlc.individual_table.evorder.number=0;
        end
        for i=istart:length(eval_idx);
            % save the state
            if mlc.parameters.saveincomplete==1
                ic=i;
                save(fullfile(mlc.parameters.savedir,'MLC_incomplete.mat'),'JJ','ic');
            end
            if verb>1;fprintf('Individual %i from generation %i\n',eval_idx(i),ngen);end
            if verb>2;fprintf('%s\n',idv_to_evaluate{i});end
            if verb>3;fprintf('Writing %s in %s\n',gen_param.indfile,gen_param.exchangedir);end
            fid=fopen(fullfile(gen_param.exchangedir,gen_param.indfile),'w');
            % translate into formal expression if needed
            if mlc.parameters.formal==1
                m=readmylisp_to_formal_MLC(idv_to_evaluate{i},mlc.parameters);
            else
                m=idv_to_evaluate{i};
            end
            fprintf(fid,[m mlc.parameters.end_character]);
            
            
            fclose(fid);
            if verb>3;fprintf('Waiting for %s in %s\n',gen_param.Jfile,gen_param.exchangedir);end
            indiex=exist(fullfile(gen_param.exchangedir,gen_param.Jfile),'file');
            while indiex==0
                indiex=exist(fullfile(gen_param.exchangedir,gen_param.Jfile),'file');
                pause(0.1);
            end
            if verb>3;fprintf('Found fitness file\n');end
            JJ(i)=importdata(fullfile(mlc.parameters.exchangedir,mlc.parameters.Jfile));
            if verb>3;fprintf('Deleting fitness file\n');end
            delete(fullfile(mlc.parameters.exchangedir,mlc.parameters.Jfile));
            indiex=exist(fullfile(gen_param.exchangedir,gen_param.Jfile),'file');
            while indiex==1
                indiex=exist(fullfile(gen_param.exchangedir,gen_param.Jfile),'file');
                pause(0.1);
            end
            indiex=exist(fullfile(gen_param.exchangedir,gen_param.indfile),'file');
            while indiex==1
                indiex=exist(fullfile(gen_param.exchangedir,gen_param.indfile),'file');
                pause(0.1);
            end
            
            mlc.individual_table.evorder.number=mlc.individual_table.evorder.number+1;
            mlc.individual_table.evorder.individual{mlc.individual_table.evorder.number}=m;
            mlc.individual_table.evorder.fitness(mlc.individual_table.evorder.number)=JJ(i);
            mlc.individual_table.evorder.date{mlc.individual_table.evorder.number}=datestr(now);
            
            
        end
        case 'standalone_files_chex'
        %% only one evaluator is used. Interaction with files in a folder.
        
        for i=istart:length(eval_idx);
            % save the state
            if mlc.parameters.saveincomplete==1
                ic=i;
                save(fullfile(mlc.parameters.savedir,'MLC_incomplete.mat'),'JJ','ic');
            end
            if verb>1;fprintf('Individual %i from generation %i\n',eval_idx(i),ngen);end
            if verb>2;fprintf('%s\n',idv_to_evaluate{i});end
            if verb>3;fprintf('Writing %s in %s\n',gen_param.indfile,gen_param.exchangedir);end
            S2=[0:0.001:10];
            S3=S2*10;
            S4=S3*10;
            % translate into formal expression if needed
            if mlc.parameters.formal==1
                m=readmylisp_to_formal_MLC(idv_to_evaluate{i},mlc.parameters);
            else
                m=idv_to_evaluate{i};
            end
            
            if mlc.parameters.controls==1
                actuation=eval(readmylisp_to_formal_MLC(m,mlc.parameters))>0;
            else
                actuation=zeros(length(S2),mlc.parameters.controls);
                m=readmylisp_to_formal_MLC(idv_to_evaluate{i},mlc.parameters);
                for icont=1:mlc.parameters.controls
                    actuation(:,icont)=eval(m{icont})>0;
                end
            end
                    
            fid=fopen(fullfile(gen_param.exchangedir,gen_param.indfile),'w');
            fprintf(fid,'%s\n',idv_to_evaluate{i});
            if mlc.parameters.controls==1
                fprintf(fid,'%i\n',actuation);
            else
                fprintf(fid,['%i ' repmat(' %i',[1 mlc.parameters.controls-1]) '\n'],actuation');
            end
            fclose(fid);
            if verb>3;fprintf('Waiting for %s in %s\n',gen_param.Jfile,gen_param.exchangedir);end
            indiex=exist(fullfile(gen_param.exchangedir,gen_param.Jfile),'file');
            while indiex==0
                indiex=exist(fullfile(gen_param.exchangedir,gen_param.Jfile),'file');
                pause(0.1);
            end
            if verb>3;fprintf('Found fitness file\n');end
            JJ(i)=importdata(fullfile(mlc.parameters.exchangedir,mlc.parameters.Jfile));
            if verb>3;fprintf('Deleting fitness file\n');end
            delete(fullfile(mlc.parameters.exchangedir,mlc.parameters.Jfile));
            indiex=exist(fullfile(gen_param.exchangedir,gen_param.Jfile),'file');
            while indiex==1
                indiex=exist(fullfile(gen_param.exchangedir,gen_param.Jfile),'file');
                pause(0.1);
            end
            indiex=exist(fullfile(gen_param.exchangedir,gen_param.indfile),'file');
            while indiex==1
                indiex=exist(fullfile(gen_param.exchangedir,gen_param.indfile),'file');
                pause(0.1);
            end
        end
        case 'standalone_files_kai_ol'
        %% only one evaluator is used. Interaction with files in a folder.
        
        for i=istart:length(eval_idx);
            % save the state
            if mlc.parameters.saveincomplete==1
                ic=i;
                save(fullfile(mlc.parameters.savedir,'MLC_incomplete.mat'),'JJ','ic');
            end
            if verb>1;fprintf('Individual %i from generation %i\n',eval_idx(i),ngen);end
            if verb>2;fprintf('%s\n',idv_to_evaluate{i});end
            if verb>3;fprintf('Writing %s in %s\n',gen_param.indfile,gen_param.exchangedir);end
            % translate into formal expression if needed
            if mlc.parameters.formal==1
                m=readmylisp_to_formal_MLC_kai_ol(idv_to_evaluate{i},mlc.parameters);
                m=strrep(m,'.*','*');
            else
                m=idv_to_evaluate{i};
            end
            fid=fopen(fullfile(gen_param.exchangedir,gen_param.indfile),'w');
            fprintf(fid,'%s',m);
            fclose(fid);
            
            %system(['./go.sh']);
            
            
            if verb>3;fprintf('Waiting for %s in %s\n',gen_param.Jfile,gen_param.exchangedir);end
            indiex=exist(fullfile(gen_param.exchangedir,gen_param.Jfile),'file');
            while indiex==0
                indiex=exist(fullfile(gen_param.exchangedir,gen_param.Jfile),'file');
                pause(0.1);
            end
            if verb>3;fprintf('Found fitness file\n');end
            j=importdata(fullfile(mlc.parameters.exchangedir,mlc.parameters.Jfile));
            if all(isnan(j)) || all(ischar(j))
                JJ(i)=mlc.parameters.badvalue;
            else
            JJ(i)=j;
            end
            if verb>3;fprintf('Deleting fitness file\n');end
            delete(fullfile(mlc.parameters.exchangedir,mlc.parameters.Jfile));
            indiex=exist(fullfile(gen_param.exchangedir,gen_param.Jfile),'file');
            while indiex==1
                indiex=exist(fullfile(gen_param.exchangedir,gen_param.Jfile),'file');
                pause(0.1);
            end
            indiex=exist(fullfile(gen_param.exchangedir,gen_param.indfile),'file');
            while indiex==1
                indiex=exist(fullfile(gen_param.exchangedir,gen_param.indfile),'file');
                pause(0.1);
            end
        end
    case 'standalone_function'
        %% only one evaluator is used, the function given in mlc.parameters.evaluation_fuction is used.
        
        eval(['heval=@' mlc.parameters.evaluation_function ';']);
        f=heval;
        for i=istart:length(eval_idx);
            
            if mlc.parameters.saveincomplete==1
                ic=i;
                save(fullfile(mlc.parameters.savedir,'MLC_incomplete.mat'),'JJ','ic');
            end
            if verb>1;fprintf('Individual %i from generation %i\n',eval_idx(i),ngen);end
            if verb>2;fprintf('%s\n',idv_to_evaluate{i});end
            % translate into formal expression if needed
            if mlc.parameters.formal==1
                m=readmylisp_to_formal_MLC(idv_to_evaluate{i},mlc.parameters);
            else
                m=idv_to_evaluate{i};
            end
            JJ(i)=feval(f,m,mlc.parameters,i);
        end
        
    case 'multithread_function'
        %% multithread is used, the function given in mlc.parameters.evaluation_fuction is used.
        eval(['heval=@' mlc.parameters.evaluation_function ';']);
        f=heval;
        if matlabpool('size')==0
            matlabpool 6
        end
     %   pb=parfor_progress(length(eval_idx));
     %   tnow=now;
     %   milestones=round(linspace(1,length(eval_idx),11))/length(eval_idx)*100;
        formal=mlc.parameters.formal;
        gen_param=mlc.parameters;
        parfor i=1:length(eval_idx);
     %       perc=parfor_progress;
      %      bnow=now;
       %     enow=(bnow-tnow)/perc*100+tnow;
        %    [~,k]=find(perc==milestones);
         %   if isempty(k)==0
         %       if verb>1;fprintf('%i percent sent, exp: %s\n',(k-1)*10,datestr(enow,13));end
          %  end
            if verb>2;fprintf('Individual %i from generation %i\n',eval_idx(i),ngen);end
            if verb>2;fprintf('%s\n',idv_to_evaluate{i});end
            % translate into formal expression if needed
            if formal==1
                m=readmylisp_to_formal_MLC(idv_to_evaluate{i},gen_param);
            else
                m=idv_to_evaluate{i};
            end
            JJ(i)=feval(f,m,gen_param,i);
        end
      %  pb=parfor_progress(0);
        %matlabpool close
        
        case 'multithread_files'
        %% multithread is used, the function given in mlc.parameters.evaluation_fuction is used.
        eval(['heval=@' mlc.parameters.evaluation_function ';']);
        f=heval;
        if matlabpool('size')==0
            matlabpool 6
        end
        pb=parfor_progress(length(eval_idx));
        tnow=now;
        milestones=round(linspace(1,length(eval_idx),11))/length(eval_idx)*100;
        formal=mlc.parameters.formal;
        gen_param=mlc.parameters;
        j=1;
        k=1;
        for i=1:length(eval_idx);
            evalu(k,j)=eval_idx(i);
            j=j+1;if j>10; j=1; k=k+1;end
        end
        parfor i=1:10;%length(eval_idx);
            perc=parfor_progress;
            bnow=now;
            enow=(bnow-tnow)/perc*100+tnow;
            [~,k]=find(perc==milestones);
            if isempty(k)==0
                if verb>1;fprintf('%i percent sent, exp: %s\n',(k-1)*10,datestr(enow,13));end
            end
            if verb>2;fprintf('Individual %i from generation %i\n',eval_idx(i),ngen);end
            if verb>2;fprintf('%s\n',idv_to_evaluate{i});end
            % translate into formal expression if needed
            if formal==1
                m=readmylisp_to_formal_MLC(idv_to_evaluate{i},gen_param);
            else
                m=idv_to_evaluate{i};
            end
            JJ(i)=feval(f,m,gen_param,i);
        end
        pb=parfor_progress(0);
        %matlabpool close
end
if  mlc.parameters.saveincomplete==1 && ~strcmp(mlc.parameters.evaluation_method,'multithread_function');
    delete(fullfile(mlc.parameters.savedir,'MLC_incomplete.mat'));
end
if verb>0;fprintf('Updating database\n');end
for i=1:length(eval_idx);
    if verb>2;fprintf('Individual %i from generation %i\n',eval_idx(i),ngen);end
    if verb>2;fprintf('%s\n',mlc.population(ngen).individuals{eval_idx(i)});end
    J=JJ(i);
    if isnan(J) || isinf(J)
        if verb>4;fprintf('That''s a NaN !\n');end
        J=mlc.parameters.badvalue;
    end
    
    if J>mlc.parameters.badvalue;
        J=mlc.parameters.badvalue;
    end
    
    if verb>4
        if mlc.population(ngen).occurence(eval_idx(i))-1>0 && J~= mlc.population(ngen).fitnesses(eval_idx(i))
            fprintf('Past occurence: %i\n', mlc.population(ngen).occurence(eval_idx(i))-1);
            fprintf('New value: %e\n',J)
            fprintf('Old value: %e\n', mlc.population(ngen).fitnesses(eval_idx(i)));
            mlc.population(ngen).evaluation_problem(eval_idx(i))=1;
            fprintf('Inconsistency in the J values !\n')
            fprintf('If the work is numeric without source of noise it might be a problem\n')
        end
    end
    
    
    if J~= mlc.population(ngen).fitnesses(eval_idx(i))
        mlc.population(ngen).evaluation_problem(eval_idx(i))=1;
    end
    %mlc.population(ngen).fitnesses(eval_idx(i))=(mlc.population(ngen).fitnesses(eval_idx(i))*(mlc.population(ngen).occurence(eval_idx(i))-1)...
    %    + J)/mlc.population(ngen).occurence(eval_idx(i)); %% newJ = (meanJ*previous occurence + actualJ)/all_occurences
    % Update individual table mlc.individual_table or create if not
    % present
    k=find(strcmp(mlc.population(ngen).individuals{eval_idx(i)},mlc.individual_table.individuals));
    if isempty(k)
        mlc.individual_table.nb=mlc.individual_table.nb+1;
        mlc.individual_table.individuals{mlc.individual_table.nb}=mlc.population(ngen).individuals{eval_idx(i)};
        mlc.individual_table.occurence(mlc.individual_table.nb)=1;
        %mlc.individual_table.fitnesses(mlc.individual_table.nb)=mlc.population(ngen).fitnesses(eval_idx(i));
        mlc.individual_table.pastfitness{mlc.individual_table.nb}=J;
        mlc.population(ngen).fitnesses(eval_idx(i))=J;
        mlc.individual_table.fitnesses(mlc.individual_table.nb)=J;
    else
        mlc.individual_table.occurence(k)=mlc.individual_table.occurence(k)+1;
        %mlc.individual_table.fitnesses(k)=mlc.population(ngen).fitnesses(eval_idx(i));
        mlc.individual_table.pastfitness{k}=[mlc.individual_table.pastfitness{k} J];
        mlc.population(ngen).fitnesses(eval_idx(i))=mean(mlc.individual_table.pastfitness{k});
        mlc.individual_table.fitnesses(k)=mean(mlc.individual_table.pastfitness{k});
    end
    if verb>2;fprintf('J=%.4e\n',J);end
    if verb>2;fprintf('J_mean=%.4e\n',mlc.population(ngen).fitnesses(eval_idx(i)));end
end

%% Eliminate meaningless individuals (All the individuals with fitness=badvalue)
switch mlc.parameters.badvalues_elim
    case 'none'
    case 'first'
        if ngen==1
            if verb>1;fprintf('Replacing bad individuals\n');end
            mlc=mlc.remove_badvalues;
        end
    case 'all'
        if verb>1;fprintf('Replacing bad individuals\n');end
        mlc=mlc.remove_badvalues;
end

%% Calculates the complexity of the fitness and stores it in mlc.population.complexity
if strcmp(mlc.parameters.selectionmethod,'pareto')
    if verb >1
        fprintf('Calculating the complexity of the functions...');
    end
    %CC = zeros(1,length(eval_idx));
    for i=1:length(eval_idx)
        m=idv_to_evaluate{i};
        %mlc.population(ngen).complexity(eval_idx(i)) = length(strfind(m,'('));
        mlc.population(ngen).complexity(eval_idx(i)) = pareto_complexity(m,mlc.parameters,0);
    end
    %mlc.population(ngen).complexity=CC;
end



%% Cascading Call
if nargin<2
    if mlc.parameters.no_of_cascades>0
        if verb>0; fprintf('Evaluating cascades of generation %i \n',ngen); end
        mlc = mlc.evaluate_cascades(mlc);
    end
end

%% End of evaluate_population


% Sort population
if nargin<2 % if nargin < 2 then we are in the original call,
    % not a call from remove_badvalues or this loop.
    % this is where we evaluate again the best individuals
    [~,idx]=sort(mlc.population(ngen).fitnesses,'ascend');
    mlc.population(ngen).individuals=mlc.population(ngen).individuals(idx);
    mlc.population(ngen).fitnesses=mlc.population(ngen).fitnesses(idx);
    mlc.population(ngen).occurence=mlc.population(ngen).occurence(idx);
    mlc.population(ngen).generatedfrom=mlc.population(ngen).generatedfrom(idx);
    mlc.population(ngen).selected=mlc.population(ngen).selected(idx);
    if strcmp(mlc.parameters.selectionmethod,'pareto')
        mlc.population(ngen).complexity=mlc.population(ngen).complexity(idx);
        mlc = pareto_sort(mlc);
    end
    if mlc.parameters.ev_again_best
        if verb>0;fprintf('Reevaluating best individuals\n');end
        for i=1:mlc.parameters.ev_again_times
            for j=1:mlc.parameters.ev_again_nb
                mlc.population(ngen).occurence(j)=mlc.population(ngen).occurence(j)+1;
                mlc.population(ngen).fitnesses(j)=-1;
            end
            mlc.parameters.elimswitch(0);
            mlc.evaluate_population('again');
            mlc.parameters.elimswitch(1);
            [~,idx]=sort(mlc.population(ngen).fitnesses,'ascend');
            mlc.population(ngen).individuals=mlc.population(ngen).individuals(idx);
            mlc.population(ngen).fitnesses=mlc.population(ngen).fitnesses(idx);
            mlc.population(ngen).occurence=mlc.population(ngen).occurence(idx);
            mlc.population(ngen).generatedfrom=mlc.population(ngen).generatedfrom(idx);
            mlc.population(ngen).selected=mlc.population(ngen).selected(idx);
            if strcmp(mlc.parameters.selectionmethod,'pareto')
                mlc.population(ngen).complexity=mlc.population(ngen).complexity(idx);
                mlc = pareto_sort(mlc);
            end
        end
        [~,idx]=sort(mlc.population(ngen).fitnesses,'ascend');
        mlc.population(ngen).individuals=mlc.population(ngen).individuals(idx);
        mlc.population(ngen).fitnesses=mlc.population(ngen).fitnesses(idx);
        mlc.population(ngen).occurence=mlc.population(ngen).occurence(idx);
        mlc.population(ngen).generatedfrom=mlc.population(ngen).generatedfrom(idx);
        mlc.population(ngen).selected=mlc.population(ngen).selected(idx);
        if strcmp(mlc.parameters.selectionmethod,'pareto')
            mlc.population(ngen).complexity=mlc.population(ngen).complexity(idx);
            mlc = pareto_sort(mlc);
        end
        %         subpop=MLC;subpop.parameters=mlc.parameters;
        %         subpop.parameters.size=mlc.parameters.ev_again_nb;
        %         subpop.parameters.elitism=mlc.parameters.ev_again_nb;
        %         for i=1:mlc.parameters.ev_again_nb
        %             subpop.insert_individual(mlc.population(ngen).individuals{i});
        %         end
        %         subpop.evaluate_population('again');
        %         for i=1:mlc.parameters.ev_again_times-1
        %             subpop.evolve_population;
        %             subpop.evaluate_population('again');
        %         end
        %
        %         for i=1:mlc.parameters.ev_again_nb
        %             idx=strcmp(mlc.population(ngen).individuals{i},subpop.population(mlc.parameters.ev_again_times).individuals);
        %             old_fit=mlc.population(ngen).fitnesses(i);
        %             old_occ=mlc.population(ngen).occurence(i);
        %             uptd_fit=subpop.population(mlc.parameters.ev_again_times).fitnesses(idx);
        %             uptd_occ=subpop.population(mlc.parameters.ev_again_times).occurence(idx);
        %             mlc.population(ngen).fitnesses(i)=(old_fit*old_occ+uptd_fit*uptd_occ)/(old_occ+uptd_occ);
        %             mlc.population(ngen).occurence(i)=(old_occ+uptd_occ);
        %         end
        
    end
    if verb>0;fprintf('Population successfully evaluated\n');end
end



end
