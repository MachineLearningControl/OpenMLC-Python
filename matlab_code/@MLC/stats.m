function stats(mlc,nb)
%STATS    Method of the MLC class. Computes statistics.
%
%   MLC_OBJ.STATS displays statistics on the MLC process. Show statistics
%   for all generations.
%   MLC_OBJ.STATS(NB) displays statistics on the MLC process. Show statistics
%   for generation NB.
%
%   See also MLC, SHOW_CONVERGENCE, SHOW_STATS, SHOW_TREEDEPTH
%
%   Copyright (C) 2013 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox
if nargin>1
    sgen=nb;
else
    sgen=1;
end
lgen=length(mlc.population);
if min(mlc.population(lgen).fitnesses)==-1
    lgen=lgen-1;
end
for ngen=sgen:lgen;
    if isempty(mlc.population(1).fitnesses)
        fprintf('Maybe start the GP before you ask some stats\n');
        fprintf('(And that''s me beeing polite here...)\n');
    else
        [minJ,k]=min(mlc.population(ngen).fitnesses);
        meanJ=mean(mlc.population(ngen).fitnesses(mlc.population(ngen).fitnesses<mlc.parameters.badvalue));
        stdJ=std(mlc.population(ngen).fitnesses(mlc.population(ngen).fitnesses<mlc.parameters.badvalue));
        toohigh=sum(mlc.population(ngen).fitnesses==mlc.parameters.badvalue);
        fprintf('After generation %i:\n',ngen);
        fprintf('Best individual:\n');
        fprintf('%s\n',mlc.population(ngen).individuals{k});
        fprintf('Best J (average over %i occurence(s)): \t %e\n',mlc.population(ngen).occurence(k),minJ);
        fprintf('Average J of population:\t\t %e\n',meanJ);
        fprintf('Std deviation of J in Population:\t %e\n',stdJ);
        fprintf('Average and std computed for values below %e (%i cases)\n',mlc.parameters.badvalue,toohigh);
        if ngen<lgen;fprintf('\n\n');end
    end
end