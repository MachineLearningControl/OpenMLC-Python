function m=show_best(mlc,fig)
% SHOW_BEST display current best individual (MLC2 Toolbox)
%
%   IND_OBJ=MLC_OBJ.SHOW_BEST(N) returns the <a href="matlab:help MLCind">MLCind</a> object corresponding to
%       the best individual. Additionaly calls the evaluation function avec
%       N as fourth argument, which can be used to implement graphic
%       functions.
%
%   Copyright (C) 2015 Thomas Duriez (thomas.duriez@gmail.com)
%   Development version. Use, copy and diffusion of this pogram is subject 
%   to the author's agreement.
    if nargin<2
        fig=1;
    end
    eval(['heval=@' mlc.parameters.evaluation_function ';']);
            f=heval;
     [~,idx]=min(mlc.population(length(mlc.population)).costs);
     m=mlc.table.individuals(mlc.population(length(mlc.population)).individuals(idx));        
    feval(f,m,mlc.parameters,1,fig);