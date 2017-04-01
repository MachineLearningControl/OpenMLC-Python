function pre_ev_is_a_success=MLC_preevaluator_Arduino_Simulink(idv,parameters)
    pre_ev_is_a_success=1;
    %% Get data from problem_variables for readability

    model_name = parameters.problem_variables.model_name;
    gamma      = parameters.problem_variables.gamma;
    Tev        = parameters.problem_variables.Tev;
    dT         = parameters.problem_variables.dT;
    f          = parameters.problem_variables.signal_frequency;
    A          = parameters.problem_variables.signal_amplitude;
    offset     = parameters.problem_variables.signal_offset;
    
    data=0; 
    
    %% Transform individual to expressions
    
    idv_formal=idv.formal;
   
    T=[0:dT:Tev];
    signal_to_cancel=offset+A*sin(2*pi*f*T);
    control=signal_to_cancel*0;
    idv_formal=strrep(idv_formal,'S0','signal_to_cancel');
    eval(sprintf('control=control+%s;',idv_formal));
    
    n=length(T);
    if length(find(control<=0)) > 0.9*n
        fprintf('REJECT!\n')
        pre_ev_is_a_success=0;
    end
    
    if length(find(control>3.3)) > 0.9*n
        fprintf('REJECT!\n')
        pre_ev_is_a_success=0;
    end
    
    
    
    
    