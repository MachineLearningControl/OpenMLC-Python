import unittest
import matlab.engine
import numpy as np
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Application import Application
from MLC.Population.Population import Population
from MLC.matlab_engine import MatlabEngine
from MLC.mlc_table.MLCTable import MLCTable
from MLC.Application import Simulation
import sys, os
import yaml

"""
This test run the application setting the seed to a fix number. The output of
the pure MATLAB Application is stored in the file 'generations.txt'
"""


class MLCIntegrationTest(unittest.TestCase):
    TEST_DIRECTORY = None
    GENERATIONS = None

    @classmethod
    def _populate_indiv_dict(cls):
        individuals_file = os.path.join(MLCIntegrationTest.TEST_DIRECTORY, 'individuals.txt')
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
        populations_file = os.path.join(MLCIntegrationTest.TEST_DIRECTORY, 'populations.txt')
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
        config_file = os.path.join(MLCIntegrationTest.TEST_DIRECTORY, './configuration.ini')
        cls._eng = MatlabEngine.engine()

        # Load the config
        config = Config.get_instance()
        config.read(config_file)

        # Load randoms from file
        random_file = 'matlab_randoms.txt'
        MatlabEngine.clear_random_values()
        MatlabEngine.load_random_values(random_file)

        simulation = Simulation()

        for g in MLCIntegrationTest.GENERATIONS:
            # clear static values
            MLCTable._instance = None
            cls._app = Application(simulation, "testing")
            cls._app.go(g, 0)

        a = cls._app.get_simulation().generations()
        print "Number of populations: " + str(a)

        # List with individuals data
        cls._indivs = []
        cls._populate_indiv_dict()

        cls._pops = []
        cls ._populate_pop_dict()

    ## FIXME: Test methods should be cerated dynamically in the setUp method.
    def test_generation_1(self):
        if max(MLCIntegrationTest.GENERATIONS) >= 1:
            self._run_x_generation(1)

    # @unittest.skip
    def test_generation_2(self):
        if max(MLCIntegrationTest.GENERATIONS) >= 2:
            self._run_x_generation(2)

    # @unittest.skip
    def test_generation_3(self):
        if max(MLCIntegrationTest.GENERATIONS) >= 3:
            self._run_x_generation(3)

    # @unittest.skip
    def test_generation_4(self):
        if max(MLCIntegrationTest.GENERATIONS) >= 4:
            self._run_x_generation(4)

    # @unittest.skip
    def test_generation_5(self):
        if max(MLCIntegrationTest.GENERATIONS) >= 5:
            self._run_x_generation(5)

    # @unittest.skip
    def test_generation_6(self):
        if max(MLCIntegrationTest.GENERATIONS) >= 6:
            self._run_x_generation(6)

    # @unittest.skip
    def test_generation_7(self):
        if max(MLCIntegrationTest.GENERATIONS) >= 7:
            self._run_x_generation(7)

    def _run_x_generation(self, gen_number):
        print "Checking Generation %s" % gen_number

        print "Check Indvidual properties..."
        self._check_indiv_values(gen_number)

        print "Check Indvidual properties..."
        pop = self._app.get_simulation().get_generation(gen_number)
        self._check_indiv_property(gen_number, pop.get_individuals(), 'index', 'int')
        self._check_indiv_property(gen_number, pop.get_costs(), 'cost', 'float')
        self._check_indiv_property(gen_number, pop.get_gen_methods(), 'gen_method', 'int')
        # self._check_cellarray_property(gen_number, 'parents', 'parents')

    def _check_indiv_values(self, gen_number):
        i = 1
        indexes = self._app.get_simulation().get_generation(gen_number).get_individuals()
        print "Check %s indviduals from generation %s" % (len(indexes), gen_number)
        for index in indexes:
            indiv = MLCTable.get_instance().get_individual(index)

            self.assertEqual(indiv.get_value(), self._indivs[int(index) - 1]['value'])
            self.assertEqual(indiv.get_complexity(), int(self._indivs[int(index) - 1]['complexity']))

            if isinstance(indiv.get_formal(), str):
                self.assertEqual(indiv.get_formal(), self._indivs[int(index) - 1]['formal'])
            else:
                self.assertEqual(" ".join(indiv.get_formal()), self._indivs[int(index) - 1]['formal'])

            print "Individual N# ", i, " OK!"
            i += 1

    def _check_indiv_property(self, gen_number, values, map_property, type=None):
        # List of dictionaries with the values of every individual
        pop = self._pops[gen_number - 1]
        for i in range(len(pop)):
            if str(values[i]) != str(pop[i][map_property]):
                print "Indiv N#{0} - Value obtained: {1}".format(i + 1, values[i])
                print "Indiv N#{0} - Value expected: {1}".format(i + 1, str(pop[i][map_property]))

            if type == 'int':
                self.assertEqual(int(values[i]),
                                 int(pop[i][map_property]))
            elif type == 'float':
                obtained = float(values[i])
                expected = float(pop[i][map_property])
                if (not np.isclose(obtained, expected)):
                    self.assertEqual(True, False)
                else:
                    self.assertEqual(True, True)
            else:
                self.assertEqual(values[i], pop[i][map_property])

def get_test_class(test_dir, integration_test):
    generations = integration_test['generations']
    if isinstance(generations, int):
        generations = [generations]

    class IntegrationTest(MLCIntegrationTest):
        MLCIntegrationTest.TEST_DIRECTORY = test_dir
        MLCIntegrationTest.GENERATIONS = generations

    return IntegrationTest

def execute_integration_test(test_name, integration_test):
    print "Running '%s' with %s generations: %s" % (integration_test['name'],
                                                    integration_test['generations'],
                                                    integration_test['description'])
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(get_test_class(test_dir, integration_test)))
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    config = yaml.load(open('integration_tests.yaml', 'r'))
    all_tests = config['integration_tests']
    test_to_run = {}

    if len(sys.argv) == 1:
        for test_name in config['default']:
            test_to_run[test_name] = all_tests[test_name]
    else:
        for test_name in sys.argv[1:]:
            if test_name in all_tests:
                test_to_run[test_name] = all_tests[test_name]
            else:
                print "'%s'? there is no integration test with that name!" % test_name

    for test_dir, integration_test in test_to_run.iteritems():
        execute_integration_test(test_dir, integration_test)