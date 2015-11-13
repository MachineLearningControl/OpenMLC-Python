function mlctable=update_individual(mlctable,idx,J,ev_time)
    if nargin<4
        mlctable.individuals(idx).evaluate(J);
    else
        mlctable.individuals(idx).evaluate(J,ev_time);
    end
    mlctable.costlist(idx)=mlctable.individuals(idx).cost;