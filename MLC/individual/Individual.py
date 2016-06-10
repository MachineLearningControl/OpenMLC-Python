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
    def __init__(self, config = None, mlc_ind = None):
        self._eng = MatlabEngine.engine()
        self._config = config

        if mlc_ind:
            self._mlc_ind = mlc_ind
        else:
            self._mlc_ind = self._eng.MLCind()

    def get_matlab_object(self):
        return self._mlc_ind

    def generate(self, mlc_parameters, varargin):
        return self._eng.generate(self._mlc_ind, mlc_parameters, varargin)

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
        return self._eng.compare(self._mlc_ind, other_individual)

    def textoutput(self):
        return self._eng.textoutput(self._mlc_ind)

    def preev(self, mlc_patameters):
        return self._eng.textoutput(self._mlc_ind, mlc_patameters)