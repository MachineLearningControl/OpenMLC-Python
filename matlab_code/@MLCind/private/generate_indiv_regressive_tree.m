function [m]=generate_indiv_regressive_tree(m,gen_param,type)
%generate_indiv_regressive_tree    Private function of the MLC CLASS. Grow individuals from seed '@';
%    [M]=generate_indiv_regressive_tree(M,GEN_PARAM,TYPE) seriously... that's a
%    PRIVATE function... Well, basically a seed '@' is placed in a string.
%    The function detect it and replace by one posible node. This node can
%    be a "leaf" (constant or tree input), or an operator. If an operator
%    is selected then as many seeds '@' as arguments needed are placed and
%    the function is called again. 
%
%    M is a string containing a seed. Initial call should be M='@', but it
%    can also be a truncated individual, during a mutation for instance.
%    (Ex : '(+ S1 (* @ S2))' will grow from the @).
%
%    GEN_PARAM contains the parameters from the MLC object.
%    (obj.parameters)
%
%    TYPE will condition how the tree grows:
%           - 0 free until absolute parameters.maxdepth (can stop before).
%           - 1 generates a tree of exactly parameters.maxdepthfirst.
%           - 2 free until absolute parameters.maxdepthfirst (can stop 
%               before).
%           - 3 full, all leaves are at depth parameters.maxdepthfirst.
%           - 4 generate a leave directly
%
%   Copyright (C) 2013 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox
%% What kind of tree
if isempty(type)
    type=-1;
end
    if nargin==3   
        if type==1;
            mindepth=gen_param.maxdepthfirst;
            maxdepth=gen_param.maxdepthfirst;
        elseif type==2 || type==3
            mindepth=gen_param.mindepth;
            maxdepth=gen_param.maxdepthfirst;
        elseif type==4
            mindepth=gen_param.mindepth;
            maxdepth=1;
        else
            mindepth=gen_param.mindepth;
            maxdepth=gen_param.maxdepth;
        end
    else
         mindepth=gen_param.mindepth;
         maxdepth=gen_param.maxdepth;
    end
    
    idx=strfind(m,'@');
    if isempty(idx)    %% No seed...
        return
    else
        idx=idx(1);    %% one call of the function only cares about one seed.
        if idx==1
            begstr=[];
            endstr=[];
        else
            begstr=m(1:idx-1);
            endstr=m(idx+1:end);
        end
        leftpar=cumsum(m=='(');
        rightpar=cumsum(m==')');
        currank=(m=='@').*(leftpar-rightpar); %% detecting the depth of the seed.
        %% Choose next node.
        nbop=length(gen_param.opset);
        if max(currank)>=maxdepth   %% Cannot go deeper => leaf
            choice=1;
        elseif (max(currank)<mindepth && isempty(strfind(endstr,'@')))...
                || (max(currank)<maxdepth && type==3) %% cannot stop here => operator
            choice=0;      
        else
            choice=rand<gen_param.leaf_prob;  %% freedom
        end
        %% Create node or leaf.
            if choice
                choice2=rand<gen_param.sensor_prob;
                if choice2
                    choice3=ceil(rand*gen_param.sensors)-1;
                    m=[begstr 'z' num2str(choice3) endstr];
                else
                    newexp=num2str((rand-0.5)*2*gen_param.range,gen_param.precision);
                    m=[begstr newexp endstr];
                end
            else
                nbop=length(gen_param.opset);
                choice2=ceil(rand*(nbop));
                if gen_param.opset(choice2).nbarg==1
                    m=[begstr '(' gen_param.opset(choice2).op ' @)' endstr];
                    m=generate_indiv_regressive_tree(m,gen_param,type);
               
                elseif gen_param.opset(choice2).nbarg==2
                    m=[begstr '(' gen_param.opset(choice2).op ' @ @)' endstr];
                    [m]=generate_indiv_regressive_tree(m,gen_param,type);
                    [m]=generate_indiv_regressive_tree(m,gen_param,type);
                end
            end    
    end
end

