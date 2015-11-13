function mlc=generate_population(mlc)
% GENERATE_POPULATION initializes the population. (MLC2 Toolbox)
%
% OBJ.GENERATE_POPULATION updates the OBJ MLC2 object with an initial population 
%
% The function creates a  <a href="matlab:help MLCpop">MLCpop</a> object defining the population and launch its 
% creation method according to the OBJ.PARAMETERS content.
% The creation algorithm is implemented in the <a href="matlab:help MLCpop">MLCpop</a> class.
%
%   See also MLCPARAMETERS, MLCPOP
%
%   Copyright (C) 2015 Thomas Duriez (thomas.duriez@gmail.com)
%   Development version. Use, copy and diffusion of this pogram is subject 
%   to the author's agreement.
    mlc.population=MLCpop(mlc.parameters);
    [mlc.population(1),mlc.table]=mlc.population.create(mlc.parameters);
    mlc.population(1).state='created';