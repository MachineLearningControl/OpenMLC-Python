function [sys]=x0_rate_my_lorentz_check(r,contro,ev)
load lorentz
%warning off
idx=findstr('28',equa{2});
part1=equa{2}(1:idx-1);
part2=equa{2}(idx+2:end);
equa{2}=[part1 num2str(r) part2];
cont=contro;
init(:,1)=[0 0 0];
if r<=1 
init(:,2)=init(:,1)+rand(3,1);
init(:,3)=init(:,1)+rand(3,1);
else
init(:,2)=[sqrt(8/3*(r-1)) sqrt(8/3*(r-1)) r-1];
init(:,3)=[-sqrt(8/3*(r-1)) -sqrt(8/3*(r-1)) r-1];
end

build_system_lyapunov_lor(equa,cont,ev);
systemthere=exist(['my_lyapunov_ev' num2str(ev) '.m'],'file');
while systemthere==0
	systemthere=exist(['my_lyapunov_ev' num2str(ev) '.m'],'file');
	pause(0.1)
end
system(['sed -i ''s:^if toc<30*:if 1>0:'' my_lyapunov_ev' num2str(ev) '.m']);

build_system_newton(equa,cont,100+ev);

systemthere=exist(['my_lyapunov_ev' num2str(100+ev) '.m'],'file');
while systemthere==0
	systemthere=exist(['my_lyapunov_ev' num2str(100+ev) '.m'],'file');
	pause(0.1)
end
%eval(['[T,Y] = lyapunov(3,@my_lyapunov_ev' num2str(645) ',@ode45,0,0.5,200,[0 1 0],10);'])
fprintf('Calculating LEs\n')
fprintf(['Started at ' datestr(now,13) '\n']);tic
eval(['[T,LE,Y]=lyapunov(3,@my_lyapunov_ev' num2str(ev) ',@ode45,0,0.5,200,[0 1 0],10);']);
fprintf(['done in ' num2str(toc) ' seconds\n']);
fprintf(['LE : %f %f %f\n'],LE(end,:));
for i=1:3
fprintf(['Newton descent on point number ' num2str(i) '\n']);tic
eval(['fp(:,i)=my_newton(equa,cont,@my_lyapunov_ev' num2str(100+ev) ',init(:,i));']);
fprintf(['done in ' num2str(toc) ' seconds\n']);
fprintf(['Stability around point ' num2str(i) '\n']);tic
lambda(:,i)=eig(my_jacob2(equa,cont,fp(:,i)));
fprintf(['done in ' num2str(toc) ' seconds\n']);
end
LE=LE(end,:);
system(['sed -i ''s:^function.*:function f=my_lyapunov_ev' num2str(100+ev) '(t,y):'' my_lyapunov_ev' num2str(100+ev) '.m']);
eval(['[T,Y]=ode45(@my_lyapunov_ev' num2str(100+ev) ',[0:0.01:200],[0 1 0]);']);

%system(['rm my_lyapunov_ev' num2str(ev) '.m my_lyapunov_ev' num2str(100+ev) '.m']);


for i=1:3
FP(i).stable=sum((lambda(:,i)==real(lambda(:,i))).*lambda(:,i)<0);
FP(i).unstable=sum((lambda(:,i)==real(lambda(:,i))).*lambda(:,i)>0);
FP(i).oscst=sum((lambda(:,i)~=real(lambda(:,i))).*real(lambda(:,i))<0);
FP(i).oscunst=sum((lambda(:,i)~=real(lambda(:,i))).*real(lambda(:,i))>0);
end
if strncmp(lastwarn,'Failure',7);
    warning('reset')
end
sys.fp=fp;
sys.lambda=lambda;
sys.LE=LE;
sys.FP=FP;
sys.Y=Y;
sys.T=T;













