
function J=toy_problem(ind,parameters,i,fig)
x=-10:0.1:10;
y=tanh(x.^3-x.^2-1);
% y2=y+(rand(size(y))-0.5)*500*parameters.artificialnoise;
y2 = y;
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
    

