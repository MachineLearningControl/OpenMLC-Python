function preevok=pre_ev_chex2(m)
 
    S2=0:0.001:10; 
    S3=S2*10;
    S4=S2*100;
    b=eval(readmylisp_to_formal_MLC(m));
    b=b+S2*0;
    res=(b>0)+1-1;
    f=(0:2^15-1)/2^16*1000;
    
    fy=fft(res-mean(res),2^16);
    py=fy.*conj(fy);
    [~,k]=max(py(1:length(f)));
    dc=sum(res)/length(res);
    fmax=f(k);
    

    if max(abs(diff(res(S2>=9))))==0 || (fmax<30) || (fmax>250) || (dc<0.1) || (dc>0.9) % we check the last second (S2>=9)
        preevok=0;
    else
        preevok=1;
    end
end

