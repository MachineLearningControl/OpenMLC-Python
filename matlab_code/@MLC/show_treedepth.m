function show_treedepth(mlc)
%SHOW_TREEDEPTH    Method of the MLC class. Graphs tree-depth repartition.
%
%   MLC_OBJ.SHOW_TREEDEPTH 
%
%   See also MLC, SHOW_CONVERGENCE, STATS, SHOW_STATS
%
%   Copyright (C) 2013 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox
if isempty(mlc.population)
    display('You need at one population.');
    display('Use MLC_OBJ.generate_population.');
    return
end

mdepth=mlc.parameters.maxdepth
pop=mlc.population
md=zeros(length(pop(1).individuals),length(pop));
for j=1:length(pop);
for i=1:length(pop(1).individuals);
m=pop(j).individuals{i};
maxdepth=max(cumsum(m=='(')-cumsum(m==')'));
md(i,j)=maxdepth;
end
end
hmd=zeros(length(pop),mdepth);
size(hmd)
for j=1:length(pop);
hmd(j,:)=hist(md(:,j),1:mdepth);
end

plot3(repmat(1:mdepth,[length(pop) 1])',repmat((1:length(pop))',[1 mdepth])',(hmd'))