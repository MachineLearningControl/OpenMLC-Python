function op=choose_genetic_op(mlc_parameters,n);
prob_rep=mlc_parameters.probrep;
prob_mut=mlc_parameters.probmut;
prob_cro=mlc_parameters.probcro;

if (prob_cro+prob_rep+prob_mut)~=1
    fprintf('Probabilities of genetic operations is not equal to one.\nPlease adjust and relaunch\n');
    op=[];
    return
end

%% n is the number of individuals left to produce. While if n<2 crossover is not possible
p=rand;
if n<2
    p=p*(prob_rep+prob_mut);
    if p<=prob_rep;
        op='replication';
    else
        op='mutation';
    end
else
    if p<=prob_rep;
        op='replication';
    elseif p>prob_rep && p<=(prob_mut+prob_rep)
        op='mutation';
    else
        op='crossover';
    end
end
    