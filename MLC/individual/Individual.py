import numpy as np
from MLC.matlab_engine import MatlabEngine

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
    def __init__(self, config=None, mlc_ind=None, value=None):
        self._eng = MatlabEngine.engine()
        self._config = config

        if mlc_ind:
            self._mlc_ind = mlc_ind
        else:
            if value:
                self._mlc_ind = self._eng.MLCind(value)
            else:
                self._mlc_ind = self._eng.MLCind()

    def get_matlab_object(self):
        return self._mlc_ind

    def generate(self, mlc_parameters, varargin):
        """
        generate individual from scratch or from unfinished individual.

        MLCIND.generate(MLC_PARAMETERS,MODE) creates an individual using mode MODE.
        MODE is a number which interpretation depends on the MLCIND.type property.
        (Not designed to be played with by user, code dive for details)

        MLCIND.generate(MLC_PARAMETERS,VALUE) creates an individual with MLCIND.value VALUE.

        matlab_impl: return self._eng.generate(self._mlc_ind, mlc_parameters, varargin)
        """

         # TODO: refactor MLCParameters access
        param_individual_type = self._eng.eval('wmlc.parameters.individual_type')
        param_controls = int(self._eng.eval('wmlc.parameters.controls'))

        if param_individual_type == 'tree':
            self.set_type('tree')

            if type(varargin) == int:
                value = '(root @' + ' @' * (param_controls - 1) + ')'
                for i in range(1, param_controls+1):
                    value = self.__generate_indiv_regressive_tree(value, mlc_parameters, varargin)
                self.set_value(value)
            else:
                self.set_value(varargin)

            self.set_value(self.__simplify_and_sensors_tree(self.get_value(), mlc_parameters))
            string_hash = self._eng.calculate_hash_from_value(self.get_matlab_object()) #string_hash = DataHash(mlcind.value);
            self.set_hash(self._eng.eval("hex2num('%s')" % string_hash[0:16]))
            self.set_formal(self._eng.readmylisp_to_formal_MLC(self.get_value(), mlc_parameters))
            self.set_complexity(self.__tree_complexity(self.get_value(), mlc_parameters))
            return

        raise NotImplementedError("Individual::generate() is not implemented for type %s" % self.get_type())

    def evaluate(self, mlc_parameters, varargin):
        return self._eng.evaluate(self._mlc_ind, mlc_parameters, varargin)

    def mutate(self, mlc_parameters):
        new_ind, fail = self._eng.mutate(self._mlc_ind, mlc_parameters, nargout=2)
        return Individual(mlc_ind=new_ind), fail

    def crossover(self, other_individual, mlc_parameters):
        new_ind, new_ind2, fail = self._eng.crossover(self._mlc_ind,
                                                      other_individual.get_matlab_object(),
                                                      mlc_parameters,
                                                      nargout=3)

        return Individual(mlc_ind=new_ind), Individual(mlc_ind=new_ind2), fail

    def compare(self, other_individual):
        """
        Compare two MLCind value properties.
        ISEQUAL=COMPARE(MLCIND1,MLCIND2) returns 1 if both values are equal.
        """
        if self.get_type() == 'tree':
            return self.get_value() == other_individual.get_value()

        raise NotImplementedError("Individual::compare() is not implemented for type %s" % self.get_type())

    def textoutput(self):
        return self._eng.textoutput(self._mlc_ind)

    def preev(self, mlc_patameters):
        return self._eng.textoutput(self._mlc_ind, mlc_patameters)

    def get_value(self):
        return self._eng.get_value(self._mlc_ind)

    def set_value(self, value):
        return self._eng.set_value(self._mlc_ind, value)

    def get_type(self):
        return self._eng.get_type(self._mlc_ind)

    def set_type(self, type):
        return self._eng.set_type(self._mlc_ind, type)

    def get_cost(self):
        return int(self._eng.get_cost(self._mlc_ind))

    def get_cost_history(self):
        return self._eng.get_cost_history(self._mlc_ind)

    def get_evaluation_time(self):
        return self._eng.get_evaluation_time(self._mlc_ind)

    def get_appearences(self):
        return int(self._eng.get_appearences(self._mlc_ind))

    def get_hash(self):
        return self._eng.get_hash(self._mlc_ind)

    def set_hash(self, hash):
        return self._eng.set_hash(self._mlc_ind, hash)

    def get_formal(self):
        return self._eng.get_formal(self._mlc_ind)

    def set_formal(self, formal):
        return self._eng.set_formal(self._mlc_ind, formal)

    def get_complexity(self):
        return int(self._eng.get_complexity(self._mlc_ind))

    def set_complexity(self, complexity):
        return self._eng.set_complexity(self._mlc_ind, complexity)

    def __simplify_and_sensors_tree(self, value, mlc_parameters):
        return self._eng.private_simplify_and_sensors_tree(self.get_matlab_object(), value, mlc_parameters)

    def __tree_complexity(self, value, mlc_parameters):
        return self._eng.private_tree_complexity(self.get_matlab_object(), value, mlc_parameters)

    def __generate_indiv_regressive_tree(self, value, mlc_parameters, indiv_type):
        return self._eng.private_generate_indiv_regressive_tree(self.get_matlab_object(), value, mlc_parameters, indiv_type)

    def __str__(self):
        return "value: %s\n" % self.get_value() + \
               "type: %s\n" % self.get_type() + \
               "cost_history: %s\n" % self.get_cost_history() + \
               "evaluation_time: %s\n" % self.get_evaluation_time() + \
               "appearences: %s\n" % self.get_appearences() + \
               "hash: %s\n" % self.get_hash() + \
               "formal: %s\n" % self.get_formal() + \
               "complexity: %s\n" % self.get_complexity()
