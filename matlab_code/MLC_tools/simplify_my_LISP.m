function newlisp = simplify_my_LISP(oldlisp,parameters)
%SIMPLIFY_MY_LISP   simplify <a href="matlab:help MLC">MLC</a> LISP written individuals.
%    NEWLISP=SIMPLIFY_MY_LISP(OLDLISP,PARAMETERS) applys simplifications laws
%    implemented in an <a href="matlab:help MLC">MLC</a> object in its
%    parameters field to a LISP individual.
%
%    NEWLISP=SIMPLIFY_MY_LISP(OLDLISP) applys simplifications laws
%    implemented by default in the <a href="matlab:help MLC">MLC</a> class.
%
%    Ex:
%    my_lisp='(+ (+ (exp 0.565) (- S2 (- (exp S1) (exp S1)))) (* (- S1 S1) (cos S2)))';
%    my_newlisp=simplify_my_LISP(my_lisp)
%
%    The function recursively identify each node and its arguments, calls
%    itself for each argument. For each node the simplifications
%    implemented in <a href="matlab:help opset">opset</a> are performed.
%    Then the simplified arguments are feeded higher in the tree until the
%    top.
%
%   See also MLC, readmylisp_to_formal_MLC, Derivate_my_lisp_MLC
%
%   Copyright (C) 2013 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox


% LISP expression are feeded back to the user or to earlier calls in the
% variable NEWLISP.

% get parameters, load default if nothing present.
    if nargin>1
        ops=parameters.opset;
    else
        ops=opset(1:9);
        parameters.opset=ops;
        parameters.precision=4;
    end

    str_format = '';
    str_format = strcat(str_format, '% .');
    str_format = strcat(str_format, num2str(parameters.precision));
    str_format = strcat(str_format, 'f');

    fvig=find(oldlisp==' ');
    if isempty(fvig);       %% no space => no arguments => no simplification
        newlisp=oldlisp;
    else                    %% we have arguments
        op=oldlisp(2:fvig(1)-1);  %% operator after prenthesis and before first space
        stru=[find(((cumsum(double(oldlisp=='('))-cumsum(double(double(oldlisp)==')'))).*double(double(oldlisp==' '))==1)) length(oldlisp+1)];
        % stru contains indices of spaces between arguments of the leftmost
        % operator
        % Ex:                (+ (- a b) c)
        %  cumsum of (  :    1112222222222
        %  cumsum of )  :    0000000001112
        %   difference  :    1112222221110
        %    space      :    0010010100100
        %  space*diff   :    0010020200100
        % space*diff==1 :    0010000000100
        %    stru       :  3,11,14 (we add the length+1 so that arguments
        %                  are always between two indices of stru).
        newlisp=oldlisp;
        if strcmp(op,'root');
            newlisp='(root';
            for nc=1:length(stru)-1
                exp=simplify_my_LISP(oldlisp(stru(nc)+1:stru(nc+1)-1),parameters);
                newlisp=[newlisp ' ' exp];
            end
            newlisp=[newlisp ')'];
        else
            for i=1:length(ops)
                if strcmp(ops(i).op,op)
                    for j=1:ops(i).nbarg
                        % get deeper simplifications
                        eval(['arg' num2str(j) '=''' simplify_my_LISP(oldlisp(stru(j)+1:stru(j+1)-1),parameters) ''';']);
                        % apply deeper simplifications
                        eval(['newlisp=strrep(newlisp,oldlisp(stru(j)+1:stru(j+1)-1),arg' num2str(j) ');']);
                    end
                    for j=1:length(ops(i).simplificationcondition);          % do current simplification
                        eval(['if ' ops(i).simplificationcondition{j} ';'... % rule j for operator i
                                    ops(i).simplificationaction{j} ';'...    % action if rule j for operatot i is met
                              'end']);
                    end
                end
            end
        end
    end;
end
