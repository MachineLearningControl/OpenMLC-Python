function J=dyn_sys_problem(ind,gen_param,i,~);
    verb=gen_param.verbose(6)-1;
    if verb>0;fprintf('(%i) Simulating ...\n',i);end
    try
        [sys]=x0_rate_my_dynsys(ind,gen_param,i,verb>1);		%% Evaluates individual
        if strncmp(lastwarn,'Failure',7);
            warning('reset')
            sys.crashed=1;
        else
            sys.crashed=0;
        end

        
        if verb>0;fprintf('(%i) Simulation finished.\n',i);end
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
        if verb>0;fprintf('(%i) Simulation crashed: ',i);end
        if strncmp(err.message,'Output argument f (and maybe others) not assigned during call to ',15)
            if verb>0;fprintf('Time is up\n');end
        else
            if verb>0;fprintf(['(%i) ' err.message '\n'],i);end
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
        LE=zeros(1,gen_param.controls);
    else
        LE=sys.LE;
    end
    if crashed==1;
        J=gen_param.badvalue;
        if verb>1;fprintf('(%i) Bad fitness: sim crashed\n',i);end
    elseif sum(LE)>0 || sum(isnan(LE))>0
        if verb>1;fprintf('(%i) ',i);fprintf('%f ',LE);fprintf('\n');end
        if verb>1;fprintf('(%i) Bad fitness: sum(LE) > 0\n',i);end
        J=gen_param.badvalue;
    else
        if verb>1;fprintf(['(%i) Max LE: ' num2str(max(LE)) '\n'],i);end
        cost=sys.Y(end,13);
        J=abs(20-max(LE));
        if verb>0;fprintf(['(%i) J= ' num2str(J) '\n'],i);end
    end
    if nargin==4
        [sys]=x0_rate_my_dynsys_eval(ind,gen_param,i,verb>1);
        plot3(sys.Y(:,1),sys.Y(:,2),sys.Y(:,3));
    end
end
