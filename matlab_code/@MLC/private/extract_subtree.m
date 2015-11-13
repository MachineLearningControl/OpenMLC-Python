function [m,sm,stdepth]=extract_subtree(m,mindepth,subtreedepthmax,maxdepth)
    subtreedepthmin=2;
    leftpar=cumsum(m=='(');
    rightpar=cumsum(m==')');
    cdepth=leftpar-rightpar;
%   fprintf([m '\n']);
   if length(m)==0
       merguez
   end
%     for i=1:length(m);
%         fprintf(num2str(leftpar(i)));
%     end
%     fprintf('\n');
%     for i=1:length(m);
%         fprintf(num2str(rightpar(i)));
%     end
%     fprintf('\n');
%     for i=1:length(m);
%         fprintf(num2str(cdepth(i)));
%     end
%     fprintf('\n');
%     for i=1:length(m);
%         fprintf(num2str(mod(i,10)));
%     end
%     fprintf('\n');
    rankpar=(m=='(').*cdepth;
    rankpar2=((m==')')).*(cdepth+1);
	idx1=find(rankpar);
	%idx2=find(rankpar2);
	subtreedepth=rankpar*0;
	for i=1:length(idx1)
		idx1(i);
		crank=rankpar(idx1(i));
		icendpar=find(rankpar2==crank);
		icendpar=icendpar(icendpar>idx1(i));
		icendpar=icendpar(1);

		subtreedepth(idx1(i))=max(rankpar(idx1(i):icendpar));
	end
%     fprintf('\n');
%     for i=1:length(m);
%         fprintf(num2str(subtreedepth(i)-rankpar(i))); 
%         
%     end	
%     fprintf('\n');
%     fprintf(num2str((rankpar>=mindepth))); fprintf('\n');
%         fprintf(num2str( (subtreedepth-rankpar<=(subtreedepthmax-1)))); fprintf('\n');
%         fprintf(num2str( (rankpar<=maxdepth))); fprintf('\n');
    
   
   
    eligiblepar=find((rankpar>=mindepth).*(subtreedepth-rankpar<=(subtreedepthmax-1)).*(rankpar<=maxdepth)); 
    if isempty(eligiblepar)
 %   fprintf('nothing eligible\n')
	m=[];
	sm=[];
    stdepth=-1;
	else
    n=ceil(rand*length(eligiblepar));
    n=eligiblepar(n);
    n2=find(rankpar(n)==rankpar2);
    
    idx=find(n2.*(n2>n));
    n2=n2(idx(1));
    sm=m(n:n2);
    leftpar=cumsum(sm=='(');
    rightpar=cumsum(sm==')');
    cdepth=leftpar-rightpar;
    stdepth=max(cdepth);
    m=[m(1:n-1) '°' m(n2+1:end)];
    end
end
