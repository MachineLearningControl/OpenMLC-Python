function [m]=reparam(m,gen_param)
    preevok=0; 
    while preevok==0
        [m]=change_const(m,gen_param);
        preevok=1;
        if gen_param.preevaluation
            eval(['peval=@' gen_param.preev_function ';']);
            f=peval;
            preevok=feval(f,m);
        end
    end
end
	 

    
