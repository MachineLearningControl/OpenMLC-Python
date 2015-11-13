function a = readmylisp_to_formal_clean(expression,prout);
    expr=expression;
    fvig=find(expr==32);
    if isempty(fvig);
        idx=0;
        if expr(1)==83;
            axpr=expr(2:end);
            for i=1:length(axpr(1:end));
                idx=idx+(axpr(end-(i-1))-48)*10^(i-1);
            end;
            a=expr;
        else;
            a=expr;
            
            
        end;
    else;
    
        op=expr(2:fvig(1)-1);
	%fprintf(expr);fprintf('\n');
        stru=find(((cumsum(double(double(expr)==40))-cumsum(double(double(expr)==41))).*double(double(expr==32))==1));
	%fprintf(num2str(stru));fprintf('\n');
        a=0;

        if length(op)==1;

            if all(op == 43) % addition case;
                arg1=expr(stru(1)+1:stru(2)-1);
                arg2=expr(stru(2)+1:end-1); 
                   
                   a=['(' readmylisp_to_formal_clean(arg1,prout) ') + (' readmylisp_to_formal_clean(arg2,prout) ')'];
            elseif all(op==45);
                     arg1=expr(stru(1)+1:stru(2)-1);
                arg2=expr(stru(2)+1:end-1); 
                   
                   a=['(' readmylisp_to_formal_clean(arg1,prout) ') - (' readmylisp_to_formal_clean(arg2,prout) ')'];
            elseif all(op==42);
			%fprintf(expr);fprintf('\n');
                   arg1=expr(stru(1)+1:stru(2)-1);
                arg2=expr(stru(2)+1:end-1); 
                    a=['(' readmylisp_to_formal_clean(arg1,prout) ') * (' readmylisp_to_formal_clean(arg2,prout) ')'];
            elseif all(op==47);
                   arg1=expr(stru(1)+1:stru(2)-1);
                arg2=expr(stru(2)+1:end-1); 
                a=['(' readmylisp_to_formal_clean(arg1,prout) ') / (' readmylisp_to_formal_clean(arg2,prout) ')'];
                   
            end;

        else;
            if op(1)==115;
                arg=expr(stru(1)+1:end-1);
                a=['sin(' readmylisp_to_formal_clean(arg,prout) ')'];
                    
            elseif op(1)==101;
                    arg=expr(stru(1)+1:end-1);
                a=['exp(' readmylisp_to_formal_clean(arg,prout) ')'];
            elseif op(1)==99;
                    arg=expr(stru(1)+1:end-1);
                a=['cos(' readmylisp_to_formal_clean(arg,prout) ')'];
            elseif op(1)==116 && op(4)==104;
                    arg=expr(stru(1)+1:end-1);
                a=['tanh(' readmylisp_to_formal_clean(arg,prout) ')'];
            elseif op(1)==97 && op(4)==99;
                    arg=expr(stru(1)+1:end-1);
                a=['acos(' readmylisp_to_formal_clean(arg,prout) ')'];
            elseif op(1)==108;
                arg=expr(stru(1)+1:end-1);
                a=['log(' readmylisp_to_formal_clean(arg,prout) ')'];
                   
            end;
        end;
    end;
