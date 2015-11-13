function draw_my_tree_article(expression,initpos,prof,list_of_ops)
expression=strrep(expression,'%','/');
simple=0;
hold on
col=[0 0 0];pcol=[1 0 0];
markcol='none';
l=1;
 expr=expression;
    fvig=find(expr==32);
    if isempty(fvig);
        if expr(1)=='S'
            ttex=expr;
        else
             while expr(1)=='('
                expr=expr(2:end);
            end
            while expr(end)==')'
                expr=expr(1:end-1);
            end
            
            for i=1:length(list_of_ops)
                if strcmp(expr,list_of_ops{i})
                    col=[0 0 0];markcol=pcol;
                end
            end
           
            constant=str2double(expr);
            ttex=num2str(constant,'%.3f');
            %ttex=expr;
           
        end
       
    else
    
        op=expr(2:fvig(1)-1);
        if strcmp(op,'root')
             stru=find(((cumsum(double(double(expr)==40))-cumsum(double(double(expr)==41))).*double(double(expr==32))==1));
             struc=[stru length(expr)+1];
             length(stru)
             for i=1:length(stru)
                 arg=expr(struc(i)+1:struc(i+1)-1);
                 cpos=initpos-[(length(stru)-1)/2-(i-1) l]; 
                 plot([initpos(1) cpos(1)],[initpos(2) cpos(2)],'k')
                 draw_my_tree_article(arg,cpos,prof+1,list_of_ops)
             end
             ttex='root';
        else

        
            for i=1:length(list_of_ops)
                if strcmp(op,list_of_ops{i})
                    col=[0 0 0];markcol=pcol;
                end
            end
            ttex=op;
        
        stru=find(((cumsum(double(double(expr)==40))-cumsum(double(double(expr)==41))).*double(double(expr==32))==1));
        
        if length(stru)==2;
            arg1=expr(stru(1)+1:stru(2)-1);
            arg2=expr(stru(2)+1:end-1);
                    
                    cpos=initpos-[-l/(2)^(prof-1) l]; 
                    plot([initpos(1) cpos(1)],[initpos(2) cpos(2)],'k')
                    draw_my_tree_MLC(arg1,cpos,prof+1,list_of_ops)
                    cpos=initpos-[l/(2)^(prof-1) l]; 
                    plot([initpos(1) cpos(1)],[initpos(2) cpos(2)],'k')
                    draw_my_tree_MLC(arg2,cpos,prof+1,list_of_ops)

        else
            expr
            arg1=expr(stru(1)+1:end-1);
            cpos=initpos-[0 l];
            plot([initpos(1) cpos(1)],[initpos(2) cpos(2)],'k')
            draw_my_tree_MLC(arg1,cpos,prof+1,list_of_ops)
            
        end;
    end
    end;

    %plot(initpos(1),initpos(2),'o','color',col,'markersize',30,'markerfacecolor',markcol)
   % system('cat subsel.tab | wc -l > nbt.txt');
    %cat subsel.tab | grep `echo '  ' | sed 's/\*/\\\*/g'` | wc -l
  %  system(['cat subsel.tab | grep `echo ''' ttex ''' | sed ''s/\*/\\\*/g''` | wc -l> nb2.txt']);
    
    if simple==1
    idx=strfind(ttex,'^');
    if length(idx)==1
    ttex=ttex(idx+1:end);
    else
        ttex=ttex(idx(1)+1:idx(2)-1);
    end
    end
    marktype='o';
    if ttex(1)=='S'
        marktype='square';
    end
    
    %markcol=myred(floor((nb2/nbt)*63+1),:)*0+1;
    plot(initpos(1),initpos(2),'marker',marktype,'color',col,'markersize',30,'markerfacecolor',markcol)
    text(initpos(1),initpos(2),['$' ttex '$'],'color',col,'interpreter','latex','fontweight','bold')