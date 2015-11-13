function [mlcpop,mlctable,i]=fill_creation(mlcpop,mlctable,mlc_parameters,indiv_to_generate,i,type,verb)
n_indiv_to_generate=length(indiv_to_generate);
while i<=n_indiv_to_generate
    mlcind=MLCind;
    mlcind.generate(mlc_parameters,type);
    [mlctable,number,already_exist]=mlctable.add_individual(mlcind);
    if already_exist==0
        if verb>1;fprintf('Generating individual %i\n',indiv_to_generate(i));end
        if verb>2;mlcind.textoutput;end
         
            if  mlcind.preev(mlc_parameters) 
                mlcpop.individuals(indiv_to_generate(i))=number;
                i=i+1;
            else
                if verb>1;fprintf('preevaluation fail\n');end
            end
        
    else
        if verb>3;fprintf('replica\n');end
    end
end