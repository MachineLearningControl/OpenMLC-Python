import unittest
import matlab.engine
import numpy as np
from MLC.Config.Config import Config
from MLC.Application import Application
from MLC.Population.Population import Population
from MLC.matlab_engine import MatlabEngine

"""
This test run the application setting the seed to a fix number. The output of
the pure MATLAB Application is stored in the file 'generations.txt'
"""


class IntegrationTest1(unittest.TestCase):

    @classmethod
    def _populate_indiv_dict(cls):
        individuals_file = 'individuals.txt'
        # Parse the generations
        with open(individuals_file) as f:
            for line in f:
                # Chomp line
                line = line.rstrip()

                # Create the individual as a dictionary
                indiv = {}
                properties = line.split('@')
                for prop in properties:
                    key_value = prop.split('=')
                    indiv[str(key_value[0])] = key_value[1]

                cls._indivs.append(indiv)

    @classmethod
    def _populate_pop_dict(cls):
        populations_file = 'populations.txt'
        with open(populations_file) as f:
            # Each line has a different population
            for line in f:
                # Chomp line
                line = line.rstrip()

                # Create the populations
                pop = []
                indivs = line.split('$')
                for indiv in indivs:
                    indiv_dict = {}
                    fields = indiv.split('@')
                    for field in fields:
                        key_value = field.split('=')
                        if key_value[0] != 'parents':
                            indiv_dict[key_value[0]] = key_value[1]
                        else:
                            parents = []
                            parents = key_value[1].split(',')
                            value = [float(i)
                                     for i in parents
                                     if parents != ['']]
                            indiv_dict[key_value[0]] = value
                    pop.append(indiv_dict)
                cls._pops.append(pop)

    @classmethod
    def setUpClass(cls):
        config_file = 'configuration.ini'
        cls._eng = MatlabEngine.engine()

        # Load the config
        config = Config.get_instance()
        config.read(config_file)

        # Fix seed and run program
        cls._eng.rand('seed', 20.0, nargout=0)
        cls._eng.workspace['wmlc'] = cls._eng.MLC2()
        cls._app = Application(cls._eng, config, "testing")
        cls._app.go(6, 0)

        a = Population.generations()
        print "Number of populations: " + str(a)

        # List with individuals data
        cls._indivs = []
        IntegrationTest1._populate_indiv_dict()

        cls._pops = []
        IntegrationTest1._populate_pop_dict()

    def test_generation_1(self):
        self._run_x_generation(1)

    # @unittest.skip
    def test_generation_2(self):
        self._run_x_generation(2)

    # @unittest.skip
    def test_generation_3(self):
        self._run_x_generation(3)

    # @unittest.skip
    def test_generation_4(self):
        self._run_x_generation(4)

    # @unittest.skip
    def test_generation_5(self):
        self._run_x_generation(5)

    # @unittest.skip
    def test_generation_6(self):
        self._run_x_generation(6)

    @unittest.skip
    def test_generation_7(self):
        self._run_x_generation(7)

    def _run_x_generation(self, gen_number):
        self._check_indiv_values(gen_number)
        self._check_indiv_property(gen_number, 'individuals',
                                   'index', 'int')
        self._check_indiv_property(gen_number, 'costs',
                                   'cost', 'float')
        self._check_indiv_property(gen_number, 'gen_method',
                                   'gen_method', 'int')
        self._check_cellarray_property(gen_number, 'parents', 'parents')

    def _check_indiv_values(self, gen_number):
        indexes = \
            self._eng.eval('wmlc.population(' +
                           str(gen_number) + ').individuals')

        '''
        Stupid matlab arrays notation..., everything is a matrix,
        ALSO an array and not viceversa
        '''
        i = 1

        for index in indexes[0]:
            value = 'wmlc.table.individuals(' + str(index) + ').value'

            self.assertEqual(self._eng.eval(value),
                             self._indivs[int(index) - 1]['value'])
            print "Individual N# ", i, " OK!"
            i += 1

    def _check_cellarray_property(self, gen_number, property, map_property):
        property_string = ('wmlc.population(' +
                           str(gen_number) +
                           ').' + property)
        values_obtained = self._eng.eval(property_string)

        pop = self._pops[gen_number - 1]
        for i in range(len(pop)):
            obtained = []
            if type(values_obtained[i]) is list:
                obtained = values_obtained[i]
            elif type(values_obtained[i]) is float:
                obtained = [values_obtained[i]]
            """
            else:
                print type(values_obtained[i])
                if len(values_obtained[i]) > 0:
                    obtained = [float(item)
                                for item in values_obtained[i][0]]
            """
            print "Value obtained: " + str(obtained)
            print "Value expected: " + str(pop[i][map_property])
            self.assertEqual(obtained, pop[i][map_property])

    def _check_indiv_property(self,
                              gen_number,
                              property,
                              map_property,
                              type=None):
        property_string = ('wmlc.population(' +
                           str(gen_number) + ').' + property)
        values_obtained = self._eng.eval(property_string)

        # List of dictionaries with the values of every individual
        pop = self._pops[gen_number - 1]
        for i in range(len(pop)):
            print "Value obtained: " + str(values_obtained[0][i])
            print "Value expected: " + str(pop[i][map_property])

            if type == 'int':
                self.assertEqual(int(values_obtained[0][i]),
                                 int(pop[i][map_property]))
            elif type == 'float':
                obtained = float(values_obtained[0][i])
                expected = float(pop[i][map_property])
                if (not np.isclose(obtained, expected)):
                    self.assertEqual(True, False)
                else:
                    self.assertEqual(True, True)
            else:
                self.assertEqual(values_obtained[0][i], pop[i][map_property])


def suite():
    a_suite = unittest.TestSuite()
    a_suite.addTest(IntegrationTest1())
    return a_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)
