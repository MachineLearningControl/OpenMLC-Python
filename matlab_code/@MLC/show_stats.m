function show_stats(mlc,loglin)
%SHOW_STATS    Method of the MLC class. Graphs cost repartition.
%
%   MLC_OBJ.SHOW_STATS 
%   MLC_OBJ.SHOW_STATS(LINLOG) plots minimum, average, standart deviation
%   and maximum of cost values through the generations.
%
%   LINLOG       - logarithmic (0) or linear (1) scale (default 1).
%
%   See also MLC, SHOW_CONVERGENCE, STATS, SHOW_TREEDEPTH
%
%   Copyright (C) 2013 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox
if nargin<2
    loglin=1;
end
pop=mlc.population;
lgen=length(pop);
if isempty(mlc.population)
    display('You need at least two evaluated generations.');
    display('Use MLC_OBJ.stats.');
    return
end
if min(pop(lgen).fitnesses)==-1
    lgen=lgen-1;
end
if lgen<2
    display('You need at least two evaluated generations.');
    display('Use MLC_OBJ.stats.');
    return
end

minJ=zeros(1,lgen);
meanJ=minJ;
stdJ=minJ;
maxJ=minJ;
if isempty(pop(1).fitnesses)
    fprintf('Maybe start the GP before you ask some stats\n');
    fprintf('(And that''s me beeing polite here...)\n');
else
    for ngen=1:lgen;
        
        minJ(ngen)=min(pop(ngen).fitnesses);
        meanJ(ngen)=mean(pop(ngen).fitnesses(pop(ngen).fitnesses<mlc.parameters.badvalue/10));
        stdJ(ngen)=std(pop(ngen).fitnesses(pop(ngen).fitnesses<mlc.parameters.badvalue/10));
        maxJ(ngen)=max(pop(ngen).fitnesses(pop(ngen).fitnesses<mlc.parameters.badvalue/10));
    end
    my_statistics=[minJ;meanJ;stdJ;maxJ];
    
        plot(1:lgen,my_statistics);
        legend('Minimum','Average','Std deviation','Maximum')
        if loglin==0
            set(gca,'Yscale','log')
        end
    
    
end


