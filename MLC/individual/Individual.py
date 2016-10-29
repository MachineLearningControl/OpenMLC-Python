import numpy as np
import math

import MLC.Log.log as lg
from collections import Counter
from MLC.matlab_engine import MatlabEngine
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Common.Operations import Operations
from MLC.Common.Lisp_Tree_Expr.Lisp_Tree_Expr import Lisp_Tree_Expr, TreeVisitor

import re


class Individual(object):
    """
    MLCind constructor of the Machine Learning Control individual class.
    Part of the MLC2 Toolbox.

    Implements the individual type, value and costs. Archives history of
    evaluation and other informations.

    This class requires a valid MLCparameters object for most of its
    functionnalities.

    MLCind properties:
        type:
            type of individual (expression trees only now)
        value:
            string or matrice representing the individual in the representation
            considered in 'type'
        cost:
            current cost value of the individual (average of cost_history)
        cost_history:
            history of raw values returned by the evaluation function
        evaluation_time:
            date and time (on the computer clock) of sending of the indivs
            to the evaluation function
        appearances:
            number of time the individual appears in a generation
        hash:
            hash of 'value' to help finding identical individuals
            (will be turned to private)
        formal:
            matlab interpretable expression of the individual
        complexity:
            weighted addition of operators

    MLCind methods:
        generate:
            creates one indiv according to the current MLCparameters object
            and type of individual.
        evaluate:
            evaluates one individual according to the current MLCparameters
            object.
        mutate:
            mutates one individual according to the current MLCparameters
            object and type of indiv.
        crossover:
            crosses two indiv according to the current MLCparameters object
            and type of individuals.
        compare:
            stricly compares two individuals' values
        textoutput:
            display indiviudal value as text string
        preev:
            calls preevaluation function

    See also MLCPARAMETERS, MLCTABLE, MLCPOP, MLC2
    """
    class MutationType:
        ANY = 0
        REMOVE_SUBTREE_AND_REPLACE = 1
        REPARAMETRIZATION = 2
        HOIST = 3
        SHRINK = 4

    _maxdepthfirst = None

    def __init__(self, value=None):
        self._eng = MatlabEngine.engine()
        self._config = Config.get_instance()
        self._tree = None

        # For the moment is the only type available
        self._value = value
        self._cost = 1e36
        self._cost_history = []
        self._evaluation_time = 0.0
        self._appearences = 1
        self._hash = ""
        self._formal = ""
        self._complexity = 0

        self._range = self._config.getint("POPULATION", "range")
        self._precision = self._config.getint("POPULATION", "precision")

    @staticmethod
    def set_maxdepthfirst(value):
        Individual._maxdepthfirst = value

    def get_matlab_object(self):
        return self._mlc_ind

    def generate(self, value=None, individual_type=None):
        """
            generate individual from scratch or from unfinished individual.

            MLCIND.generate(MLC_PARAMETERS,MODE) creates an individual using mode MODE.
            MODE is a number which interpretation depends on the MLCIND.type property.
            (Not designed to be played with by user, code dive for details)

            MLCIND.generate(MLC_PARAMETERS,VALUE) creates an individual with MLCIND.value VALUE.

            matlab_impl: return self._eng.generate(self._mlc_ind, varargin)
        """
        if value is None and individual_type is None:
            raise Exception("Individual::generate() value or individual_type arguments should be passed to generate method")

        if value:
            self._value = value
        else:
            controls = self._config.getint('POPULATION', 'controls')
            self._value = '(root%s)' % (' @' * controls)
            for i in range(controls):
                self._value = self.__generate_indiv_regressive_tree(self._value, individual_type)

        self._value = self.__simplify_and_sensors_tree(self._value)
        self._hash = self._tree.calculate_hash()
        self._formal = self._tree.formal()
        self._complexity = self._tree.complexity()

    def mutate(self, mutation_type=MutationType.ANY):
        new_value, fail = self.__mutate_tree(self.get_value(), mutation_type)

        if fail:
            return None, fail

        new_individual = Individual()
        new_individual.generate(new_value)
        return new_individual, fail

    def crossover(self, other_individual):
        """
            CROSSOVER crosses two MLCind individuals.
            [NEW_IND1,NEW_IND2,FAIL]=CROSSOVER(MLCIND1,MLCIND2,MLC_PARAMETERS)
        """
        m1, m2, fail = self.__crossover_tree(self.get_value(), other_individual.get_value())

        if fail:
            return None, None, fail

        new_ind1 = Individual()
        new_ind1.generate(m1)

        new_ind2 = Individual()
        new_ind2.generate(m2)

        return new_ind1, new_ind2, fail

    def compare(self, other_individual):
        return self.get_value() == other_individual.get_value()

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    def get_cost(self):
        return self._cost

    def get_cost_history(self):
        return self._cost_history

    def get_evaluation_time(self):
        return self._evaluation_time

    def get_appearences(self):
        return self._appearences

    def inc_appearences(self):
        self._appearences += 1

    def get_hash(self):
        return self._hash

    def set_hash(self, hash):
        self._hash = hash

    def get_formal(self):
        return self._formal

    def set_formal(self, formal):
        self._formal = formal

    def get_complexity(self):
        return self._complexity

    def set_complexity(self, complexity):
        self._complexity = complexity

    def set_cost(self, cost):
        self._cost = cost

    def get_tree(self):
        return self._tree

    def __simplify_and_sensors_tree(self, value):
        sensor_list = ()
        replace_list = ()

        if self._config.getboolean('POPULATION', 'sensor_spec'):
            config_sensor_list = sorted(self._config.get_list('POPULATION', 'sensor_list'))
            sensor_list = ['S' + str(x) for x in config_sensor_list]
            replace_list = ['z' + str(x) for x in range(len(config_sensor_list))]
        else:
            amount_sensors = self._config.getint('POPULATION', 'sensors')
            # Replace the available sensors in the individual expression
            sensor_list = ['S' + str(x) for x in range(amount_sensors)]
            replace_list = ['z' + str(x) for x in range(amount_sensors)]

        for i in range(len(replace_list)):
            value = value.replace(replace_list[i], sensor_list[i])

        # Create the Individual Tree after the sensor replacement
        self._tree = Lisp_Tree_Expr(value)

        if self._config.getboolean('OPTIMIZATION', 'simplify'):
            return self._tree.get_simplified_tree_as_string()

        return value

    def __generate_indiv_regressive_tree(self, value, indiv_type=None):
        min_depth = 0
        max_depth = 0
        new_value = ""

        # Maxdepthfirst change while we are creating the first population
        if indiv_type:
            if indiv_type == 1:
                min_depth = Individual._maxdepthfirst
                max_depth = Individual._maxdepthfirst
            elif indiv_type == 2 or indiv_type == 3:
                min_depth = int(self._config.get('GP', 'mindepth'))
                max_depth = Individual._maxdepthfirst
            elif indiv_type == 4:
                min_depth = int(self._config.get('GP', 'mindepth'))
                max_depth = 1
            else:
                min_depth = int(self._config.get('GP', 'mindepth'))
                max_depth = int(self._config.get('GP', 'maxdepth'))

        else:
            min_depth = int(self._config.get('GP', 'mindepth'))
            max_depth = int(self._config.get('GP', 'maxdepth'))

        # Check if the seed character is in the string
        index = value.find('@')
        if index == -1:
            return

        # Split the value in two strings, not containing the first seed character
        begin_str = value[:index]
        end_str = value[index + 1:]

        # Count the amounts of '(' until the first seed character (This is the depth of the seed)
        counter = Counter(begin_str)
        begin_depth = counter['('] - counter[')']

        leaf_node = False
        if begin_depth >= max_depth:
            leaf_node = True
        elif (begin_depth < min_depth and end_str.find('@') == -1) or indiv_type == 3:
            leaf_node = False
        else:
            leaf_node = MatlabEngine.rand() < self._config.getfloat('POPULATION', 'leaf_prob')

        if leaf_node:
            use_sensor = MatlabEngine.rand() < self._config.getfloat('POPULATION', 'sensor_prob')
            if use_sensor:
                sensor_number = math.ceil(MatlabEngine.rand() * self._config.getint('POPULATION', 'sensors')) - 1
                new_value = begin_str + 'z' + str(sensor_number).rstrip('0').rstrip('.') + end_str
            else:
                range = self._config.getfloat('POPULATION', 'range')
                precision = self._config.get('POPULATION', 'precision')
                # Generate a float number between -range and +range with a precision of 'precision'
                new_exp = (("%." + precision + "f") % ((MatlabEngine.rand() - 0.5) * 2 * range))
                new_value = begin_str + new_exp + end_str
        else:
            # Create a node
            op_num = math.ceil(MatlabEngine.rand() * Operations.get_instance().length())
            op = Operations.get_instance().get_operation_from_op_num(op_num)
            if (op["nbarg"] == 1):
                new_value = begin_str + '(' + op["op"] + ' @)' + end_str
                new_value = self.__generate_indiv_regressive_tree(new_value, indiv_type)
            else:
                # nbrag == 2
                new_value = begin_str + '(' + op["op"] + ' @ @)' + end_str
                new_value = self.__generate_indiv_regressive_tree(new_value, indiv_type)
                new_value = self.__generate_indiv_regressive_tree(new_value, indiv_type)

        return new_value

    def __crossover_tree(self, value_1, value_2):
        """
            Extract a subtree out of a tree, extract a correct subtree out of
            another tree (with depth that can fit into maxdepth). Then interchange
            the two subtrees inputs:

            :param value_1: first tree (lisp ascii expression)
            :param value_2: second tree (lisp ascii expression)
            returned by set_GP_parameters.m
            :return:
            m1: first new tree (lisp ascii expression)                              %
            m2: second new tree (lisp ascii expression)
        """
        maxtries = self._config.getint("GP", "maxtries")
        mutmindepth = self._config.getint("GP", "mutmindepth")
        maxdepth = self._config.getint("GP", "maxdepth")

        correct = False
        count = 0

        tmp_value_1 = value_1
        tmp_value_2 = value_2

        while not correct and count < maxtries:
            # Extracting subtrees
            value_1, sm1, n = self.__extract_subtree(tmp_value_1, mutmindepth, maxdepth, maxdepth)  # check extract_subtree comments
            value_2, sm2, n2 = self.__extract_subtree(tmp_value_2, mutmindepth, n, maxdepth - n + 1)

            # n or n2 < 0 indicates the extraction was not correct for any reason.
            correct = n > 0 and n2 > 0
            count += 1

        if correct:
            # Replacing subtrees
            value_1 = value_1.replace('@', sm2)
            value_2 = value_2.replace('@', sm1)
            """
            %if gen_param.preevaluation
            %   eval(['peval=@' gen_param.preev_function ';']);
            %   f=peval;
            %   preevok1=feval(f,m1);
            %   preevok2=feval(f,m2);
            %   fail=1-preevok1*preevok2;
            %end
            """
        # correct == false means that we could not find a candidate substitution
        # in maxtries tests. We will select other individuals.

        return value_1, value_2, not correct

    def __mutate_tree(self, value, mutation_type):
        fail = False

        mutmindepth = self._config.getint("GP", "mutmindepth")
        maxdepth = self._config.getint("GP", "maxdepth")
        sensor_spec = self._config.getboolean("POPULATION", "sensor_spec")
        sensors = self._config.getint("POPULATION", 'sensors')
        mutation_types = self._config.get_list("GP", 'mutation_types')

        # equi probability for each mutation type selected.
        if mutation_type == Individual.MutationType.ANY:
            rand_number = MatlabEngine.rand()
            mutation_type = mutation_types[int(np.floor(rand_number * len(mutation_types)))]

        if mutation_type in [Individual.MutationType.REMOVE_SUBTREE_AND_REPLACE, Individual.MutationType.SHRINK]:
            preevok = False
            while not preevok:
                # remove subtree and grow new subtree
                value, _, _ = self.__extract_subtree(value, mutmindepth, maxdepth, maxdepth)

                if mutation_type == Individual.MutationType.REMOVE_SUBTREE_AND_REPLACE:
                    value = self.__generate_indiv_regressive_tree(value, 0)
                else:
                    value = self.__generate_indiv_regressive_tree(value, 4)

                if value:
                    if sensor_spec:
                        config_sensor_list = sorted(self._config.get_list('POPULATION', 'sensor_list'))
                    else:
                        config_sensor_list = range(sensors-1, -1, -1)

                    for i in range(len(config_sensor_list)):
                        value = value.replace("z%d" % i, "S%d" % config_sensor_list[i])

                    """
                    if sensor_spec:
                        config_sensor_list = sorted(self._config.get_list('POPULATION', 'sensor_list'))
                        for i in range(len(config_sensor_list)):
                            value = value.replace("z%d" % i, "S%d" % config_sensor_list[i])
                    else:
                        for i in range(sensors, 0, -1):
                            value = value.replace("z%d" % (i - 1), "S%d" % (i - 1))
                    """
                    preevok = True
                    # if gen_param.preevaluation
                    #   eval(['peval=@' gen_param.preev_function ';']);
                    #   f=peval;
                    #   preevok=feval(f,m);
                    # end
                else:
                    preevok = True

            return value, not value

        elif mutation_type == Individual.MutationType.REPARAMETRIZATION:
            value = self.__reparam_tree(value)
            return value, False

        elif mutation_type == Individual.MutationType.HOIST:
            controls = self._config.getint("POPULATION", "controls")
            prob_threshold = 1 / float(controls)

            expression_tree = Lisp_Tree_Expr(value)
            cl = [stree.to_string() for stree in expression_tree.get_root_node()._nodes]

            changed = False
            k = 0

            for nc in MatlabEngine.randperm(controls):
                k += 1
                # control law is cropped if it is the last one and no change happend before
                if (MatlabEngine.rand() < prob_threshold) or (k == controls and not changed):
                    _, sm, _, = self.__extract_subtree('(root '+cl[nc - 1]+')', mutmindepth+1, maxdepth, maxdepth+1)

                    if sm:
                        cl[nc - 1] = sm

                    changed = not sm is None

            value = "(root %s)" % " ".join(cl[:controls])
            return value, False

        else:
            raise NotImplementedError("Mutation type %s not implemented" % mutation_type)

    def __extract_subtree(self, m, mindepth, subtreedepthmax, maxdepth):
        expression_tree = Lisp_Tree_Expr(m)
        candidates = []
        for node in expression_tree.internal_nodes():
            if mindepth <= node.get_depth() <= maxdepth:
                if node.get_subtreedepth() <= subtreedepthmax:
                    candidates.append(node)

        if candidates:
            candidates.sort(key=lambda x: x.get_expr_index(), reverse=False)
            n = int(np.ceil(MatlabEngine.rand() * len(candidates))) - 1
            extracted_node = candidates[n]
            index = extracted_node.get_expr_index()
            new_value = m[:index] + m[index:].replace(extracted_node.to_string(), '@', 1)
            return new_value, extracted_node.to_string(), extracted_node.get_subtreedepth()
        else:
            return [], [], -1

    def __reparam_tree(self, value):
        def leaf_value_generator():
            leaf_value = (MatlabEngine.rand() - 0.5) * 2 * self._range
            return "%0.*f" % (self._precision, leaf_value)

        return self.__change_const_tree(value, leaf_value_generator)

    def __change_const_tree(self, expression, leaf_value_generator):
        expression_tree = Lisp_Tree_Expr(expression)
        for leaf in expression_tree.leaf_nodes():
            if not leaf.is_sensor():
                leaf._arg = leaf_value_generator()
        return expression_tree.get_expanded_tree_as_string()

    def __str__(self):
        return "value: %s\n" % self.get_value() + \
               "type: %s\n" % self.get_type() + \
               "cost_history: %s\n" % self.get_cost_history() + \
               "evaluation_time: %s\n" % self.get_evaluation_time() + \
               "appearences: %s\n" % self.get_appearences() + \
               "hash: %s\n" % self.get_hash().__repr__() + \
               "formal: %s\n" % self.get_formal() + \
               "complexity: %s\n" % self.get_complexity()
