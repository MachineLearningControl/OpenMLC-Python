function mlcpop=sort(mlcpop,mlc_parameters)
idxsubgen=subgen(mlcpop,mlc_parameters);
%% normal sort
for i=1:length(idxsubgen)
    [~,idx]=sort(mlcpop.costs(idxsubgen{i}));
    mlcpop.individuals(idxsubgen{i})=mlcpop.individuals(idxsubgen{i}(idx));
    mlcpop.costs(idxsubgen{i})=mlcpop.costs(idxsubgen{i}(idx));
    mlcpop.parents(idxsubgen{i})=mlcpop.parents(idxsubgen{i}(idx));
    mlcpop.gen_method(idxsubgen{i})=mlcpop.gen_method(idxsubgen{i}(idx));
end
    