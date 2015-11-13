function show_convergence(mlc,nhisto,Jmin,Jmax,linlog,maxsat,gen_range,axis)
%SHOW_CONVERGENCE    Method of the MLC class. Graphs cost repartition.
%
%   MLC_OBJ.SHOW_CONVERGENCE 
%   MLC_OBJ.SHOW_CONVERGENCE(NHISTO,JMIN,JMAX,LINLOG,MAXSAT)
%   MLC_OBJ.SHOW_CONVERGENCE(NHISTO,JMIN,JMAX,LINLOG,MAXSAT,RANGE) display
%   2D or 3D histogram. 
%
%   NHISTO       - number of bins for the histograms (default 1000).
%   JMIN         - minimum cost value included (default 0).
%   JMAX         - maximum cost value included (default maximum in the
%                  data).
%   LINLOG       - logarithmic (0) or linear (1) spacing of the bins
%                  (default 0).
%   MAXSAT       - % of individuals at which the colormap saturates 
%                  (default 10).
%   RANGE        - index of population to use (default 1:end).
%
%   If only one generation is present the histogram is 2D, 3D otherwise.
%
%   See also MLC, SHOW_STATS, STATS, SHOW_TREEDEPTH
%
%   Copyright (C) 2013 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox
if nargin<2
     ngen=length(mlc.population);
        if min(mlc.population(ngen).fitnesses)==-1
            ngen=ngen-1;
        end
    nhisto=1000;
    Jmax=max(mlc.population(ngen).fitnesses(mlc.population(ngen).fitnesses<mlc.parameters.badvalue));
    Jmin=min(mlc.population(ngen).fitnesses);
    linlog=0;
    maxsat=1;
elseif (nargin>1 && nargin <6) || nargin >8 
    disp('Correct calls:')
    disp('mlc_obj.show_convergence')
    disp('mlc_obj.show_convergence(nhisto,Jmin,Jmax,linlog,maxsat)')
    disp('mlc_obj.show_convergence(nhisto,Jmin,Jmax,linlog,maxsat,gen_range)')
    return
end
pop=mlc.population;
if nargin>=7
    pop=pop(gen_range);
end
if nargin==8
    axes(axis)
else
    figure(666)
end
    
    if min(pop(length(pop)).fitnesses)==-1
       
        pop=pop(1:length(pop)-1);
    end
    nb=length(pop(1).fitnesses);
    J=zeros(nb,length(pop));
    for i=1:length(pop)
        J(:,i)=pop(i).fitnesses;
    end
      % J=1./J-1; % From adjusted fitness to goal functional
     
     nind=size(J,1);
     ngen=size(J,2);
     %% Construction of bins
     if linlog==0
        range=log10(max(J(J(:)<Jmax)))-log10(min(J(J(:)>max(Jmin,0))));
        binhisto=10.^(linspace(log10(min(J(J(:)>max(Jmin,0))))-range*0.1,log10(max(J(J(:)<Jmax)))+range*0.1,nhisto));    
     else
        range=(max(J(J(:)<Jmax)))-(min(J(J(:)>Jmin)));
        binhisto=linspace((min(J(J(:)>Jmin)))-range*0.1,(max(J(J(:)<Jmax)))+range*0.1,nhisto);
        
     end
     
     %% Construction of histograms
     histo=zeros(length(binhisto),ngen);
     for i=1:ngen
        c=hist((J(:,i)),binhisto);
        histo(:,i)=c/nind*100;
     end
     
   
      if length(pop)>=2
     %% Plot
     hgen=repmat(1:ngen,[nhisto-1 1]);
     surf(hgen,repmat(binhisto(1:end-1)',[1 ngen]),histo(1:end-1,:),log(1+histo(1:end-1,:)));view(0,90);shading interp
     hold on
     for i=1:ngen-1
         plot3(ones(size(binhisto(1:end-1)))*i,binhisto(1:end-1),histo(1:end-1,i),'b','linewidth',2);
     end
     plot3(ones(size(binhisto(1:end-1)))*ngen,binhisto(1:end-1),histo(1:end-1,ngen),'r','linewidth',2);
     hold off
     set(gca,'xlim',[1 ngen],'ylim',[min(binhisto(:)),max(binhisto(:))],'zlim',[0 max(max(histo(1:end-1,:)))],'clim',[-1/5 maxsat]);
     xlabel('n (generation index)','Interpreter','latex','fontsize',30);
     ylabel('J','Interpreter','latex','fontsize',30);
     set(gcf,'color',[1 1 1]);
     %box on
     set(gca,'fontsize',20,'fontweight','bold','linewidth',2);
     if linlog==0
         set(gca,'yscale','log');
     end
     load my_default_colormap c
     colormap(c);
     %clb=colorbar;set(clb,'fontsize',20,'linewidth',2,'fontweight','bold')
     t=title('Population repartition (\%)');set(t,'interpreter','latex','fontsize',30)
        view(0,90)
        
        
        
    else
     plot(binhisto,histo);
        xlabel('J','Interpreter','latex','fontsize',30);
         ylabel('N','Interpreter','latex','fontsize',30);
         set(gca,'xlim',[min(binhisto(:)),max(binhisto(:))]);
         set(gcf,'color',[1 1 1]);
     box on
     if linlog==0
         set(gca,'xscale','log');
     end
     end
            
    end
    
            
    
