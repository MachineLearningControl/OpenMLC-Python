function [mlcpop2,mlctable]=evolve(mlcpop,mlc_parameters,mlctable,mlcpop2)
    ngen=mlcpop.gen;         
    verb=mlc_parameters.verbose;
    if nargin<4
        mlcpop2=MLCpop(mlc_parameters,ngen+1);
    end
    if verb>0;fprintf('Evolving population\n');end
    idxsubgen=subgen(mlcpop,mlc_parameters);
    idxsubgen2=subgen(mlcpop2,mlc_parameters);
    
    for i=1:length(idxsubgen2);
        idxsubgen2{i}=idxsubgen2{i}(mlcpop2.individuals(idxsubgen2{i})==-1);
        if verb>0;fprintf('Evolving sub-population %i/%i\n',i,mlcpop2.subgen);end
        if length(idxsubgen)==1
            idx_source_pool=idxsubgen{1};
        else
            idx_source_pool=idxsubgen{i};
        end
        individuals_created=0;
        %% elitism
        if nargin < 4
            for i_el=1:ceil(mlc_parameters.elitism/length(idxsubgen2));
                idv_orig=idx_source_pool(i_el);
                idv_dest=idxsubgen2{i}(individuals_created+1);

                % fprintf('ELITISM - IDV_ORIG: %d - IDV_DEST: %d \n', idv_orig, idv_dest);
                mlcpop2.individuals(idv_dest)=mlcpop.individuals(idv_orig);
                mlcpop2.costs(idv_dest)=mlcpop.costs(idv_orig);
                mlcpop2.parents{idv_dest}=idv_orig;
                mlcpop2.gen_method(idv_dest)=4;
                mlctable.individuals(mlcpop.individuals(idv_orig)).appearences=mlctable.individuals(mlcpop.individuals(idv_orig)).appearences+1;
                individuals_created=individuals_created+1;
            end
        end
        
        %% completing population
        while individuals_created<length(idxsubgen2{i})
            % fprintf('LEN idx_sub: %d\n', length(idxsubgen2{i})-individuals_created');
            op=choose_genetic_op(mlc_parameters,length(idxsubgen2{i})-individuals_created);
            switch op
                case 'replication'
                    idv_orig=choose_individual(mlcpop,mlc_parameters,idx_source_pool);
                    idv_dest=idxsubgen2{i}(individuals_created+1);
                    % fprintf('REPLICATION - IDV_ORIG: %d - IDV_DEST: %d \n', idv_orig, idv_dest);
                    mlcpop2.individuals(idv_dest)=mlcpop.individuals(idv_orig);
                    mlcpop2.costs(idv_dest)=mlcpop.costs(idv_orig);
                    mlcpop2.parents{idv_dest}=idv_orig;
                    mlcpop2.gen_method(idv_dest)=1;
                    mlctable.individuals(mlcpop.individuals(idv_orig)).appearences=mlctable.individuals(mlcpop.individuals(idv_orig)).appearences+1;
                    individuals_created=individuals_created+1;
                    
                case 'mutation'
                    fail=1;
                    while fail==1
                        idv_orig=choose_individual(mlcpop,mlc_parameters,idx_source_pool);
                        idv_dest=idxsubgen2{i}(individuals_created+1);
                        % fprintf('MUTATION - IDV_ORIG: %d - IDV_DEST: %d \n', idv_orig, idv_dest);
                        old_ind=mlctable.individuals(mlcpop.individuals(idv_orig));
                        [new_ind,fail]=old_ind.mutate(mlc_parameters);                    
                    end
                    [mlctable,number]=add_individual(mlctable,new_ind);
                    mlcpop2.individuals(idv_dest)=number;
                    mlcpop2.costs(idv_dest)=-1;
                    mlcpop2.parents{idv_dest}=idv_orig;
                    mlcpop2.gen_method(idv_dest)=2;
                    mlctable.individuals(number).appearences=mlctable.individuals(number).appearences+1;
                    individuals_created=individuals_created+1;
                                       
                case 'crossover'
                    fail=1;
                    while fail==1
                        idv_orig=choose_individual(mlcpop,mlc_parameters,idx_source_pool);
                        idv_orig2=idv_orig;
                        while idv_orig2==idv_orig;
                            idv_orig2=choose_individual(mlcpop,mlc_parameters,idx_source_pool);
                        end
                        idv_dest=idxsubgen2{i}(individuals_created+1);
                        idv_dest2=idxsubgen2{i}(individuals_created+2);
                        % fprintf('CROSSOVER - IDV_ORIG 1 : %d - IDV_DEST 1 : %d - IDV_ORIG 2 : %d - IDV_DEST 2 : %d\n', idv_orig, idv_dest, idv_orig2, idv_dest2);
                        old_ind=mlctable.individuals(mlcpop.individuals(idv_orig));
                        old_ind2=mlctable.individuals(mlcpop.individuals(idv_orig2));
                        [new_ind,new_ind2,fail]=old_ind.crossover(old_ind2,mlc_parameters);
                    end
                    
                    [mlctable,number]=add_individual(mlctable,new_ind);
                    mlcpop2.individuals(idv_dest)=number;
                    mlcpop2.costs(idv_dest)=-1;
                    mlcpop2.parents{idv_dest}=[idv_orig idv_orig2];
                    mlcpop2.gen_method(idv_dest)=3;
                    mlctable.individuals(number).appearences=mlctable.individuals(number).appearences+1;
                    individuals_created=individuals_created+1;
                    
                    [mlctable,number2]=add_individual(mlctable,new_ind2);
                    mlcpop2.individuals(idv_dest2)=number2;
                    mlcpop2.costs(idv_dest2)=-1;
                    mlcpop2.parents{idv_dest2}=[idv_orig idv_orig2];
                    mlcpop2.gen_method(idv_dest2)=3;
                    mlctable.individuals(number2).appearences=mlctable.individuals(number2).appearences+1;
                    individuals_created=individuals_created+1;
                                 
                    
            end
        end
        
        
        
        
    end
    
    
    
    