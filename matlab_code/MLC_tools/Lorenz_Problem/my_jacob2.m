function Jac=my_jacob2(equa,cont,y)
	n=length(equa);
	for i=1:n
		%dumstring=[];
		for j=1:n
			if isempty(cont{i})
				eq=equa{i};
			else
				eq=['(+ ' equa{i} ' ' cont{i} ')'];
			end
			devstring=readmylisp_to_formal(Derivate_My_Lisp(eq,j-1),1);
			eval(['Jac(' num2str(i) ',' num2str(j) ')=' devstring ';']);
			
			
		end
		%fprintf(fid,[dumstring '\n']);
	end
