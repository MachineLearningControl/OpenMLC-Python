function []=build_system_lyapunov(ind,parameters,thread_number)
	n=parameters.controls;
	fid=fopen(['my_lyapunov_ev' num2str(thread_number) '.m'],'w');
%% Construction of the file
    fprintf(fid,['function f=my_lyapunov_ev' num2str(thread_number) '(t,y)\n']);
	%fprintf(fid,'if t==0; tic;end\n');
%% Construction of the Vector applied to the derived Jacobian
% 	for i=1:n
% 		
% 		for j=1:n
% 			fprintf(fid,['Y(' num2str(i) ',' num2str(j) ')=y(' num2str(i+n+(j-1)*n) ');\n']);
% 			
% 			
% 		end
% 		
% 	end
%fprintf(fid,'if toc<30\n');
%% Construction of the system
	fprintf(fid,['f=zeros(' num2str(n*(n+1)) ',1);\n']);
%	fprintf(fid,['b=zeros(' num2str(n) ',1);\n']);
    a=readmylisp_to_formal_MLC(ind,parameters);
	for i=1:n
		fprintf(fid,['f(' num2str(i) ')= ' a{i} ';\n']);
	end
         
                
%% Construction of the Jacobian
 stru=[find(((cumsum(double(double(ind)=='('))-cumsum(double(double(ind)==')'))).*double(double(ind==' '))==1)) length(ind+1)];
 list_of_eqs=cell(1,parameters.controls);
%  for i=1:parameters.controls
%      list_of_eqs{i}=ind(stru(i)+1:stru(i+1)-1);
%  end
% 	for i=1:n
% 		%dumstring=[];
% 		for j=1:n
% 			%fprintf(['eq: ' list_of_eqs{i} '\n']);
% 			%fprintf(['control: ' list_of_controls{i} '\n']);
% 			
% 				eq=list_of_eqs{i};
% 			
% 			%fprintf(['compond: ' eq '\n']);
% 			
% 			%fprintf(num2str(j-1));fprintf('\n')
% 			%fprintf(eq);fprintf('\n')
% 			devstring=readmylisp_to_formal(Derivate_My_Lisp(eq,j-1),1);
% 			fprintf(fid,['Jac(' num2str(i) ',' num2str(j) ')=' devstring ';\n']);
% 			
% 			
% 		end
% 		%fprintf(fid,[dumstring '\n']);
% 	end

%% Variational equation
	%fprintf(fid,['f(' num2str(n+1) ':' num2str(n*(n+1)) ')=Jac*Y;\n']);
	%fprintf(fid,['f(' num2str(n*(n+1)+1) ')=sum(b.^2)/200;\n']);
%  fprintf(fid,'else\n');
%         fprintf(fid,'return\n');
%         fprintf(fid,'end\n');
	fclose(fid);
	pause(0.2)
				
	

	
