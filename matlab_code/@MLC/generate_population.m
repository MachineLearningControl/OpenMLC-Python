function [mlc]=generate_population(mlc)
%GENERATE_POPULATION    Method of the MLC class. Generates first population.
%
%   MLC_OBJ.GENERATE_POPULATION generates the first population of the MLC
%   OBJECT.
%
%   All options are set in the MLC object (See <a href="matlab:help MLC">MLC</a>). 
%
%   Implemented: - Minimum and maximum initial depth.
%                - Simplification of LISP expression.
%                - Diverse depth/completness rates. (See <a href="matlab:help MLC/parameters">MLC parameters</a>).
%
%   See also MLC, EVALUATE_POPULATION, EVOLVE_POPULATION, SIMPLIFY_MY_LISP
%
%   Copyright (C) 2013 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox

%% Some stuff
    verb=mlc.parameters.verbose;
    gen_param=mlc.parameters;  %% we will mess with some parameters so we replicate to not overwrite.
    
%% From empty or just filling ?    
    if isempty(mlc.population)
        if verb>0;fprintf('Generating new population\n');end
        idv=cell(gen_param.size,1);
    else
        if verb>0;fprintf('Completing new population\n');end
        nind=length(mlc.population(1).individuals);
        to_fill=zeros(1,nind);
        for i=1:nind
            to_fill(i)=isempty(mlc.population(1).individuals{i});
        end
        idx_fofill=find(to_fill);
        idv=cell(length(idx_fofill),1);
    end

%% Start filling
    
    indiv_generated=0;
    tic
    if verb>1;fprintf(['Using "' mlc.parameters.generation_method '" method\n']);end
    switch mlc.parameters.generation_method
        case 'random_maxdepth'
            [idv]=filling(idv,indiv_generated,length(idv),gen_param,0);
        case 'fixed_maxdepthfirst'
            [idv]=filling(idv,indiv_generated,length(idv),gen_param,1);
        case 'random_maxdepthfirst'
            [idv]=filling(idv,indiv_generated,length(idv),gen_param,2);
        case 'full_maxdepthfirst'
            [idv]=filling(idv,indiv_generated,length(idv),gen_param,3);
        case 'mixed_maxdepthfirst' %% 50% at full, 50% random, at maxdepthfirst
            [idv,indiv_generated]=filling(idv,indiv_generated,round(length(idv)/2),gen_param,1);
            [idv]=filling(idv,indiv_generated,(length(idv)),gen_param,3);
        case 'mixed_ramped_even'        %% 50% full, 50% random with ramped depth
            n=round(linspace(length(idv)/(length(mlc.parameters.ramp)*2),length(idv),length(mlc.parameters.ramp)*2));
            for i=1:length(mlc.parameters.ramp)
                gen_param.maxdepthfirst=mlc.parameters.ramp(i);
                [idv,indiv_generated]=filling(idv,indiv_generated,n(2*i-1),gen_param,1);
                [idv,indiv_generated]=filling(idv,indiv_generated,n(2*i),gen_param,3);
            end
        case 'mixed_ramped_gauss'   %% 50% full 50% random gaussian distrib
            minde=min(mlc.parameters.ramp);
            maxde=max(mlc.parameters.ramp);
            center=round((maxde+minde)/2);
            r=mlc.parameters.ramp;
            sigma=mlc.parameters.gaussigma;
            g=(exp(-((r-center).^2)/sigma^2)/sum(exp(-((r-center).^2)/sigma^2)))*length(idv);
            n=[0 round(cumsum(g))];
            for i=1:length(n)-1;
                gen_param.maxdepthfirst=mlc.parameters.ramp(i);
                [idv,indiv_generated]=filling(idv,indiv_generated,n(i)+round((n(i+1)-n(i))/2),gen_param,1);
                [idv,indiv_generated]=filling(idv,indiv_generated,n(i+1),gen_param,3);
            end
            
    end
            

    %% Population generated, allocation in MLC object.
    
    if verb>1;fprintf(['Population generated in ' num2str(toc,'%.1f') ' seconds\n']);end
    if isempty(mlc.population)
        mlc.population.individuals=idv;
        mlc.population.occurence=zeros(size(idv))*0+1;
        mlc.population.fitnesses=zeros(size(idv))*0-1;
        mlc.population.generatedfrom=zeros(size(idv))*0;
        mlc.population.evaluation_problem=zeros(size(idv))*0;
        mlc.population.selected=zeros(size(idv))*0;
        if strcmp(mlc.parameters.selectionmethod,'pareto')
            mlc.population.complexity=zeros(size(idv))*0+100;
        end
        mlc.individual_table.individuals=cell(gen_param.size*gen_param.fgen,1);
        mlc.individual_table.occurence=zeros(gen_param.size*gen_param.fgen,1);
        mlc.individual_table.fitnesses=zeros(gen_param.size*gen_param.fgen,1);
        mlc.individual_table.nb=0;
    else
        mlc.population.individuals(idx_fofill)=idv;
        mlc.population.occurence(idx_fofill)=zeros(size(idv))*0+1;
        mlc.population.fitnesses(idx_fofill)=zeros(size(idv))*0-1;
        mlc.population.generatedfrom(idx_fofill)=zeros(size(idv))*0;
        mlc.population.evaluation_problem(idx_fofill)=zeros(size(idv))*0;
        mlc.population.selected(idx_fofill)=zeros(size(idv))*0;
        if strcmp(mlc.parameters.selectionmethod,'pareto')
            mlc.population.complexity(idx_fofill)=zeros(size(idv))*0+100;
        end
    end
    %% Create archive iff archive_size>0 on the first call of the function
    if mlc.parameters.archive_size>0 && isempty(mlc.archive)
        %indiv_generated=0;
        %idv=cell(mlc.parameters.archive_size,1);
        %[idv]=filling(idv,indiv_generated,length(idv),gen_param,3);
        mlc.archive.individuals=cell(mlc.parameters.archive_size,1);%idv(1:mlc.parameters.archive_size);cell(mlc.parameters.archive_size,1);
        mlc.archive.occurence=zeros(mlc.parameters.archive_size,1)*0+1;
        mlc.archive.fitnesses=zeros(mlc.parameters.archive_size,1)*0+mlc.parameters.badvalue;
        if strcmp(mlc.parameters.selectionmethod,'pareto')
            mlc.archive.complexity=zeros(mlc.parameters.archive_size,1)*0+100;
        end
    end
end
