function out=compare(mlcind,mlcind2)
% COMPARE     compares two MLCind value properties.
%
%   ISEQUAL=COMPARE(MLCIND1,MLCIND2) returns 1 if both values are equal.
%
%   Copyright (C) 2015 Thomas Duriez (thomas.duriez@gmail.com)
%   Development version. Use, copy and diffusion of this pogram is subject 
%   to the author's agreement.
    switch mlcind.type
        case 'tree'
            out=strcmp(mlcind.value,mlcind2.value);
    end
end