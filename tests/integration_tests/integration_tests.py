# -*- coding: utf-8 -*-
# MLC (Machine Learning Control): A genetic algorithm library to solve chaotic problems
# Copyright (C) 2015-2017, Thomas Duriez (thomas.duriez@gmail.com)
# Copyright (C) 2015, Adrian Durán (adrianmdu@gmail.com)
# Copyright (C) 2015-2017, Ezequiel Torres Feyuk (ezequiel.torresfeyuk@gmail.com)
# Copyright (C) 2016-2017, Marco Germano Zbrun (marco.germano@intraway.com)
# Copyright (C) 2016-2017, Raúl Lopez Skuba (raulopez0@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import sys
import os
sys.path.append("../..")

import numpy as np
import shutil
import unittest
import yaml

from MLC.api.MLCLocal import MLCLocal
from MLC.Application import Application
from MLC.Common.RandomManager import RandomManager
from MLC.db.mlc_repository import MLCRepository
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Simulation import Simulation

"""
This test run the application setting the seed to a fix number. The output of
the pure MATLAB Application is stored in the file 'generations.txt'
"""


class MLCIntegrationTest(unittest.TestCase):
    TEST_DIRECTORY = None
    GENERATIONS = None
    WORKSPACE_DIR = os.path.abspath("/tmp/mlc_workspace/")
    EXPERIMENT_NAME = "integration_tests"

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
                            value = [int(i) for i in parents if parents != ['']]
                            indiv_dict[key_value[0]] = value
                    pop.append(indiv_dict)
                cls._pops.append(pop)

    @classmethod
    def setUpClass(cls):
        config_file = os.path.join(MLCIntegrationTest.TEST_DIRECTORY, './configuration.ini')
        ev_script = os.path.join(MLCIntegrationTest.TEST_DIRECTORY, './default_evaluation_script.py')
        preev_script = os.path.join(MLCIntegrationTest.TEST_DIRECTORY, './default_preevaluation_script.py')

        # Load the config
        config = Config.get_instance()
        config.read(config_file)

        # Load randoms from file
        random_file = 'matlab_randoms.txt'
        RandomManager.clear_random_values()
        RandomManager.load_random_values(random_file)

        # Create the workspace directory
        try:
            os.makedirs(MLCIntegrationTest.WORKSPACE_DIR)
        except OSError:
            shutil.rmtree(MLCIntegrationTest.WORKSPACE_DIR)
            os.makedirs(MLCIntegrationTest.WORKSPACE_DIR)

        # Create a new experiment, which will be used to
        cls._mlc = MLCLocal(working_dir=MLCIntegrationTest.WORKSPACE_DIR)
        cls._mlc.new_experiment(experiment_name=MLCIntegrationTest.EXPERIMENT_NAME,
                                experiment_configuration=config_file,
                                evaluation_script=ev_script,
                                preevaluation_script=preev_script)
        cls._mlc.open_experiment(experiment_name=MLCIntegrationTest.EXPERIMENT_NAME)

        for generation_params in MLCIntegrationTest.GENERATIONS:
            if isinstance(generation_params, int):
                cls._mlc.go(experiment_name=MLCIntegrationTest.EXPERIMENT_NAME,
                            to_generation=generation_params)

            elif isinstance(generation_params, list):
                cls._mlc.go(experiment_name=MLCIntegrationTest.EXPERIMENT_NAME,
                            from_generation=generation_params[0],
                            to_generation=generation_params[1])

            else:
                raise Exception("Integration test, bad value for generations param")

        # List with individuals data
        cls._indivs = []
        cls._populate_indiv_dict()

        cls._pops = []
        cls ._populate_pop_dict()

    @classmethod
    def tearDownClass(cls):
        cls._mlc.close_experiment(experiment_name=MLCIntegrationTest.EXPERIMENT_NAME)
        shutil.rmtree(MLCIntegrationTest.WORKSPACE_DIR)

    # FIXME: Test methods should be crated dynamically in the setUp method.
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
        print("Checking Generation %s" % gen_number)

        print("Check Indvidual properties...")
        self._check_indiv_values(gen_number)

        print("Check Indvidual properties...")
        pop = self._mlc.get_generation(MLCIntegrationTest.EXPERIMENT_NAME, gen_number)
        self._check_indiv_property(gen_number, pop.get_individuals(), 'index', 'int')
        self._check_indiv_property(gen_number, pop.get_costs(), 'cost', 'float')

        self._check_indiv_property(gen_number, pop.get_gen_methods(), 'gen_method', 'int')
        self._check_indiv_property(gen_number, pop.get_parents(), 'parents')

    def _check_indiv_values(self, gen_number):
        i = 1
        indexes = self._mlc.get_generation(MLCIntegrationTest.EXPERIMENT_NAME, gen_number).get_individuals()
        print("Check %s indviduals from generation %s" % (len(indexes), gen_number))
        for index in indexes:
            indiv = MLCRepository.get_instance().get_individual(index)

            self.assertEqual(indiv.get_value(), self._indivs[int(index) - 1]['value'])
            self.assertEqual(indiv.get_complexity(), int(self._indivs[int(index) - 1]['complexity']))

            if isinstance(indiv.get_formal(), str):
                self.assertEqual(indiv.get_formal(), self._indivs[int(index) - 1]['formal'])
            else:
                self.assertEqual(" ".join(indiv.get_formal()), self._indivs[int(index) - 1]['formal'])
            i += 1

    def _check_indiv_property(self, gen_number, values, map_property, type=None):
        # List of dictionaries with the values of every individual
        pop = self._pops[gen_number - 1]
        for i in range(len(pop)):
            if type == 'int':
                self.assertEqual(int(values[i]), int(pop[i][map_property]))
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
        MLCIntegrationTest.EXPERIMENT_NAME = test_dir

    return IntegrationTest


def execute_integration_test(test_dir, integration_test):
    print("Running '%s' with %s generations: %s" % (integration_test['name'],
                                                    integration_test['generations'],
                                                    integration_test['description']))
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
                print("'%s'? there is no integration test with that name!" % test_name)

    for test_dir, integration_test in test_to_run.items():
        execute_integration_test(test_dir, integration_test)
