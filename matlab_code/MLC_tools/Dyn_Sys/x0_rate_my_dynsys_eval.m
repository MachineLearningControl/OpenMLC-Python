function [sys]=x0_rate_my_dynsys_eval(ind,parameters,ev,verb)

warning off
init=repmat(10^-6,[1 parameters.controls]);

build_system_lyapunov_eval(ind,parameters,ev);
systemthere=exist(['my_lyapunov_eval.m'],'file');
while systemthere==0
	systemthere=exist(['my_lyapunov_eval.m'],'file');
	pause(0.1)
end

[T,Y]=ode45(@my_lyapunov_eval,[0 100],init);

sys.Y=Y;












