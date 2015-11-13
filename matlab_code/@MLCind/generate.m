function mlcind=generate(mlcind,mlc_parameters,varargin)
% GENERATE     generates individual from scratch or from unfinished individual.
%
%   MLCIND.generate(MLC_PARAMETERS,MODE) creates an individual f using mode
%          MODE. MODE is a number which interpretation depends on the
%          MLCIND.type propertie. (Not designed to be played with by user, 
%          code dive for details)
%
%   MLCIND.generate(MLC_PARAMETERS,VALUE) creates an individual with
%   MLCIND.value VALUE.
%   
%   Copyright (C) 2015 Thomas Duriez (thomas.duriez@gmail.com)
%   Development version. Use, copy and diffusion of this pogram is subject 
%   to the author's agreement.
switch mlc_parameters.individual_type
    case 'tree'
        mlcind.type='tree';
        mlcind.value=['(root @' repmat(' @',[1 mlc_parameters.controls-1]) ')'];
        type=varargin{1};
        if ~ischar(type)
            for i=1:mlc_parameters.controls
                mlcind.value=generate_indiv_regressive_tree(mlcind.value,mlc_parameters,type);
            end
        else
            mlcind.value=type;
        end
        mlcind.value=simplify_and_sensors_tree(mlcind.value,mlc_parameters);
        string_hash = DataHash(mlcind.value);
        mlcind.hash=hex2num(string_hash(1:16));
        mlcind.formal=readmylisp_to_formal_MLC(mlcind.value,mlc_parameters);
        mlcind.complexity=tree_complexity(mlcind.value,mlc_parameters);
end
