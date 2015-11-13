function [m,fail]=mutate(m,gen_param,forcetype)
if isempty(m)
    merguez
end
    fail=0;
    

    %% equi probability for each mutation type selected.
    if nargin<3
        type_mut=gen_param.mutation_types(floor(rand*(length(gen_param.mutation_types)))+1);
    else
        type_mut=forcetype;
    end
    switch type_mut
        %% mutation 'remove subtree and replace'
        case 1
            
        preevok=0; 
        while preevok==0
            %% remove subtree.
            [m]=extract_subtree(m,gen_param.mutmindepth,gen_param.maxdepth,gen_param.maxdepth);	 
            %% grow new subtree
            [m]=generate_indiv_regressive(m,gen_param,0);
            if isempty(m)
                preevok=1;
            else
            if gen_param.sensor_spec
                slist=sort(gen_param.sensor_list);
                for i=length(slist):-1:1
                    m=strrep(m,['z' num2str(i-1)],['S' num2str(slist(i))]);
                end
            else
                for i=gen_param.sensors:-1:1
                    m=strrep(m,['z' num2str(i-1)],['S' num2str(i-1)]);
                end

            end
            preevok=1;
            if gen_param.preevaluation
                eval(['peval=@' gen_param.preev_function ';']);
                f=peval;
                preevok=feval(f,m);
            end
            end
        end
        %% mutation 'reparametrization'
        case 2
            [m]=reparam(m,gen_param);
        %% mutation 'hoist' : subtree becomes the tree
        case 3
            if gen_param.controls==1
                [~,m]=extract_subtree(m,gen_param.mutmindepth,gen_param.maxdepth,gen_param.maxdepth);
            else
                % each control law has a 1/gen_param.controls chance to be
                % croped
                prob_threshold=1/gen_param.controls;
                stru=[find(((cumsum(double(double(m)=='('))-cumsum(double(double(m)==')'))).*double(double(m==' '))==1)) length(m+1)];
                cl=cell(1,gen_param.controls);
                for nc=1:(gen_param.controls)
                    cl{nc}=m(stru(nc)+1:stru(nc+1)-1); % each control law is extracted
                end
                changed=0;
                k=0;
                for nc=randperm(gen_param.controls) % order is randomized so that the last one is not always the same
                    k=k+1;
                    if (rand<prob_threshold) || (k==gen_param.controls && changed==0) % control law is cropped if it is the last one and no change happend before
                        changed=1;
                        [~,ind]=extract_subtree(cl{nc},gen_param.mutmindepth,gen_param.maxdepth,gen_param.maxdepth);
                        if isempty(ind)
                            changed=0;
                        else
                            cl{nc}=ind;
                        end
                    end
                end
                m='(root';
                for i=1:gen_param.controls
                    m=[m ' ' cl{i}];
                end
                m=[m ')'];    
            end
        %% mutation 'shrink' cut subtree, introduce leaf.
        case 4
            m=extract_subtree(m,gen_param.mutmindepth,gen_param.maxdepth,gen_param.maxdepth);
            m=generate_indiv_regressive(m,gen_param,4);
            if ~isempty(m)
            if gen_param.sensor_spec
                slist=sort(gen_param.sensor_list);
                for i=length(slist):-1:1
                    m=strrep(m,['z' num2str(i-1)],['S' num2str(slist(i))]);
                end
            else
                for i=gen_param.sensors:-1:1                   
                    m=strrep(m,['z' num2str(i-1)],['S' num2str(i-1)]);
                end

            end
            end
    end
    if isempty(m)
        fail=1;
    end
end
	 

    
