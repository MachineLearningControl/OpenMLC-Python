function [sys]=x0_rate_my_dynsys(ind,parameters,ev,verb)
warning off
init=repmat(10^-6,[1 parameters.controls]);

build_system_lyapunov(ind,parameters,ev);
systemthere=exist(['my_lyapunov_ev' num2str(ev) '.m'],'file');
while systemthere==0
	systemthere=exist(['my_lyapunov_ev' num2str(ev) '.m'],'file');
	pause(0.1)
end

if verb;fprintf('(%i) Calculating LEs\n',ev);end
if verb;fprintf(['(%i) Started at ' datestr(now,13) '\n'],ev);end
    tic
eval(['[T,LE,Y]=lyapunov(' num2str(parameters.controls) ',@my_lyapunov_ev' num2str(ev) ',@ode45,0,0.5,200,init,10);']);
if verb;fprintf(['(%i) done in ' num2str(toc) ' seconds\n'],ev);end

delete(['my_lyapunov_ev' num2str(ev) '.m']);
    LE=LE(end,:);



sys.LE=LE;

sys.Y=Y;












