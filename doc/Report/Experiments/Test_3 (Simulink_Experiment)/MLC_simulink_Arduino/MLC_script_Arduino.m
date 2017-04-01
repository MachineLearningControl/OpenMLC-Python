        parameters.size=50;
        parameters.sensors=1;
        parameters.sensor_spec=0;
        parameters.controls=1;
        parameters.sensor_prob=0.33;
        parameters.leaf_prob=0.3;
        parameters.range=10;
        parameters.precision=4;
        parameters.opsetrange=1:3; 
        parameters.formal=1;
        parameters.end_character='';
        parameters.individual_type='tree';


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
        parameters.maxtries=10;
        parameters.mutation_types=1:4;


        %%  Optimization parameters
        parameters.elitism=1;
        parameters.probrep=0.1;
        parameters.probmut=0.4;
        parameters.probcro=0.5;
        parameters.selectionmethod='tournament';
        parameters.tournamentsize=7;
        parameters.lookforduplicates=1;
        parameters.simplify=0;
        parameters.cascade=[1 1];

        %%  Evaluator parameters 
        %parameters.evaluation_method='standalone_function';
        %parameters.evaluation_method='standalone_files';
        parameters.evaluation_method='mfile_standalone';
        parameters.evaluation_function='MLC_evaluator_Arduino_Simulink';
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
        parameters.preevaluation=1;
        parameters.preev_function='MLC_preevaluator_Arduino_Simulink';
        
        %% Problem definition
        parameters.problem_variables.signal_frequency=1;  % and not pulsation (sin(2*pi*frequency))
        parameters.problem_variables.signal_amplitude=1;  % factor in front of sinus, so half of pic to pic amp.
        parameters.problem_variables.signal_offset=3.3/2; % centered
        parameters.problem_variables.Tev=2/parameters.problem_variables.signal_frequency;   % 2 periods
        parameters.problem_variables.dT=0.001;            % 1Khz 
        parameters.problem_variables.gamma=0.1;           % quite high, you can test with 0.01 and 0.001 to see
        parameters.problem_variables.model_name='arduino_expe';
        %parameters.problem_variables.sensor_source='difference'; % MLC does not have acces to the original signal, just the difference
        parameters.problem_variables.sensor_source='signal_to_cancel'; % MLC has access to the original signal
        %parameters.problem_variables.goal='kill_perturbation'; % MLC tries to minimize the standart deviation
        parameters.problem_variables.goal='kill_signal'; % MLC tries to minimize the output
        parameters.problem_variables.summator_gain=-1; % multiplies the output of controller. Use -1 to get an inversor.
        
        
        %% MLC behaviour parameters 
        parameters.save=1;
        parameters.saveincomplete=1;
        parameters.verbose=2;
        parameters.fgen=250; 
        parameters.show_best=1;
        parameters.savedir=fullfile(pwd,'save_GP');