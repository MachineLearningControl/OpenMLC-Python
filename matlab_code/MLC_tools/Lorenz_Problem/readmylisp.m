function a = readmylisp(s,expression);
    expr=expression;
    fvig=find(expr==32);
    if isempty(fvig);
        idx=0;
        if expr(1)==83;
            axpr=expr(2:end);
            for i=1:length(axpr(1:end));
                idx=idx+(axpr(end-(i-1))-48)*10^(i-1);
            end;
            a=s(idx+1);
        else;
            if expr(1)==45;
                axpr=expr(2:end);signus=-1;
            else;
                axpr=expr;
                signus=1;
            end;
            fp=find(axpr==46);
            ifp=find(1-(axpr==46));
            bxpr=axpr(ifp);
            for i=1:length(bxpr);
                    idx=idx+(bxpr(end-(i-1))-48)*10^(i-1);
            end;
            a=signus*idx*10^(fp-length(bxpr)-1);
            a=a;
            
            
        end;
    else;
    
        op=expr(2:fvig(1)-1);
        stru=find(((cumsum(double(double(expr)==40))-cumsum(double(double(expr)==41))).*double(double(expr==32))==1));
        a=0;

        if length(op)==1;

            if all(op == 43) % addition case;
                   for i=1:length(stru)-1;
                       
                       a=a+readmylisp(s,(expr(stru(i)+1:stru(i+1)-1)));
                   end;
                   a=a+readmylisp(s,(expr(stru(end)+1:end-1)));
            elseif all(op==45);
                    a=readmylisp(s,(expr(stru(1)+1:stru(2)-1)))-readmylisp(s,(expr(stru(2)+1:end-1)));
            elseif all(op==42);
                    a=readmylisp(s,(expr(stru(1)+1:stru(2)-1)))*readmylisp(s,(expr(stru(2)+1:end-1)));
            elseif all(op==47);
			
                    a=readmylisp(s,(expr(stru(1)+1:stru(2)-1)))/max(0.01,readmylisp(s,(expr(stru(2)+1:end-1))));
            end;

        else;
            if op(1)==115;
                    a=sin(readmylisp(s,(expr(stru(1)+1:end-1))));
            elseif op(1)==101;
                    a=exp(readmylisp(s,(expr(stru(1)+1:end-1))));
            elseif op(1)==99;
                    a=cos(readmylisp(s,(expr(stru(1)+1:end-1))));
            elseif op(1)==97 && op(4)==115;
                    a=tanh(readmylisp(s,(expr(stru(1)+1:end-1))));
            elseif op(1)==97 && op(4)==99;
                    a=acos(mod(readmylisp(s,(expr(stru(1)+1:end-1))),2)-1);
            elseif op(1)==108;
                    pb=readmylisp(s,(expr(stru(1)+1:end-1)));
                    if pb==0;
                        a=0;
                    else; 
                        a=log(abs(pb));
                    end;
            end;
        end;
    end;
