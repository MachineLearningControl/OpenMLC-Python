function [m1,m2,fail]=crossover_tree(m1,m2,gen_param)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%  crossover.m a function of TUCOROM_MLC MATLAB          %%%%%%%%%%%%%
%%%%%%  author: Thomas Duriez (thomas.duriez@gmail.com)       %%%%%%%%%%%%%
%%%%%%  PPRIME Laboratory, Poitiers, France                   %%%%%%%%%%%%%
%%%%%%  Funded by ANR TUCORM                                  %%%%%%%%%%%%%
%%%%%%  Created: 11 Dec. 2013                                 %%%%%%%%%%%%%
%%%%%%  Revised: 13 Dec. 2013                                 %%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Extract a subtree out of a tree, extract a correct subtree out of       %
% another tree (with depth that can fit into maxdepth).                   %
% Then interchange the two subtrees.                                      %
% inputs:                                                                 %
% m1: first tree (lisp ascii expression)                                  %
% m2: second tree (lisp ascii expression)                                 %
% gen_param: a parameters structure for genetic programming as returned   %
% by set_GP_parameters.m                                                  %
% outputs:                                                                %
% m1: first new tree (lisp ascii expression)                              %
% m2: second new tree (lisp ascii expression)                             %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    om1=m1;
    om2=m2;
    correct=0;
    count=0;
    while correct==0 && count<gen_param.maxtries
        %% Extracting subtrees
        [m1,sm1,n]=extract_subtree(om1,gen_param.mutmindepth,gen_param.maxdepth,gen_param.maxdepth); %% check extract_subtree comments
        [m2,sm2,n2]=extract_subtree(om2,gen_param.mutmindepth,n,gen_param.maxdepth-n+1);
      %  fprintf('done\n')
        count=count+1;
        if n>0 && n2>0;correct=1;end %% n or n2 < 0 indicates the extraction was not correct for any reason.
    end
    if correct==0
        fail=1;  %% we could not find a candidate substitution in maxtries tests. We will select other individuals.
    else
        fail=0;
        %% Replacing subtrees
        m1=strrep(m1,'@',sm2);
        m2=strrep(m2,'@',sm1);
%         if gen_param.preevaluation
%             eval(['peval=@' gen_param.preev_function ';']);
%             f=peval;
%             preevok1=feval(f,m1);
%             preevok2=feval(f,m2);
%             fail=1-preevok1*preevok2;
% 
%         end


    end
    %% So easy.
end


