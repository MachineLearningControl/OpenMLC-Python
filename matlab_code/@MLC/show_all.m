function show_all(mlc,fig)   
    if isempty(mlc.population)
        return
    else
        ngen=length(mlc.population);
        if min(mlc.population(ngen).fitnesses)==-1
            ngen=ngen-1;
        end
        if ngen<2
            return
        end
        if ngen>15
            fig=1;
        end
        figure(500)
        if fig>1
        s=subplot(1,2,1);
        Jmax=max(mlc.population(ngen).fitnesses(mlc.population(ngen).fitnesses<mlc.parameters.badvalue));
        Jmin=min(mlc.population(ngen).fitnesses);
        mlc.show_convergence(1000,0,Jmax,0,1,[1:ngen],s);
        s=subplot(1,2,2);
        k=ceil(log(Jmax/Jmin)/log(10));
        refvalues=[Jmin*10.^(0:k)];
        mlc.genealogy(ngen,1,refvalues,s)
        else
            s=gca;
            Jmax=max(mlc.population(ngen).fitnesses(mlc.population(ngen).fitnesses<mlc.parameters.badvalue));
        Jmin=min(mlc.population(ngen).fitnesses);
        mlc.show_convergence(1000,0,Jmax,0,1,[1:ngen],s);
        end
            
    end
end
        