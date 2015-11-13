function preevok=pre_ev_chex(m)
S2=9:0.001:10; % we check the last second
b=eval(readmylisp_to_formal_MLC(m));
b=b+S2*0;
res=(b>0)+1-1;
if max(abs(diff(res)))==0
    preevok=0;
else
    preevok=1;
end


    