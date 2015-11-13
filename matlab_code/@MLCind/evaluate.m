function mlcind=evaluate(mlcind,J,evtime)
% EVALUATE     updates the individual with an evaluation.
%
%   ISEQUAL=COMPARE(MLCIND1,MLCIND2) returns 1 if both values are equal.
%
%   Copyright (C) 2015 Thomas Duriez (thomas.duriez@gmail.com)
%   Development version. Use, copy and diffusion of this pogram is subject 
%   to the author's agreement.
    if nargin<3
        evtime=now;
    end
    mlcind.cost_history=[mlcind.cost_history J];
    mlcind.evaluation_time=[mlcind.evaluation_time evtime];
    mlcind.cost=mean(mlcind.cost_history);
end