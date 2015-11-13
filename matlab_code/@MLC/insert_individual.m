function mlc=insert_individual(mlc,ind)
%INSERT_INDIVIDUAL    Method of the MLC class. Allows insertion of known individual in a first generation
%   MLC_OBJ.INSERTINDIVIDUAL(IND) insert individual IND in the first
%   generation of the MLC object.
%
%   IND has to be a LISP expression compliant with the syntax used in the
%   MLC toolbox and contains only operations defined by <a
%   href="matlab:help OPSET">OPSET</a>.
%   An individual cannot be added in an other generation than the first
%   one. The first generation must not be filled or evaluated.
%
%   ex: 
%     mlc=MLC;
%     mlc.insert_individual('(+ S0 S1)');
%     mlc.insert_individual('(% 0.235 (tanh S0))');
%     mlc
%     mlc.population.individuals
%
%   See also MLC, GENERATE_POPULATION.
%
%   Copyright (C) 2013 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox
    if isempty(mlc.population);
        fit=zeros(mlc.parameters.size,1);
        idv=cell(mlc.parameters.size,1);
        idv{1}=ind;
        mlc.population.individuals=idv;
        mlc.population.occurence=fit*0+1;
        mlc.population.fitnesses=fit*0-1;
        mlc.population.generatedfrom=fit*0;
        mlc.population.evaluation_problem=fit*0;
        mlc.population.selected=fit*0;
        mlc.individual_table.individuals=cell(mlc.parameters.size*mlc.parameters.fgen,1);
        mlc.individual_table.occurence=zeros(mlc.parameters.size*mlc.parameters.fgen,1);
        mlc.individual_table.fitnesses=zeros(mlc.parameters.size*mlc.parameters.fgen,1);
        mlc.individual_table.nb=0;
    else
        ngen=length(mlc.population);
        if ngen>1
            fprintf('Inserting individual in MLC already started is not recommanded.\n');
            fprintf('Inserting individual in MLC already started is not implemented.\n');
        elseif max(mlc.population(1).fitnesses)>-1
            fprintf('Population already evaluated...\n');
            fprintf('Start a new MLC problem to manually add individuals\n');
        else
            estaempty=zeros(1,mlc.parameters.size);
            for i=1:mlc.parameters.size
                estaempty(i)=isempty(mlc.population(1).individuals{i});
            end
            if max(estaempty)==0
                fprintf('Population Full\n');
                fprintf('Cannot add new individual\n');
            else
                idx=find(estaempty==1,1);
                mlc.population(1).individuals{idx}=ind;
            end
        end
    end
end

