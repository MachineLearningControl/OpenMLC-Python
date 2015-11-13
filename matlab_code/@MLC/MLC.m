classdef MLC < handle
%MLC    TUCOROM Machine Learning Control class constructor. 
%   The MLC class is a handle class that implements <a href="matlab: 
% web('http://www.arxiv.org/abs/1311.5250')">a machine learning control problem</a>.
%
%   OBJ_MLC=MLC implements a new MLC problem using default options
%   OBJ_MLC=MLC('FILENAME') implements a MLC problem using options
%   defined in M-file FILENAME. 
%  
%   Ex:
%   TOY=MLC;TOY.go(3); % computes 3 générations for the "toy_problem"
%   TOY=MLC;TOY.go(13,1); % computes 13 générations for the "toy_problem"
%   with graphical output
%   LOR=MLC('GP_lorenz');LOR.go(2) % computes 2 générations of the "Lorenz Problem"
%
%   MLC properties:  
%      population   - (private) can not be modified by the user. Contains 
%                     all generations with fitnesses, occurences, parent
%                     individuals and generation method used.
%      parameters   - All parameters for all methods, including evaluation
%                     method and the problem to be solved. This property is
%                     a  <a href="matlab:help
%                     MLC_parameters">MLC_parameters</a> class.
%
%   MLC methods: 
%      generate_population   - generates first population.
%      evaluate_population   - evaluates current generation.
%      evolve_population     - breeds next generation.
%      go                    - performs MLC process until given generation.
%      show_convergence      - graph cost value repartion.
%      stats                 - display statistics.
%      show_stats            - graph statistics.
%      show_treedepth        - graph individual tree depth repartition.
%
%   Copyright (C) 2013 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox

    
    properties (SetAccess = private, Hidden)
        individual_table  
    end
    
    properties (SetAccess = private)
        population
        archive
    end
    
    properties
        parameters
    end
    
    methods (Hidden)
        obj=remove_badvalues(obj);
        obj=fill_population(obj);
        obj=addlistener(obj);
    end
    
    methods (Static)
        %parameters=set_MLC_parameters(filename);
        ops=opset(range)
    end
    
    methods
        obj=my_new_functionality(obj);
        obj=selection_stats(obj);
        obj=insert_individual(obj,ind)
        obj=set_population(obj,new_population);
        obj=generate_population(obj);
        obj=evaluate_population(obj,~);
        obj=evolve_population(obj,i);
        obj=go(obj,nb,fig);
        
        
        %obj=parameter_update(obj,i);
        %obj=pareto_sort(obj,~);
        
        show_convergence(obj,nhisto,Jmin,Jmax,linlog,sat,gen_range,axis);
        show_all(obj,fig);
        genealogy(obj,ngen,indiv,refvalues,axis);
        stats(obj,nb);
        show_treedepth(obj);
        show_stats(obj,loglin);
        show_best_indiv(obj,ngen);
        create_script(obj,filename);
        %% Constructor
        function obj=MLC(varargin)
           % obj.parameters=set_MLC_parameters(varargin{:});
            obj.parameters=MLC_parameters(varargin{:});
            obj.parameters.opset=opset(obj.parameters.opsetrange);
        end
        %% Display overload
        function disp(obj)
            if strcmp(inputname(1),'ans')
                fprintf('Done\n');
                return
            end
            %% Header
           
            fprintf('-------------------------------------\n')
            fprintf('    Machine Learning Control Object  \n')
            fprintf('-------------------------------------\n')
            
            fprintf('\n')
            %% Problem definition
            if  strfind(obj.parameters.evaluation_method,'files');
                fprintf('Problem linked with files :\n');
                fprintf('Directory: \t\t''%s''\n',obj.parameters.exchangedir);
                fprintf('Individual: \t\t''%s''\n',obj.parameters.indfile);
                fprintf('Cost function value: \t''%s''\n',obj.parameters.Jfile);
            else
            fprintf('Problem = ''%s''\n',obj.parameters.evaluation_function);
            end
            fprintf('\n');
            %% Problem parameters
            fprintf('Individuals: \t\t%i\n',obj.parameters.size);
            fprintf('Sensors: \t\t%i\n',obj.parameters.sensors);
            fprintf('Constants range: \t[-%.2f %.2f]\n',obj.parameters.range,obj.parameters.range);
            operations=[];
            for i=1:length(obj.parameters.opset)-1
                operations=[operations obj.parameters.opset(i).op ','];
            end
            operations=[operations obj.parameters.opset(length(obj.parameters.opset)).op];
            fprintf('Selected operations: \t(%s)\n',operations);
            fprintf('\n');
            %% Problem state
            if isempty(obj.population)
                fprintf('Population ');
                fprintf('empty');
                fprintf('. Start problem with ');
                fprintf([inputname(1) '.go(nb)']);
                fprintf('.\n');
                fprintf('Fill population with ');
                fprintf([inputname(1) '.generate_population']);
                fprintf('.\n');
            else
                ngen=length(obj.population);
                if min(obj.population(ngen).fitnesses)==-1; to_evaluate=1;else to_evaluate=0;end
                fprintf('%i generations filled, %i generations evaluated.\n',ngen,ngen-to_evaluate);
                if ngen-to_evaluate >0
                    fprintf('\n')
                    obj.stats(ngen-to_evaluate);
                    fprintf('\n')
                end
                fprintf(['Continue problem with ' inputname(1) '.go(nb) (nb >= ' num2str(ngen+1-to_evaluate) ').\n']);
                %% What to do now
                if to_evaluate              
                    fprintf(['Evaluate last generation with ' inputname(1) '.evaluate_population.\n']);
                else
                    fprintf(['Breed next generation with ' inputname(1) '.evolve_population.\n']);
                end
               
            end
            disp('Find <a href="matlab:help MLC">Help</a>');
            
        end
        
           
     
    end
    
end
