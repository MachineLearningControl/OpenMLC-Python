function dx=oscil(t,x)
    dx(1)=x(2);
    dx(2)=-x(1);
    dx=dx(:);