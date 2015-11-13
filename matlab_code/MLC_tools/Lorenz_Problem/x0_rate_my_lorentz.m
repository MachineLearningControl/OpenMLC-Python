function [sys]=x0_rate_my_lorentz(r,contro,ev,verb)
warning off
load lorentz
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

if verb;fprintf('(%i) Calculating LEs\n',ev);end
if verb;fprintf(['(%i) Started at ' datestr(now,13) '\n'],ev);end
    tic
eval(['[T,LE,Y]=lyapunov(3,@my_lyapunov_ev' num2str(ev) ',@ode45,0,0.5,200,[0 1 0],10);']);
if verb;fprintf(['(%i) done in ' num2str(toc) ' seconds\n'],ev);end

delete(['my_lyapunov_ev' num2str(ev) '.m']);
    LE=LE(end,:);



sys.LE=LE;

sys.Y=Y;












