function b=my_div(arg1,arg2)
    protec=0.001;
    if abs(arg2)>protec
        b=arg1./arg2;
    else
        b=sign(arg2).*arg1./protec;
    end
end