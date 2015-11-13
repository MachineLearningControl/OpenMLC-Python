function genealogy(mlc,gen,idv)
% GENEALOGY (MLC2 Toolbox)
%
%   Directly taken from MLC. Dev version, not tested. 
%
%   Copyright (C) 2015 Thomas Duriez (thomas.duriez@gmail.com)
%   Development version. Use, copy and diffusion of this pogram is subject 
%   to the author's agreement.
    figure
    hold on
    for i=1:gen
        plot(ones(1,length(mlc.population(i).individuals))*i,1:length(mlc.population(i).individuals),'o');
    end
    lnwidth=1;
    idx1=idv;
    for i=gen:-1:2
        idx2=[];
        for j=idx1
        idxn=mlc.population(i).parents{j};
        hold on
        switch mlc.population(i).gen_method(j)
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
%         if i==indiv
%             plot([i i-1],[j,k],'color','k','linewidth',1)
%             drawnow
%         end

        end
        %hold off
        idx2=[idx2 idxn];
        end
    idx1=idx2;
    end
        