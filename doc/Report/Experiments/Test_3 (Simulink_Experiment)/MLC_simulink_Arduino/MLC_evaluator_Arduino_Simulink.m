function J0=MLC_evaluator_Arduino_Simulink(idv,parameters,i,fig)
    tic
    %% Get data from problem_variables for readability

    model_name = parameters.problem_variables.model_name;
    gamma      = parameters.problem_variables.gamma;
    Tev        = parameters.problem_variables.Tev;
    dT         = parameters.problem_variables.dT;
    f          = parameters.problem_variables.signal_frequency;
    A          = parameters.problem_variables.signal_amplitude;
    offset     = parameters.problem_variables.signal_offset;
    sensing    = parameters.problem_variables.sensor_source;
    goal       = parameters.problem_variables.goal;
    gain       = parameters.problem_variables.summator_gain;
    
    data=0; 
    
    %% Transform individual to expressions
    
    idv_formal=idv.formal;
    idv_formal=strrep(idv_formal,'.*','*'); % simulink does not support .*
    idv_formal=strrep(idv_formal,'S0','u(1)');
    
  
   
   %% insert evaluation parameters
   
   try %% If simulink not open it won't work...
   
   
   set_param([model_name '/Arduino/Control_Function'],'expression',idv_formal) % control law
   catch
   open(model_name); % open itif necessary
   set_param([model_name '/Arduino/Control_Function'],'expression',idv_formal) % control law
   end
   
   set_param(model_name,'StopTime',num2str(Tev))
   set_param(model_name,'FixedStep',num2str(dT))
   set_param([model_name,'/Signal_to_cancel'],'SampleTime',num2str(dT))
   
   set_param([model_name,'/Signal_to_cancel'],'Amplitude',num2str(A))
   set_param([model_name,'/Signal_to_cancel'],'Bias',num2str(offset))
   set_param([model_name,'/Signal_to_cancel'],'frequency',num2str(f*2*pi))
   set_param([model_name,'/Ampli-op_sum/Gain'],'Gain',num2str(gain))
   
   switch sensing 
       case 'difference'
           set_param([model_name,'/sensor_selec'],'value',num2str(1))
       case 'signal_to_cancel'
           set_param([model_name,'/sensor_selec'],'value',num2str(0))
   end
   
   %% evaluate
   try % Simulink knows many ways of crashing.
   sim(model_name);
   
   %% Collect data. The Simulink model lets a 'data' variable in the workspace.
   
   T                = data(:,1);
   signal_to_cancel = data(:,2);
   sensor           = data(:,3);
   control          = data(:,4);
   
   %% Calculate J
   
   if T(end)==parameters.problem_variables.Tev; % To deal with Simulink clean crashes
       %% The goal is to nullify the oscillation, at the lowest cost
       
       switch goal
           case 'kill_perturbation'
               dJsensor=(sensor-mean(sensor)).^2; 
               dJnat=(signal_to_cancel-mean(signal_to_cancel)).^2; % without control
           case 'kill_signal'
               dJsensor=sensor.^2; 
               dJnat=signal_to_cancel.^2; % without control
       end
       dJcontrol=gamma * (control).^2; 
       Jnat=1/T(end)*cumtrapz(T,dJnat);
       Jsensor=1/T(end)*cumtrapz(T,dJsensor)/Jnat(end);  % normalized
       Jcontrol=1/T(end)*cumtrapz(T,dJcontrol)/Jnat(end); % normalized
       J=Jsensor+Jcontrol;
       J0=J(end);
       
       if length(find(control<=0)) > length(T)*0.9
           J0=parameters.badvalue; % cause I don't need that.
       end
       
       if length(find(control>3.3)) > length(T)*0.9 
           J0=parameters.badvalue; % cause I don't need that.
       end
       
       %% Forced standard output to quickly check if things are smooth
       if J0>parameters.badvalue
           fprintf('It worked badly\n')
       else
           fprintf('Calculation finished in %f seconds !!!!!!!!!!!!!!!!!!!!!!\n',toc) % <- easy to spot
           fprintf('J=%f\n',J0)
       end
   else
       J0=parameters.badvalue;
       fprintf('It stopped before\n')
   end
   
  if nargin>3 %% hey graphics !!!!!
      
     
      
      
      
        subplot(3,1,1)
        plot(T,signal_to_cancel,'-g','linewidth',1.2);hold on
        plot(T,sensor,'-b','linewidth',1.2);
        plot(T,control,'-r','linewidth',1.2);hold off
        
        ylabel('Voltages ($V$)','Fontsize',16,'interpreter','latex');
        legend('signal','ampli','control')
        
        subplot(3,1,2)
        plot(T,((sensor-mean(sensor)).^2)+gamma * abs(control).^2,'-k','linewidth',2);hold on
        plot(T,((sensor-mean(sensor)).^2),'-b','linewidth',1.2);
        plot(T,gamma * abs(control).^2,'-r','linewidth',1.2);hold off
        
        ylabel('$dJ$s','Fontsize',16,'interpreter','latex');
        legend('dJ total','dJ sensor','dJ control')
        subplot(3,1,3)
        plot(T,J,'-k','linewidth',1.2);hold on
        plot(T,Jsensor,'-b','linewidth',1.2)
        plot(T,Jcontrol,'-r','linewidth',1.2);hold off
        
        ylabel('$\int_0^t dJ \mathrm{d}t/J_{nat}$','Fontsize',16,'interpreter','latex');
        legend('total','sensor','control')
        
        for i=1:3
            subplot(3,1,i)
            xlabel('$T$ (s)','Fontsize',16,'interpreter','latex');
            set(gca,'Fontsize',12)
            grid on
        end
        
        if parameters.problem_variables.summator_gain==-1;
            tit_sum='difference';
        else
            tit_sum='summation';
        end

        if strcmp(parameters.problem_variables.sensor_source,'difference');
            tit_sensor='ampli-op output (blue curve)';
        else
            tit_sensor='initial signal (green curve)';
        end

        if strcmp(parameters.problem_variables.goal,'kill_signal')
            tit_goal='signal (RMS)';
        else
            tit_goal='perturbation (STD)';
        end

        subplot(3,1,1)
        title(sprintf('Ampli-op mode: %s,\n Sensor choice: %s,\n Goal to achieve: %s supression.\n This law: %s',tit_sum,tit_sensor,tit_goal,simplify_my_LISP(idv.value)));
        
        drawnow
        pause(1)
    end
   
   
   catch err
        fprintf('It crashed line %d of %s\n',err.stack(1).line,err.stack(1).name)
    fprintf(err.message)
       J0=parameters.badvalue;
       J=-1;
       T=-1;
       a=-1;
       s=-1;
       s_star=-1;
       b=-1;
       wd=-1;
       ws=-1;
   end   
 