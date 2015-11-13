function b=my_log(arg1)
    protec=0.00001;
    if abs(arg1)>protec
        b=log(abs(arg1));
    else
        b=log(protec);
    end
end