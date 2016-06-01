import unittest
import matlab.engine
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
    def setUpClass(cls):
        config_file = 'configuration.ini'
        generations_file = 'generation.txt'
        costs_file = 'costs_gen1.txt'

        '''
        FIXME: This is really UGLY!!!. Try later to at
        least set the path with absolute paths
        '''
        cls._eng = MatlabEngine.engine()

        # Load the config
        config = Config()
        config.read(config_file)

        # Fix seed and run program
        cls._eng.rand('seed', 20.0, nargout=0)
        cls._eng.workspace['wmlc'] = cls._eng.MLC2()
        cls._app = Application(cls._eng, config, "testing")
        cls._app.go(10, 0)

        a = Population.generations()
        print "Number of populations: " + str(a)

        cls._gen = []
        # Parse the generations
        with open(generations_file) as f:
            for line in f:
                # Chomp line
                cls._gen.append(line.rstrip())

        cls._costs = []
        # Parse the costs arrays
        with open(costs_file) as f:
            for line in f:
                # Chomp line
                cls._costs.append(line.rstrip())

    def test_generation_1(self):
        self._run_x_generation(1)

    def test_generation_2(self):
        self._run_x_generation(2)

    def test_generation_3(self):
        self._run_x_generation(3)

    def test_generation_4(self):
        self._run_x_generation(4)

    def test_generation_5(self):
        self._run_x_generation(5)

    def test_generation_6(self):
        self._run_x_generation(6)

    def test_generation_7(self):
        self._run_x_generation(7)

    def _run_x_generation(self, gen_number):
        indexes = \
            self._eng.eval('wmlc.population(' +
                           str(gen_number) + ').individuals')

        '''
        Stupid matlab arrays notation..., everything is a matrix,
        ALSO an array and not viceversa
        '''
        i = 1
        print 'Generation N# ', gen_number, ' - POP indexes: '
        print indexes[0]

        for index in indexes[0]:
            value = 'wmlc.table.individuals(' + str(index) + ').value'

            self.assertEqual(self._eng.eval(value),
                             self._gen[int(index) - 1])
            print "Individual N# ", i, " OK!"
            i += 1


def suite():
    a_suite = unittest.TestSuite()
    a_suite.addTest(IntegrationTest1())
    return a_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)
