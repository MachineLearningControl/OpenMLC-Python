function J=lorenz_problem(ind,gen_param,i);
    
    verb=gen_param.verbose;
    contro=cell(1,3);
    contro{3}=ind;
    r=gen_param.problem_variables.r;
    gamma=gen_param.problem_variables.gamma;
    if verb;fprintf('(%i) Simulating ...\n',i);end
    try
        [sys]=x0_rate_my_lorentz(r,contro,i,verb>1);		%% Evaluates individual
        if strncmp(lastwarn,'Failure',7);
            warning('reset')
            sys.crashed=1;
        else
            sys.crashed=0;
        end

        
        if verb;fprintf('(%i) Simulation finished.\n',i);end
    catch err
        % A "normal" source of error is a too long evaluation.
        % The function is set-up to "suicide" after 30s.
        % In that case the error "Output argument f (and maybe others)
        % not assigned during call to..." gets out.
        % In that case we don't keep the trace.
        % In the other cases, the errors are sent to "errors_in_GP.txt"
        % with the numero of the defective individual.
        % In all cases, as the subroutine that erase the files crashes
        % we do it here.
        sys=[];
        sys.crashed=1;
        if verb;fprintf('(%i) Simulation crashed: ',i);end
        if strncmp(err.message,'Output argument f (and maybe others) not assigned during call to ',15)
            if verb;fprintf('Time is up\n');end
        else
            if verb;fprintf(['(%i) ' err.message '\n'],i);end
            system(['echo "' ind '">> errors_in_GP.txt']);
            system(['echo "' err.message '">> errors_in_GP.txt']);
        end
        try
            delete(['my_lyapunov_ev' num2str(i) '.m']);
        catch err
        end
        try
            delete(['my_lyapunov_ev' num2str(i) '.']);
        catch err
        end
    end
    crashed=sys.crashed;

    if crashed==1
        LE=zeros(1,3);
    else
        LE=sys.LE;
    end
    if crashed==1;
        J=gen_param.badvalue;
        if verb>1;fprintf('(%i) Bad fitness: sim crashed\n',i);end
    elseif sum(LE)>0 || sum(isnan(LE))>0
        if verb>1;fprintf('(%i) %f %f %f\n',i,num2str(LE));end
        if verb>1;fprintf('(%i) Bad fitness: sum(LE) > 0\n',i);end
        J=gen_param.badvalue;
    else
        if verb>1;fprintf(['(%i) Max LE: ' num2str(max(LE)) '\n'],i);end
        cost=sys.Y(end,13);
        J=abs(max(LE)) + gamma*cost;
        if verb;fprintf(['(%i) J= ' num2str(J) '\n'],i);end
    end
end
