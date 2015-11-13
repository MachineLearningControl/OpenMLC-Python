classdef MLC2 < handle
% MLC2 constructor of the Machine Learning Control 2 class.
%   The MLC2 class is a handle class that implements <a href="matlab: 
%   web('http://www.arxiv.org/abs/1311.5250')">a machine learning control problem</a>.
%
%   OBJ_MLC=MLC2 implements a new MLC problem using default options
%   OBJ_MLC=MLC2('FILENAME') implements a MLC problem using options
%   defined in M-file FILENAME.
%
%   Ex:
%   TOY=MLC2;TOY.go(3); % computes 3 generations for the default problem.
%   TOY=MLC2;TOY.go(13,1); % computes 13 generations for the default problem
%   with graphical output.
%   TOY2=MLC('toy2_cfg');TOY2.go(2) % computes 2 generations of the problem
%   defined in toy2_cfg.m file.
%
%   MLC2 properties:
%      <a href="matlab:help MLCtable">table</a>        - contains the individual database as a <a href="matlab:help MLCtable">MLCtable</a> object.
%      <a href="matlab:help MLCpop">population</a>   - contains one <a href="matlab:help MLCpop">MLCpop</a> object per generation.
%      <a href="matlab:help MLCparameters">parameters</a>   - contains the parameters as a <a href="matlab:help MLCparameters">MLCparameters</a> object.
%      version      - current version of MLC2.
%
%   MLC2 methods:
%      generate_population  -  generate the initial population. 
%      evaluate_population  -  evaluate current unevaluated population.
%      evolve_population    -  evolve current evaluated population.
%      go                   -  automatize generation evaluation and evolution.
%      genealogy            -  draws the genealogy of the individuals.
%      show_best            -  returns and shows the best individual.
%      show_convergence     -  show the repartition of the population costs.
%
%   See also MLCPARAMETERS, MLCTABLE, MLCPOP, MLCIND
%
%   Copyright (C) 2015 Thomas Duriez (thomas.duriez@gmail.com)
%   Development version. Use, copy and diffusion of this pogram is subject 
%   to the author's agreement.
   
    properties
        table
        population
        parameters
        version
    end
    
    methods
        obj=generate_population(obj);
        obj=evaluate_population(obj,n);
        obj=evolve_population(obj,n);
        obj=go(obj,n,figs);
        genealogy(obj,ngen,idv);
        m=show_best(obj,fig);
        show_convergence(obj,nhisto,Jmin,Jmax,linlog,sat,gen_range,axis);
        
        function obj=MLC2(varargin)
            vers = 'alpha.2.5';
            obj.table=[];
            obj.population=[];
            obj.parameters=MLCparameters(varargin{:});
            obj.parameters.opsetrange
            obj.parameters.opset=opset(obj.parameters.opsetrange);
            obj.version=vers;
            
            
            
            
            
            
            
            
            
        end
    end
end
            