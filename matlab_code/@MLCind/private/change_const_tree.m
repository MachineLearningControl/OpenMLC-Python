function a = change_const_tree(expression,gen_param)
if isempty(expression)
    a=[];
    return
end
if nargin>1

else
    gen_param.range=1;
    gen_param.precision=4;
    gen_param.opset=opset(1:10);
end
pattern=cell(1,11);
for i=1:10
pattern{i}=num2str(i-1);
end
pattern{11}='-';

ops=gen_param.opset;
    expr=expression;
    fvig=find(expr==' ');
    if isempty(fvig);
        if any(strcmp(expr(1),pattern))
            str_format = '';
            str_format = strcat(str_format, '% .');
            str_format = strcat(str_format, num2str(gen_param.precision));
            str_format = strcat(str_format, 'f');
            a=num2str((rand-0.5)*2*gen_param.range, str_format);
        else
            a=expr;   
        end;
    else 
        op=expr(2:fvig(1)-1);
        stru=[find(((cumsum(double(double(expr)=='('))-cumsum(double(double(expr)==')'))).*double(double(expr==' '))==1)) length(expr+1)];	
        a=0;    
        for i=1:length(ops)
            if strcmp(ops(i).op,op)
                a=['(' op];
                for j=1:ops(i).nbarg
                    a=[a ' ' change_const_tree(expression(stru(j)+1:stru(j+1)-1),gen_param)];
                end
                a=[a ')'];
            end
        end
        
        if strcmp(op,'root')
            nbct=length(stru)-1;
            a=['(' op];
            for j=1:nbct
                a=[a ' ' change_const_tree(expression(stru(j)+1:stru(j+1)-1),gen_param)];
            end
            a=[a ')'];
        end
    
                    
                

      
    end;
