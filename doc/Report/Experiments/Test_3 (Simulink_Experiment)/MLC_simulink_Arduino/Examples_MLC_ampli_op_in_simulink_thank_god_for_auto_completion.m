function mlc_object=Examples_MLC_ampli_op_in_simulink_thank_god_for_auto_completion(n)
% EXAMPLES_MLC_AMPLI_OP_IN_SIMULINK_THANK_GOD_FOR_AUTO_COMPLETION is a very
% long name. It is also a function that helps configure a MLC2 problem
% revolving around the control of a dummy electronic experiment in
% Simulink. This file is just a conveniance thus I document it much better
% than other essential pieces of code. So it can work, you need:
%       - Matlab 2015 (maybe earlier, who knows)
%       - Simulink
%       - MLC_evaluator_Arduino_Simulink.m
%       - MLC_preevaluator_Arduino_Simulink
%       - MLC_script_Arduino
%       - arduino_expe.slx
%
% Calls:
%
% MLC2=EXAMPLES_MLC_AMPLI_OP_IN_SIMULINK_THANK_GOD_FOR_AUTO_COMPLETION run
% all problems
%
% MLC2=EXAMPLES_MLC_AMPLI_OP_IN_SIMULINK_THANK_GOD_FOR_AUTO_COMPLETION(PB_NB) runs
% the problem number PB_NB.
%
%
%     PB_NB   :  summator config   :   sensor    :   goal
% -----------------------------------------------------------------
%       1     :       ++           :  subs res.  :   sig. supress.
%       2     :       +-           :  subs res.  :   sig. supress.
%       3     :       ++           :  subs res.  :   fluct. supress.
%       4     :       +-           :  subs res.  :   fluct. supress.
%       5     :       ++           :  orig. sig. :   sig. supress.
%       6     :       +-           :  orig. sig. :   sig. supress.
%       7     :       ++           :  orig. sig. :   fluct. supress.
%       8     :       +-           :  orig. sig. :   fluct. supress.
%
% subs res. : ampli op output
% orig. sig.: signal to cancel/tame
% sig. supress. : the goal is to reach a null output
% fluct ouput   : the goal is to kill fluctuations
% ++            : control and signal are added
% +-            : control is substracted from signal
%
% Have fun, T.





if nargin<1
    n=1:8;
end

k=0;

mlc_object=MLC2('MLC_script_Arduino');
mlc_object=repmat(mlc_object,1,length(n));

for pb_nb=n
    k=k+1;
    
    if k>1
    mlc_object(k)=MLC2('MLC_script_Arduino');
    end
    
    if pb_nb/2==round(pb_nb/2)
        mlc_object(k).parameters.problem_variables.summator_gain=-1;
    else
        mlc_object(k).parameters.problem_variables.summator_gain=1;
    end
    
    if pb_nb<5
        mlc_object(k).parameters.problem_variables.sensor_source='difference';
    else
        mlc_object(k).parameters.problem_variables.sensor_source='signal_to_cancel';
    end
    
    if mod(ceil(pb_nb/2),2)==1
        mlc_object(k).parameters.problem_variables.goal='kill_signal';
    else
        mlc_object(k).parameters.problem_variables.goal='kill_perturbation';
    end
    
    mlc_object(k).go(15,1)
    figure(1)
    set(gcf,'units','normalized')
    set(gcf,'outerposition',[0 0 1 1])
    saveas(gcf,sprintf('Result_experiment_number_%i.png',pb_nb),'png');
end
