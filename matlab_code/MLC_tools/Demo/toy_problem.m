function J=toy_problem(ind,parameters,i,fig)
x=-10:0.1:10;
y=tanh(x.^3-x.^2-1);
%y2=[-1.0489e+03 -9.3351e+02 -5.4344e+02 -4.7540e+02 -2.3664e+02 -1.8679e+02 -9.3592e+01 -3.4399e+01 -1.1531e+01 -3.6636e+00 0.0000e+00 1.1149e+00 5.7326e+00 1.9196e+01 3.9107e+01 9.7226e+01 1.4641e+02 2.9184e+02 5.2222e+02 5.7480e+02 8.4005e+02];
y2=y+(rand(size(y))-0.5)*500*parameters.artificialnoise;
y3=y2*0;
try
m=ind.formal;
m=strrep(m,'S0','x');
eval(['y3=' m ';'])
J=sum((y2-y3).^2);%./(1+abs(x.^2)))/length(y2)+length(m)/10^5;
catch err
    J=parameters.badvalue;
    fprintf(err.message);
end
% if rand<0.001
%     J=10^-2;
% end

if nargin==4
    subplot(2,1,1)
    plot(x,y,x,y2,'*',x,y3)
    subplot(2,1,2)
    plot(x,sqrt((y-y3).^2./(1+abs(x.^2))),'*r')
    set(gca,'yscale','log')
end
    

