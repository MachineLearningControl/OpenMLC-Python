function a = Derivate_My_Lisp(expression,vari);
    if isempty(findstr(['S' num2str(vari)],expression))
 	a='0';
	else
    expr=expression;
    fvig=find(expr==32);
    if isempty(fvig);
        idx=0;
        if expr(1)==83;
            axpr=expr(2:end);
            for i=1:length(axpr(1:end));
                idx=idx+(axpr(end-(i-1))-48)*10^(i-1);
            end;
            if idx==vari; a='1'; else; a='0';end
        else;
            a='0';
            
            
        end;
    else;
    
        op=expr(2:fvig(1)-1);
        stru=find(((cumsum(double(double(expr)==40))-cumsum(double(double(expr)==41))).*double(double(expr==32))==1));
        a=0;

        if length(op)==1;

            if all(op == 43) % addition case;
                arg1=expr(stru(1)+1:stru(2)-1);
                arg2=expr(stru(2)+1:end-1); 
                   
                   %a=['(' readmylisp_to_formal(arg1,prout) ') + (' readmylisp_to_formal(arg2,prout) ')'];
                   a=['(+ ' Derivate_My_Lisp(arg1,vari) ' ' Derivate_My_Lisp(arg2,vari) ')'];
	    elseif all(op==45);
                     arg1=expr(stru(1)+1:stru(2)-1);
                arg2=expr(stru(2)+1:end-1); 
                   
                   a=['(- ' Derivate_My_Lisp(arg1,vari) ' ' Derivate_My_Lisp(arg2,vari) ')'];
            elseif all(op==42);
                   arg1=expr(stru(1)+1:stru(2)-1);
                arg2=expr(stru(2)+1:end-1); 
                  a=['(+ (* ' Derivate_My_Lisp(arg1,vari) ' ' arg2 ') (* ' Derivate_My_Lisp(arg2,vari) ' ' arg1 '))'];
                    %a=['(' readmylisp_to_formal(arg1,prout) ') .* (' readmylisp_to_formal(arg2,prout) ')'];
            elseif all(op==47);
                   arg1=expr(stru(1)+1:stru(2)-1);
                arg2=expr(stru(2)+1:end-1); 
               % a=['(' readmylisp_to_formal(arg1,prout) ') ./ (max(0.01,(' readmylisp_to_formal(arg2,prout) ')))'];
               % d(f* 1/g)=f'* 1/g + f*(1/g)'=(+ (* D(f) g) (* f D(1/g)))
               % D(1/g)=-g'/g^2=(% (* -1 D(g)) (* g g))
                 oneovergprime=['(/ (* -1 ' Derivate_My_Lisp(arg2,vari) ') (* ' arg2 ' ' arg2 '))'];  
                 a1=['(* ' Derivate_My_Lisp(arg1,vari) ' ' arg2 ')'];
                 a2=['(* ' arg1 ' ' oneovergprime ')'];
                 a=['(+ ' a1 ' ' a2 ')']; 
                   
            end;

        else;
            if op(1)==115;
                arg=expr(stru(1)+1:end-1);
                %a=['sin(' readmylisp_to_formal(arg,prout) ')'];
                 a=['(* ' Derivate_My_Lisp(arg,vari) ' (cos ' arg '))'];   
            elseif op(1)==101;
                    arg=expr(stru(1)+1:end-1);
                %a=['exp(' readmylisp_to_formal(arg,prout) ')'];
                 a=['(* ' Derivate_My_Lisp(arg,vari) ' (exp ' arg '))']; 
            elseif op(1)==99;
                    arg=expr(stru(1)+1:end-1);
                %a=['cos(' readmylisp_to_formal(arg,prout) ')'];
		a=['(* ' Derivate_My_Lisp(arg,vari) ' (* -1 (sin ' arg ')))'];  
            elseif op(1)==97 && op(4)==115;
                    arg=expr(stru(1)+1:end-1);
              
                 %D(tanh(f)=f'*sech^2(f);
                 % sech(f)=2exp(-f)/(1-exp(-2f))=(% (* 2 (exp (- 0 f))) (- 1 (exp (* -2 f)))
                se1=['(* 2 (exp (- 0 ' arg ')))'];
                se2=['(- 1 (exp (* -2 ' arg ')))'];
                se=['(/ ' se1 ' ' se2 ')'];
                a=['(* ' se ' ' se ')']; 
            elseif op(1)==97 && op(4)==99;
                    arg=expr(stru(1)+1:end-1);
                %a=['acos(' readmylisp_to_formal(arg,prout) ')'];
            elseif op(1)==108;
                arg=expr(stru(1)+1:end-1);
                %a=['my_log(' readmylisp_to_formal(arg,prout) ')'];
                a=['(* ' Derivate_My_Lisp(arg,vari) ' (/ 1 ' arg '))'];  
                   
            end;
        end;
    end;
	if isempty(findstr('S',a));
       % a=num2str(readmylisp([],a));
	end
end;


