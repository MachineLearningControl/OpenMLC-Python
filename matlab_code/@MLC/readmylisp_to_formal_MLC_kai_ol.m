function a = readmylisp_to_formal_MLC_kai_ol(expression,gen_param)
if isempty(expression)
    a=[];
    return
end
if nargin>1

else
    gen_param.opset=opset(1:10);
end
ops=gen_param.opset;


    expr=expression;
    fvig=find(expr==' ');
    if isempty(fvig);
        expr
        if expr(1)=='-'
            a=['(' expr ')'];
        elseif expr(1)='S'
            a=['t'];
        else
            a=expr;
            
            
        end;
    else 
        op=expr(2:fvig(1)-1);
	
        stru=[find(((cumsum(double(double(expr)=='('))-cumsum(double(double(expr)==')'))).*double(double(expr==' '))==1)) length(expr+1)];	
        a=0;    
        nbarg=0;
        for i=1:length(ops)
            if strcmp(ops(i).op,op)
                a=ops(i).litop;
                for j=1:ops(i).nbarg
                    nbarg=ops(i).nbarg;
                    a=strrep(a,['arg' num2str(j)],readmylisp_to_formal_MLC(expression(stru(j)+1:stru(j+1)-1),gen_param));
                end
            end
        end
        
        if strcmp(op,'root')
            nbct=length(stru)-1;
            if nbct>1
            a=cell(1,nbct);
            for i=1:length(a)
                a{i}=readmylisp_to_formal_MLC(expression(stru(i)+1:stru(i+1)-1),gen_param);
            end
            else
                a=readmylisp_to_formal_MLC(expression(stru(1)+1:stru(2)-1),gen_param);
            end
        end
        if nbarg>1    
        a=['(' a ')'];
        end
        
                
                    
                

      
    end;
