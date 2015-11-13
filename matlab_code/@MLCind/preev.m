function pre=preev(mlcind,mlc_parameters)
    if mlc_parameters.preevaluation==0
        pre=1;
    else
        eval(['heval=@' mlc_parameters.preev_function ';']);
        pre=feval(heval,mlcind,mlc_parameters); 
    end
end