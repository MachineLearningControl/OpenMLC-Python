function [mlcpop,mlctable]=create(mlcpop,mlc_parameters,mlctable)
verb=mlc_parameters.verbose;
if nargin<3
    mlctable=MLCtable(mlc_parameters.size(1)*50);
end
%% determine number of individuals to create;
indiv_to_generate=find(mlcpop.individuals==-1);
n_indiv_to_generate=sum(mlcpop.individuals==-1);
n_indiv=length(mlcpop.individuals);
i=1;
 if verb>1;fprintf(['Using "' mlc_parameters.generation_method '" method\n']);end
    switch mlc_parameters.generation_method
        case 'random_maxdepth'
            [mlcpop,mlctable]=fill_creation(mlcpop,mlctable,indiv_to_generate,i,0,verb);
%             while i<=n_indiv_to_generate
%                mlcind=MLCind;
%                mlcind.generate(mlc_parameters,0);
%                [mlctable,number]=mlctable.add_individual(mlcind);
%                if number>0
%                     if verb>1;fprintf('Generating individual %i\n',i-n_indiv_to_generate+n_indiv);end
%                     mlcpop.individuals(i)=number;
%                     i=i+1;
%                else
%                    fprintf('replica\n')
%                end
%             end
case 'fixed_maxdepthfirst'
            [mlcpop,mlctable]=fill_creation(mlcpop,mlctable,mlc_parameters,indiv_to_generate,i,1,verb);
        case 'random_maxdepthfirst'
             [mlcpop,mlctable]=fill_creation(mlcpop,mlctable,mlc_parameters,indiv_to_generate,i,2,verb);
        case 'full_maxdepthfirst'
             [mlcpop,mlctable]=fill_creation(mlcpop,mlctable,mlc_parameters,indiv_to_generate,i,3,verb);
        case 'mixed_maxdepthfirst' %% 50% at full, 50% random, at maxdepthfirst
             [mlcpop,mlctable,i]=fill_creation(mlcpop,mlctable,mlc_parameters,indiv_to_generate(1:round(n_indiv_to_generate/2)),i,1,verb);
              [mlcpop,mlctable]=fill_creation(mlcpop,mlctable,mlc_parameters,indiv_to_generate,i,3,verb);
        case 'mixed_ramped_even'        %% 50% full, 50% random with ramped depth
            changed_param=mlc_parameters;
            n=round(linspace(n_indiv_to_generate/(length(mlc_parameters.ramp)*2),n_indiv_to_generate,length(mlc_parameters.ramp)*2));
            for j=1:length(mlc_parameters.ramp)
                changed_param.maxdepthfirst=mlc_parameters.ramp(j);
                [mlcpop,mlctable,i]=fill_creation(mlcpop,mlctable,changed_param,indiv_to_generate(1:n(2*j-1)),i,1,verb);
                [mlcpop,mlctable,i]=fill_creation(mlcpop,mlctable,changed_param,indiv_to_generate(1:n(2*j)),i,3,verb);
            end
        case 'mixed_ramped_gauss'   %% 50% full 50% random gaussian distrib
            changed_param=mlc_parameters;
            minde=min(mlc_parameters.ramp);
            maxde=max(mlc_parameters.ramp);
            center=round((maxde+minde)/2);
            r=mlc_parameters.ramp;
            sigma=mlc_parameters.gaussigma;
            g=(exp(-((r-center).^2)/sigma^2)/sum(exp(-((r-center).^2)/sigma^2)))*n_indiv_to_generate;
            n=[0 round(cumsum(g))];
            for j=1:length(n)-1;
                changed_param.maxdepthfirst=mlc_parameters.ramp(j);
                [mlcpop,mlctable,i]=fill_creation(mlcpop,mlctable,changed_param,indiv_to_generate(1:n(j)+round((n(j+1)-n(j))/2)),i,1,verb);
                [mlcpop,mlctable,i]=fill_creation(mlcpop,mlctable,changed_param,indiv_to_generate(1:n(j+1)),i,3,verb);
            end
            
    end
    
end
