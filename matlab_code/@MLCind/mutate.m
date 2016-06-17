function [new_ind,fail]=mutate(mlcind,mlc_parameters, mutate_type)
    switch mlc_parameters.individual_type
        case 'tree'
            %[newvalue,fail]=mutate_tree(mlcind.value,mlc_parameters);
            if nargin<3
                [newvalue,fail]=mutate_tree(mlcind.value,mlc_parameters);
            else
                [newvalue,fail]=mutate_tree(mlcind.value,mlc_parameters, mutate_type);
            end
            new_ind=MLCind;
            new_ind.generate(mlc_parameters,newvalue);
    end
            