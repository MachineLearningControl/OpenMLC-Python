function genealogy(mlc,gen,indiv,refvalues,axis)
%GENEALOGY    Method of the MLC class. Draws individual genealogy. 
%   MLC_OBJ.GENEALOGY(GEN,INDIV) links recursively individuals with parents
%   from the preceding generation, starting with individual INDIV (sorted
%   by cost) of generation GEN. The cost of individuals is displayed by
%   domain from the minimal to maximal cost.
%
%   MLC_OBJ.GENEALOGY(GEN,INDIV,REFVALUES) links recursively individuals with parents
%   from the preceding generation, starting with individual INDIV (sorted
%   by cost) of generation GEN. The cost of individuals is displayed by
%   domains determined by the REFVALUES vector.
%
%   MLC_OBJ.GENEALOGY(GEN,INDIV,REFVALUES,AXIS) draws the result in the
%   axis determined by the AXIS handle. Otherwise the figure 666 is used.
%
%   In the graph, each parent-children link is noted with the following
%   color code:
%     - elitism:      gold
%     - replication:  black
%     - crossover:    magenta
%     - mutation:     red
%
%   See also MLC, SHOW_CONVERGENCE, SHOW_STATS
%
%   Copyright (C) 2013 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox
if nargin==5
    axes(axis)
else
figure(888)
end
pop=mlc.population;
nind=length(pop(gen).fitnesses);
p=zeros(gen,nind);
J=p';
for i=1:gen
    J(:,i)=mlc.population(i).fitnesses;
%     for j=1:nind
%         hold on
%         color='k';
%         if mlc.population(i).fitnesses(j)==mlc.parameters.badvalue
%             color='r';
%         end
%         p(i,j)=plot(i,j,'o');
%         hold off
%     end
end
[x,y]=meshgrid([1:gen],[1:nind]);
plot(x(:),y(:),'o');
hold on
Jmax=max(J(J(:)<mlc.parameters.badvalue));
Jmean=mean(J(J(:)<mlc.parameters.badvalue));
Jmin=min(J(:));
if nargin>=4
    values=[refvalues(:)' mlc.parameters.badvalue];
else
    values=([Jmin,Jmean,Jmax,mlc.parameters.badvalue]);
end
Js=J*0+length(values);
for i=1:length(values)-1;
    Js(J>=values(i) & J<values(i+1))=i;
end

surf(repmat(1:gen,[nind 1]),repmat((1:nind)',[1 gen]),Js*0-1,Js);
 shading interp;
 set(gca,'clim',[1 length(values)])
load my_default_colormap c
c2=c(round(linspace(1,64,length(values)-1)),:);
colormap(c2)
hold off
l=colorbar;
mt=char(num2str(values(1),'%g'));
for i=2:length(values)
    mt=char(mt,num2str(values(i),'%g'));
end
set(l,'YTick',1:length(values))
set(l,'YTickLabel',mt)
set(gca,'xlim',[0 gen],'ylim',[0 nind]);
set(gcf,'color',[1 1 1])
hold on
for l=indiv
idx1=l;

lnwidth=1;
end
for i=gen:-1:2
    idx2=[];
    for j=idx1
    idxn=mlc.population(i).selected{j};
    hold on
    switch mlc.population(i).generatedfrom(j)
        case 1
            mkfc='b';
        case 2 
            mkfc='r';
        case 3
            mkfc='k';
        case 4
            mkfc='y';
    end
  %  set(p(i,j),'markerfacecolor',mkfc,'color',color);
    for k=idxn 
    plot([i i-1],[j,k],'color',mkfc,'linewidth',lnwidth)
    if i==indiv
        plot([i i-1],[j,k],'color','k','linewidth',1)
        drawnow
    end
        
    end
    %hold off
    idx2=[idx2 idxn];
    end
    idx1=idx2;
end
hold off


end

    