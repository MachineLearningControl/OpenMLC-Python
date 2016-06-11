classdef MLCind < handle
% MLCind constructor of the Machine Learning Control individual class.
% Part of the MLC2 Toolbox.
%
% Implements the individual type, value and costs. Archives history of
% evaluation and other informations.
%
% This class requires a valid MLCparameters object for most of its
% functionnalities.
%
% MLCind properties:
%    type                - type of individual (expression trees only now)
%    value               - string or matrice representing the individual 
%                          in the representation considered in 'type'
%    cost                - current cost value of the individual (average of
%                          cost_history)
%    cost_history        - history of raw values returned by the evaluation
%                          function
%    evaluation_time     - date and time (on the computer clock) of sending 
%                          of the individuals to the evaluation function
%    appearances         - number of time the individual appears in a
%                          generation
%    hash                - hash of 'value' to help finding identical
%                          individuals (will be turned to private)
%    formal              - matlab interpretable expression of the
%                          individual
%    complexity          - weighted addition of operators
%
% MLCind methods:
%    generate            - creates one individual according to the current
%    MLCparameters object and type of individual.
%    evaluate            - evaluates one individual according to the current
%    MLCparameters object.
%    mutate              - mutates one individual according to the current
%    MLCparameters object and type of individual.
%    crossover           - crosses two individuals according to the current
%    MLCparameters object and type of individuals.
%    compare             - stricly compares two individuals' values
%    textoutput          - display indiviudal value as text string
%    preev               - calls preevaluation function
%
%   See also MLCPARAMETERS, MLCTABLE, MLCPOP, MLC2
%
%   Copyright (C) 2015 Thomas Duriez (thomas.duriez@gmail.com)
%   Development version. Use, copy and diffusion of this pogram is subject 
%   to the author's agreement.
    
    
    properties
        type
        value
        cost
        cost_history
        evaluation_time
        appearences
        hash
        formal
        complexity
    end
    
    methods
        obj=generate(obj,MLC_parameters,varargin);
        obj=evaluate(obj,MLC_parameters,varargin);
        [obj_out,fail]=mutate(obj,MLC_parameters);
        [obj_out1,obj_out2,fail]=crossover(obj,obj2,MLC_parameters);
        out=compare(obj,obj2);
        textoutput(obj);
        pre=preev(obj,MLC_parameters);
        
        %% Constructor
        function obj=MLCind(varargin)
            obj.type='';
            obj.value=[];
            obj.cost=-1;
            obj.cost_history=[];
            obj.appearences=1;
            obj.hash=[];
            obj.formal='';
            obj.complexity=0;
            obj.evaluation_time=[];
        end
        
        %% getters for python tests
        function value=get_value(obj)
            value=obj.value;
        end
        
        function value=get_type(obj)
            value=obj.type;
        end

        function value=get_cost(obj)
            value=obj.cost;
        end
        
        function value=get_cost_history(obj)
            value=obj.cost_history;
        end
        
        function value=get_evaluation_time(obj)
            value=obj.evaluation_time;
        end
        
        function value=get_appearences(obj)
            value=obj.appearences;
        end
        
        function value=get_hash(obj)
            value=obj.hash;
        end
        
        function value=get_formal(obj)
            value=obj.formal;
        end
        
        function value=get_complexity(obj)
            value=obj.complexity;
        end
    end
end