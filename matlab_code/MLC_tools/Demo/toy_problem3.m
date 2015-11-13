function J=toy_problem3(ind,parameters,i,~)
warning off
tend=30;
equa{1}='(+ y(2) (* 0.1 y(1)))';
equa{2}='(- (* 0.1 y(2)) y(1))';
cont=cell(1,2);
ind=strrep(ind,'S0','y(1)');
ind=strrep(ind,'S1','y(2)');
cont{2}=ind;

try
build_system(equa,cont,parameters,i);
systemthere=exist(['my_system' num2str(i) '.m'],'file');
while systemthere==0
	systemthere=exist(['my_system' num2str(i) '.m'],'file');
	pause(0.1)
end
eval(['f=@' 'my_system' num2str(i) ';']);
[T,y]=ode45(f,0:0.01:tend,[0 1]);
b=y(:,1)*0;
k=readmylisp_to_formal_MLC(ind,parameters);
k=strrep(k,'y(1)','y(:,1)');

k=strrep(k,'y(2)','y(:,2)');
eval(['b= ' k '+y(:,1)*0;'])
tev=0;
%fprintf('%s\n',num2str(length(b)))
if T(end)==30;
J=trapz(T(T>tev),sum(y(T>tev,:).^2,2)+0.01*b(T>tev).^2)/(tend-tev);
else
    J=parameters.badvalue;
end
delete(['my_system' num2str(i) '.m']);

catch err 
   
    J=parameters.badvalue;
%     fprintf('%s\n',ind)
%     fprintf('%s\n',err.message)
%     
% 
%     for i=1:length(err.stack)
%         fprintf('file: %s\n',err.stack(i).file);
%         fprintf('line: %i\n',err.stack(i).line);
%     end
    delete(['my_system' num2str(i) '.m']);
systemthere=exist(['my_system' num2str(i) '.m'],'file');
%return
while systemthere==1
	systemthere=exist(['my_system' num2str(i) '.m'],'file');
    delete(['my_system' num2str(i) '.m']);
	pause(0.1)
end
end

if nargin==4
    subplot(2,1,1)
    plot(T,sum(y.^2,2),T,b.^2)
    set(gca,'Yscale','log');
    subplot(2,1,2)
    plot(y(:,1),y(:,2))
    
end
    
