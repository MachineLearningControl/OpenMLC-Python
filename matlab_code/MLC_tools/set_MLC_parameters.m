function parameters=set_MLC_parameters(filename)
%SET_MLC_PARAMETERS   Function for the constructor the MLC Class. Sets default values and calls parameters script.
%  PARAMETERS=set_MLC_parameters returns a pre-structure of parameters for
%  the MLC Class, with default values. (solves 'toy_problem').
%  PARAMETERS=set_MLC_parameters(FILENAME) returns a pre-structure of 
%  parameters for the MLC Class with default values overriden by
%  instructions in the FILENAME M-script. Ex: <a href="matlab:help GP_lorenz">GP_lorenz.m</a>
%
%   Copyright (C) 2013 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% DO NOT MODIFY THIS FILE, USE A SCRIPT TO CHANGE VALUES  %%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Individuals specific parameters
parameters.size=1000;
parameters.sensors=1;
parameters.controls=1;
parameters.range=10;
parameters.precision=4;
parameters.opsetrange=1:9; 


%%  GP algortihm parameters (CHANGE IF YOU KNOW WHAT YOU DO)
parameters.maxdepth=15;
parameters.maxdepthfirst=5;
parameters.mindepth=2;
parameters.mutmindepth=2;
parameters.mutmaxdepth=15;
parameters.mutsubtreemindepth=2;
parameters.generation_method='mixed_ramped_gauss';
parameters.gaussigma=3;
parameters.ramp=[2:8];
parameters.no_of_cascades=0;
parameters.no_of_gen_per_cascade=0;
parameters.archive_size=0;


%%  Optimization parameters
parameters.elitism=1;
parameters.probrep=0.1;
parameters.probmut=0.2;
parameters.procro=0.7;
parameters.selectionmethod='tournament';
parameters.tournamentsize=7;
parameters.lookforduplicates=1;
parameters.simplify=0;     
parameters.badvalues_elimswitch=1;

%%  Evaluator parameters 
parameters.evaluation_method='standalone_function';
%parameters.evaluation_method='standalone_files';
%parameters.evaluation_method='multithread_function';
parameters.evaluation_function='toy_problem';
parameters.indfile='ind.dat';
parameters.Jfile='J.dat';
parameters.exchangedir=fullfile(pwd,'evaluator0');
parameters.evaluate_all=0;
parameters.ev_again_best=0;
parameters.ev_again_nb=5;
parameters.ev_again_times=5;
parameters.artificialnoise=0;
parameters.execute_before_evaluation='';
parameters.badvalue=10^36;
parameters.badvalues_elim='first';
%parameters.badvalues_elim='none';
%parameters.badvalues_elim='all';

%% MLC behaviour parameters 
parameters.save=1;
parameters.verbose=[0,0,0,1,0,0];
parameters.fgen=250; 
parameters.show_best=1;

%% Call configuration script if present
if nargin==1
    fprintf(1,'%s\n',filename);
    run(filename)
end

end


