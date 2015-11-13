function []=build_system(list_of_eqs,list_of_controls,parameters,thread_number)
n=length(list_of_eqs);
fid=fopen(['my_system' num2str(thread_number) '.m'],'w');
%% Construction of the file
fprintf(fid,['function f=my_system' num2str(thread_number) '(t,y)\n']);
	fprintf(fid,'if t==0; tic;end\n');
%% Construction of the Vector applied to the derived Jacobian
%	for i=1:n

%		for j=1:n
%			fprintf(fid,['Y(' num2str(i) ',' num2str(j) ')=y(' num2str(i+n+(j-1)*n) ');\n']);
%
%
%		end
%
%	end
fprintf(fid,'if toc<30\n');
%% Construction of the system
fprintf(fid,['f=zeros(' num2str(n) ',1);\n']);
for i=1:n
    if isempty(list_of_controls{i})
        eq=list_of_eqs{i};
    else
        eq=['(+ ' list_of_eqs{i} ' ' list_of_controls{i} ')'];
    end
    dumstring=readmylisp_to_formal_MLC(eq,parameters);
    fprintf(fid,['f(' num2str(i) ')= ' dumstring ';\n']);
end

%% Construction of the Jacobian
%	for i=1:n
%		%dumstring=[];
%		for j=1:n
%			if isempty(list_of_controls{i})
%				eq=list_of_eqs{i};
%			else
%				eq=['(+ ' list_of_eqs{i} ' ' list_of_controls{i} ')'];
%			end
%			devstring=readmylisp_to_formal(Derivate_My_Lisp(eq,j-1),1);
%			fprintf(fid,['Jac(' num2str(i) ',' num2str(j) ')=' devstring ';\n']);
%
%
%		end
%		%fprintf(fid,[dumstring '\n']);
%	end

%% Variational equation
%	fprintf(fid,['f(' num2str(n+1) ':' num2str(n*(n+1)) ')=Jac*Y;']);
fprintf(fid,'else\n');
fprintf(fid,'return\n');
fprintf(fid,'end\n');
fprintf(fid,'f=f(:);');
fclose(fid);




