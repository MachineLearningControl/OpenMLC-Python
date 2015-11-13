%MLC parameters    This help files details the options to be set in the MLC
%     OBJ.parameters.FIELDNAME=PARAMETER
%     
%     Default parameter between parenthesis. Default parameters are used to
%     solve the 'toy_problem' problem, they are not fit for anything else.
%
%     See <a href="matlab:help set_MLC_parameters">set_MLC_parameters</a> to script parameter changes.
%
%     Individuals specific parameters
%            size          - number of individuals in the population. (100)
%            sensors       - number of inputs for control laws.         (2)
%            controls      - number of control laws.                    (1)
%            range         - absolute value of minimum and maximum of 
%                            generated constants.                      (10)
%            precision     - precision of ASCII written numbers.        (4)
%            opsetrange    - index of operations to use:              (1:9)
%                                        - 1 addition       (+)
%                                        - 2 substraction   (-)
%                                        - 3 multiplication (*)
%                                        - 4 division       (/)
%                                        - 5 sinus         (sin)
%                                        - 6 cosinus       (cos)
%                                        - 7 logarithm     (log)
%                                        - 8 exp           (exp)
%                                        - 9 tanh          (tanh)                                                                          
%            opset         - structure with set of operations and how they
%                            behave. See <a href="matlab:help opset
%                            ">opset</a> for modifications.                     
%
%     GP algortihm parameters (CHANGE IF YOU KNOW WHAT YOU DO)
%            maxdepth      - maximum depth of all individuals.         (15)
%            maxdepthfirst - maximum depth of individuals in first
%                            generation.                                (5)
%            mindepth      - minimum depth of individual before         
%                            simplification.                            (2)
%            mutmindepth   - minimum depth at which a node is selected for
%                            mutation or crossover.                     (2)
%            mutmaxdepth   - maximum depth at which a node is selected for
%                            mutation or crossover.                    (15)
%      mutsubtreemindepth  - minimum depth of a subtree for crossover.  (2)
%       generation_method  - generation method used:
%                                 - 'random_maxdepth' tree cannot go deeper
%                                   than maxdepth. Free otherwise.
%                                 - 'fixed_maxdepthfirst' all trees have at
%                                   least one leaf at maxdepthfirst.                                
%                                 - 'random_maxdepthfirst' tree cannot go
%                                   deeper than maxdepthfirst. Fee otherwise
%                                 - 'full_maxdepthfirst' all leaves are at
%                                   maxdepthfirst.
%                                 - 'mixed_ramped_even' equal repartition
%                                   of tree depth in depth defined in
%                                   parameters.ramp. 50% of the trees are
%                                   full (all leaves at the same depth).
%                                 - 'mixed_ramped_gauss' gaussian repartition
%                                   of tree depth in depth defined in
%                                   parameters.ramp. 50% of the trees are
%                                   full (all leaves at the same depth).
%                                                    ('mixed_ramped_gauss')
%            gaussigma     - standard deviation for the gaussian        (3)
%                            distribution (if 'mixed_ramped_gauss' is used) 
%            ramp          - range of tree depeth to be used in ramped
%                            generation methods.                      (2:8)
%           no_of_cascades - Number of cascades the population is divided
%                            into
%    no_of_gen_per_cascade - Number of generations each cascade is
%                            evolved
%            archive_size  - An archive of the best previouly obtained
%                            individuals is used for the crossover operation
%                            performed while breeding the next generation,
%                            additionally to the current individuals. The
%                            archive is kept during the cascading.
%
%      Optimization parameters
%            elitism       - number of individuals selected by elitism.
%                            In case of Pareto this is adjusted automatically
%                            to the number of pareto best individuals   (1)
%            probrep       - replication probability.                 (0.1)
%            probmut       - mutation probability.                    (0.2)
%            probcro        - crossover probability. Enforced as
%                            1-probre-probmut. The displayed value is just
%                            a reminder.                              (0.7)
%         selectionmethod  - method by which the individuals are selected:
%                               - 'tournament' a number of individuals are
%                                 selected, the best one is kept.
%                               - 'fitness_proportional' individuals have a
%                                 probability of being selected inversely
%                                 proportional to their cost.
%                               - 'pareto': a pareto aware algorithm is
%                                 chosen together with the tournament
%                                 selection method. The pareto best
%                                 individuals are also advanced to the next
%                                 generation
%                                                            ('tournament')
%         tournamentsize   - number of individuals that enter each 
%                            tournament.                                (7)
%        lookforduplicates - if set on 1 eradicates any duplicate
%                            individuals in the same generation. Set to 0
%                            to disable the option.                     (1)
%            simplify      - if set on 1 simplify LISP expressions using
%                            rules and actions coded in opset. Disable with
%                            0.                                         (0)
%    badvalues_elimswitch  - internal switch, DO NOT CHANGE.            (1)
%
%      Evaluator parameters            
%       evaluation_method  - determine how the evaluator is run.
%                            'standalone_function': a M-file is called. One
%                            individual is evaluated at a time using that
%                            M-file.
%                            'standalone_files': individuals and cost
%                            values are exchanged through files on the
%                            system. One individual at a time is evaluated.
%                            'multithread_function': a M-file is called.
%                            The Parallel Computing toolbox is used to call
%                            the maximum number of clients available
%                            through the cluster defined by matlabpool.
%                                                      ('standalone_files')
%      evaluation_function - absolute name of the M-file to call for
%                            evaluation. The name is suficient if the file
%                            is in the PATH.                ('toy_problem')
%            indfile       - name of the file where an external evaluator
%                            reads the individual               ('ind.dat')
%            Jfile         - name of the file where an external evaluator
%                            returns the cost                 ('Jfile.dat')
%            exchangedir   - path for indfile and Jfile  
%                                              (fullfile(pwd,'evaluator0'))
%             
%            evaluate_all  - if set on 1 evaluates individual already
%                            evaluated. In that case an average of the 
%                            costs is achieved. Disable with 0.         (0)                               
%         artificialnoise  - add random noise of value rand*artificialnoise
%                            to the cost value.                         (0)
%execute_before_evaluation - string which is evaluated before each
%                            generation evaluation.                    ('')             
%            badvalue      - cost value attributed to evaluation failures.
%                            Legal individuals with cost higher than
%                            badvalues has its cost changed to badvalue.
%                                                                 ('10^36')
%           badvalues_elim - behaviour settings relatively to individuals
%                            with cost equal to badvalue.
%                            'none': no action.
%                            'first': bad individuals in the first
%                            generation are replaced
%                            'all': all bad individual are replaced
%                                                                 ('first')
%
%    MLC behaviour parameters 
%            save          - if set on 1, saves the MLC object in 'mlc_be'
%                            before evaluation and in 'mlc_ae' after
%                            evaluation. Disable with 0.                (1)
%            verbose       - sets verbose level             ([0,0,0,1,0,0])
%            show_best     - if set on 1, will trigger a display of the
%                            best individual has defined in the problem 
%                            function. See documentation.               (1) 
%
%   See also MLC, set_MLC_parameters
%
%   Copyright (C) 2013 Thomas Duriez (thomas.duriez@gmail.com)
%   This file is part of the TUCOROM MLC Toolbox

