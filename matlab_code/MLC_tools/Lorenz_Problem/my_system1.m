function f=my_system1(t,y)
tic
if toc<30
f=zeros(2,1);
f(1)= y(2)+(0.1).*(y(1));
f(2)= (0.1).*(y(2))-(y(1));
else
return
end
f=f(:);