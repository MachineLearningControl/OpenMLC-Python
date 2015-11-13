function a = tree_complexity(expression,gen_param,a)
if isempty(expression)
    a=0;
    return
end
if nargin>1
  ops=gen_param.opset;
else
  gen_param.opset=opset(1:10);
end
%ops=gen_param.opset;


expr=expression;
fvig=find(expr==' ');
if isempty(fvig);
    a=a+1;
else
    op=expr(2:fvig(1)-1);
    
    stru=[find(((cumsum(double(double(expr)=='('))-cumsum(double(double(expr)==')'))).*double(double(expr==' '))==1)) length(expr+1)];
    
    
    for i=1:length(ops)
        if strcmp(ops(i).op,op)
            a=a+ops(i).complexity;
            for j=1:ops(i).nbarg
                a=tree_complexity(expression(stru(j)+1:stru(j+1)-1),gen_param,a);
            end
        end
    end
    
    if strcmp(op,'root')
        nbct=length(stru)-1;
        if nbct>1
            a=zeros(1,nbct);
            for i=1:length(a)
                a(i)=tree_complexity(expression(stru(i)+1:stru(i+1)-1),gen_param,0);
            end
            a=sum(a);
        else
            a=tree_complexity(expression(stru(1)+1:stru(2)-1),gen_param,0);
        end
    end
end


end
