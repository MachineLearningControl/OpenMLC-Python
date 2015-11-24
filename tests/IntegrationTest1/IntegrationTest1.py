import unittest
import matlab.engine
from MLC.Config.Config import Config
from MLC.Application import Application

"""
This test run the application setting the seed to a fix number. The output of
the pure MATLAB Application is stored in the file 'generations.txt'
"""


class IntegrationTest1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config_file = 'configuration.ini'
        generations_file = 'generation.txt'

        '''
        FIXME: This is really UGLY!!!. Try later to at
        least set the path with absolute paths
        '''
        cls._eng = matlab.engine.start_matlab()
        cls._eng.addpath("../../matlab_code")
        cls._eng.addpath("../../matlab_code/MLC_tools")
        cls._eng.addpath("../../matlab_code/MLC_tools/Demo")

        # Load the config
        config = Config()
        config.read(config_file)

        # Fix seed and run program
        cls._eng.rand('seed', 20.0, nargout=0)
        cls._eng.workspace['wmlc'] = cls._eng.MLC2()
        cls._app = Application(cls._eng, config, "testing")
        cls._app.go(3, 0)

        a = cls._eng.eval('length(wmlc.population)')
        print "Number of populations: " + str(a)

        cls._gen = []
        # Parse the generations
        with open(generations_file) as f:
            for line in f:
                # Chomp line
                cls._gen.append(line.rstrip())

    def test_first_generation(self):
        self._run_x_generation(1)

    def test_second_generation(self):
        self._run_x_generation(2)

    def test_third_generation(self):
        self._run_x_generation(3)

    def _run_x_generation(self, gen_number):
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