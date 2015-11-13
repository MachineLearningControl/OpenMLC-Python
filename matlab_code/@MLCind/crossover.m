function [new_ind1,new_ind2,fail]=crossover(mlcind,mlcind2,mlc_parameters)
% CROSSOVER crosses two MLCind individuals.
%
%   [NEW_IND1,NEW_IND2,FAIL]=CROSSOVER(MLCIND1,MLCIND2,MLC_PARAMETERS);
%
%
%   Copyright (C) 2015 Thomas Duriez (thomas.duriez@gmail.com)
%   Development version. Use, copy and diffusion of this pogram is subject 
%   to the author's agreement.
    switch mlc_parameters.individual_type
        case 'tree'
            [m1,m2,fail]=crossover_tree(mlcind.value,mlcind2.value,mlc_parameters);
            new_ind1=MLCind;
            new_ind1.generate(mlc_parameters,m1);
            new_ind2=MLCind;
            new_ind2.generate(mlc_parameters,m2);
    end