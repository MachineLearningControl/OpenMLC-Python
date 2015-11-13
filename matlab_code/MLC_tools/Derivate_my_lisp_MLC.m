function [a] = Derivate_my_lisp_MLC(expression,vari,gen_param)
if nargin>1
opset=gen_param.opset;
else
    load gen_param_default gen_param;
    opset=gen_param.opset;
end
%UNTITLED6 Summary of this function goes here
%   Detailed explanation goes here

    if isempty(strfind(expression,['S' num2str(vari)]))
        a='0';
    else
        expr=expression;
        fvig=find(expr==' ');
        if isempty(fvig);
            idx=0;
            if expr(1)=='S';
                axpr=expr(2:end);
                for i=1:length(axpr(1:end));
                    idx=idx+(axpr(end-(i-1))-48)*10^(i-1);
                end;
                if idx==vari; a='1'; else a='0';end
            else
                a='0';
            end;
        else

            op=expr(2:fvig(1)-1);
        stru=[find(((cumsum(double(double(expr)=='('))-cumsum(double(double(expr)==')'))).*double(double(expr==' '))==1)) length(expr+1)];	
            a=0;

            for i=1:length(opset)
                if strcmp(opset(i).op,op)
                    a=opset(i).derivlisp;
                    for j=1:opset(i).nbarg
                        a=strrep(a,['darg' num2str(j)],Derivate_my_lisp_MLC(expression(stru(j)+1:stru(j+1)-1),vari,gen_param));
                        a=strrep(a,['arg' num2str(j)],expression(stru(j)+1:stru(j+1)-1));
                    end
                end
            end
        end
    end
end

