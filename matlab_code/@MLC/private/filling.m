function [idv,indiv_generated]=filling(idv,indiv_generated,n,gen_param,type)
verb=gen_param.verbose(1);

while indiv_generated<n;
    if verb>1;fprintf('Generating individual %i\n',indiv_generated+1);end
    if gen_param.controls==1
        m='°';
    else
        m=['(root' repmat(' °',[1 gen_param.controls]) ')'];
    end
    for i=1:gen_param.controls
        [m]=generate_indiv_regressive(m,gen_param,type); % all individual have maxsizefirst
    end
    if gen_param.simplify
        m=simplify_my_LISP(m,gen_param);
    end
    if gen_param.sensor_spec
        slist=sort(gen_param.sensor_list);
        for i=length(slist):-1:1
            m=strrep(m,['z' num2str(i-1)],['S' num2str(slist(i))]);
        end
    else
        for i=gen_param.sensors:-1:1
            m=strrep(m,['z' num2str(i-1)],['S' num2str(i-1)]);
        end
    end
    if verb>4; fprintf('Individual: %s\n',m);end
    preevok=1;
    if gen_param.preevaluation
        eval(['peval=@' gen_param.preev_function ';']);
        f=peval;
        preevok=feval(f,m);pause(0.1)
    end
    
    if sum(strcmp(m,idv))<1 && preevok
        idv{indiv_generated+1,1}=m;
        indiv_generated=indiv_generated+1;
        
        % fprintf('%i individus générés\n',indiv_generated);
    else
        if verb>1;fprintf('Individual discarded\n');end
    end
end