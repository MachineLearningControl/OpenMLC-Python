import sys
sys.path.insert(1, '../.')

import unittest
from MLC.mlc_parameters.mlc_parameters import MLCParameters
import os
import numpy as np


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self._file = open('test', 'w+')
        self._file.write('[TEST]\n')
        self._file.write('sigma = 5\n')
        self._file.write('arange = 1:10\n')
        self._file.write('arange_step = 1:13:3\n')
        self._file.write('arange_float = 1:5:0.5\n')
        self._file.write('array = 1,2,3,4\n')
        self._file.close()
        self._config = MLCParameters()
        self._config.read('test')

    def tearDown(self):
        os.remove('test')
        self._config = None

    def test_common_type(self):
        expected = '5'
        actual = self._config.get_param('TEST', 'sigma')
        self.assertEqual(expected, actual)

    def test_array_creation(self):
        expected = np.array([1, 2, 3, 4])
        actual = self._config.get_param('TEST', 'array', type='array')
        comparison = (expected == actual).all()
        self.assertEqual(comparison, True)

    def test_arange_creation_without_step(self):
        expected = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
        actual = self._config.get_param('TEST', 'arange', type='arange')
        comparison = (expected == actual).all()
        self.assertEqual(comparison, True)

    def test_arange_creation_float_type(self):
        expected = np.arange(1, 5., .5)
        actual = self._config.get_param('TEST', 'arange_float',
                                        type='arange', dtype='float')
        comparison = (expected == actual).all()
        self.assertEqual(comparison, True)

    def test_arange_creation_with_step(self):
        expected = np.array([1, 4, 7, 10])
        actual = self._config.get_param('TEST', 'arange_step', type='arange')
        comparison = (expected == actual).all()
        self.assertEqual(comparison, True)


if __name__ == '__main__':
    # runner = unittest.TextTestRunner()
    # test_suite = suite()
    # runner.run(test_suite)
    a_suite = unittest.TestLoader().loadTestsFromTestCase(ConfigTest)
    unittest.TextTestRunner(verbosity=2).run(a_suite)

