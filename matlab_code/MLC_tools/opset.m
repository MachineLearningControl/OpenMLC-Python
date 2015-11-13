function ops=opset(range)
%OPSET Private function of the MLC class. Generates structure of node operators.
%   OPS=OPSET(RANGE) fills the OPS structure using operations defined by
%   list of index RANGE.
%
%   implemented:     - 1  addition       (+)
%                    - 2  substraction   (-)
%                    - 3  multiplication (*)
%                    - 4  division       (%)
%                    - 5  sinus         (sin)
%                    - 6  cosinus       (cos)
%                    - 7  logarithm     (log)
%                    - 8  exp           (exp)
%                    - 9  tanh          (tanh)
%                    - 10 modulo        (mod)
%                    - 11 power         (pow)
%
%   OPS=OPSET([1:3 6]) defines an operation structure for <a href="matlab:help MLC">MLC</a> with
%   (+,-,*,cos).
%
%   OPS(i).FIELD defines opération i
%
%    FIELD
%     op                  - string used in the LISP expression
%     nbarg               - number of arguments
%     litop               - litéral opérations performed on arg1, arg2,...
%                           as would be used in MATLAB. This is eventualy
%                           passed to a eval function.
% simplificationcondition - condition on arg1, arg2,... as would be used in
%                           a 'if' statement. Evaluated by eval in the
%                           simplification function. One condition by cell.
%   simplificationaction  - action done when corresponding simplification
%                           condition is met. Always starts with 'newlisp=', a
%                           being the LISP strinf returned. Exemple: the
%                           first condition implemented for the additions
%                           states that if both arg1 and arg2 are numbers
%                           in ASCII then the LISP string is replaced with
%                           the result of the operation in ASCII.
%     derivlisp           - derivative of the LISP expression. darg1,
%                           darg2... are used to express derivatives of
%                           arguments. Exemple d(arg1+arg2)=darg1+darg2,
%                           d(cos(arg1))=darg1*(-sin(arg1))...
%
%   only op and nbarg fields are needed to use <a href="matlab:help MLC">MLC</a>. 
%   absence of simplification rule just renders <a href="matlab:help simplify_my_LISP">simplify_my_LISP</a> useless.
%   litop and derivlisp are needed by <a href="matlab:help readmylisp_to_formal_MLC">readmylisp_to_formal_MLC</a> and
%   <a href="matlab:help Derivate_my_lisp_MLC">Derivate_my_lisp_MLC</a> from the MLC toolbox. These are tools to build
%   evaluators.
%
%   See also MLC, set_MLC_parameters
%
%   Copyright (C) 2013 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox



opset(1).op='+';
opset(1).nbarg=2;
opset(1).litop='arg1 + arg2';
opset(1).simplificationcondition{1}='1-isnan(str2double(arg1)) && 1-isnan(str2double(arg2))';                  %% both strings are numbers
opset(1).simplificationaction{1}='newlisp=num2str(str2double(arg1)+str2double(arg2),parameters.precision);';   %% add 2 numbers -> back in string
opset(1).simplificationcondition{2}='1-isnan(str2double(arg1)) && str2double(arg1)==0';  
opset(1).simplificationaction{2}='newlisp=arg2;';
opset(1).simplificationcondition{3}='1-isnan(str2double(arg2)) && str2double(arg2)==0';
opset(1).simplificationaction{3}='newlisp=arg1;';
opset(1).derivlisp='(+ darg1 darg2)';
opset(1).complexity=1;

opset(2).op='-';
opset(2).nbarg=2;
opset(2).litop='arg1 - arg2';
opset(2).simplificationcondition{1}='1-isnan(str2double(arg1)) && 1-isnan(str2double(arg2))';
opset(2).simplificationaction{1}='newlisp=num2str(str2double(arg1)-str2double(arg2),parameters.precision);';
opset(2).simplificationcondition{2}='1-isnan(str2double(arg2)) && str2double(arg2)==0';
opset(2).simplificationaction{2}='newlisp=arg1;';
opset(2).simplificationcondition{3}='strcmp(arg1,arg2)';
opset(2).simplificationaction{3}='newlisp=num2str(0,parameters.precision);';
opset(2).derivlisp='(- darg1 darg2)';
opset(2).complexity=1;

opset(3).op='*';
opset(3).nbarg=2;
opset(3).litop='arg1 .* arg2';
opset(3).simplificationcondition{1}='1-isnan(str2double(arg1)) && 1-isnan(str2double(arg2))';
opset(3).simplificationaction{1}='newlisp=num2str(str2double(arg1)*str2double(arg2),parameters.precision);';
opset(3).simplificationcondition{2}='(1-isnan(str2double(arg1)) && str2double(arg1)==0) || (1-isnan(str2double(arg2)) && str2double(arg2)==0)';
opset(3).simplificationaction{2}='newlisp=num2str(0,parameters.precision);';
opset(3).simplificationcondition{3}='(1-isnan(str2double(arg1)) && str2double(arg1)==1)';
opset(3).simplificationaction{3}='newlisp=arg2;';
opset(3).simplificationcondition{4}='(1-isnan(str2double(arg2)) && str2double(arg2)==1)';
opset(3).simplificationaction{4}='newlisp=arg1;';
opset(3).derivlisp='(+ (* darg1 arg2) (* arg1 darg2))';
opset(3).complexity=1;

opset(4).op='/';
opset(4).nbarg=2;
opset(4).protection=0.01;
opset(4).litop='my_div(arg1,arg2)';
opset(4).simplificationcondition{1}='1-isnan(str2double(arg1)) && 1-isnan(str2double(arg2))';
opset(4).simplificationaction{1}=['newlisp=num2str(  str2double(arg1)./(max(abs(str2double(arg2)),' num2str(opset(4).protection) ').*sign(str2double(arg2))),parameters.precision);'];
opset(4).simplificationcondition{2}='(1-isnan(str2double(arg1)) && str2double(arg1)==0) || (1-isnan(str2double(arg2)) && str2double(arg2)==0)';
opset(4).simplificationaction{2}='newlisp=num2str(0,parameters.precision);';
opset(4).simplificationcondition{3}='(1-isnan(str2double(arg2)) && str2double(arg2)==1)';
opset(4).simplificationaction{3}='newlisp=arg1;';
opset(4).derivlisp='(- (% darg1 arg2) (* arg1 (% darg2 (% arg2 arg2))))';
opset(4).complexity=1;

opset(5).op='sin';
opset(5).nbarg=1;
opset(5).litop='sin(arg1)';
opset(5).simplificationcondition{1}='1-isnan(str2double(arg1))';
opset(5).simplificationaction{1}='newlisp=num2str(sin(str2double(arg1)),parameters.precision);';
opset(5).derivlisp='(* darg1 (cos arg1))';
opset(5).complexity=3;

opset(6).op='cos';
opset(6).nbarg=1;
opset(6).litop='cos(arg1)';
opset(6).simplificationcondition{1}='1-isnan(str2double(arg1))';
opset(6).simplificationaction{1}='newlisp=num2str(cos(str2double(arg1)),parameters.precision);';
opset(6).derivlisp='(* darg1 (- 0.00 (sin arg1)))';
opset(6).complexity=3;

opset(7).op='log';
opset(7).nbarg=1;
opset(7).protection=0.01;
opset(7).simplificationcondition{1}='1-isnan(str2double(arg1))';
opset(7).simplificationaction{1}=['newlisp=num2str(log(max(' num2str(opset(7).protection) ',abs(str2double(arg1)))),parameters.precision);'];
opset(7).litop=['my_log(arg1)'];
opset(7).derivlisp='(% darg1 arg1)';
opset(7).complexity=5;


opset(8).op='exp';
opset(8).nbarg=1;
opset(8).litop='exp(arg1)';
opset(8).simplificationcondition{1}='1-isnan(str2double(arg1))';
opset(8).simplificationaction{1}='newlisp=num2str(exp(str2double(arg1)),parameters.precision);';
opset(8).derivlisp='(* darg1 (exp arg1))';
opset(8).complexity=5;

opset(9).op='tanh';
opset(9).nbarg=1;
opset(9).litop='tanh(arg1)';
opset(9).simplificationcondition{1}='1-isnan(str2double(arg1))';
opset(9).simplificationaction{1}='newlisp=num2str(tanh(str2double(arg1)),parameters.precision);';
opset(9).derivlisp='(* darg1 (- 1.00 (* (tanh arg1) (tanh arg1))))';
opset(9).complexity=5;

opset(10).op='mod';
opset(10).nbarg=2;
opset(10).litop='my_div(mod(arg1,arg2),arg2)';
opset(10).complexity=5;

opset(11).op='pow';
opset(11).nbarg=2;
opset(11).litop='my_pow(arg1,arg2)';
opset(11).complexity=10;

ops=opset(range);         
