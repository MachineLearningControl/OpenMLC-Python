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

import shutil
import os
import unittest

from MLC.api.MLCLocal import MLCLocal
from MLC.Application import Application, MLC_CALLBACKS
from MLC.config import set_working_directory
from MLC.config import get_working_directory
from MLC.config import get_test_path
from MLC.db.mlc_repository import MLCRepository
from MLC.mlc_parameters.mlc_parameters import saved
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Population.Creation import BaseCreation
from MLC.Simulation import Simulation
from nose.tools import nottest
from tests.test_helpers import TestHelper


class ApplicationTest(unittest.TestCase):
    on_start = 0
    on_start_counter_2 = 0
    on_evaluate = 0
    on_new_generation = []
    on_finish = 0
    experiment_name = "test_application"
    workspace_dir = os.path.abspath("/tmp/mlc_workspace/")
    test_conf_path = os.path.join(get_test_path(), TestHelper.DEFAULT_CONF_FILENAME)
    experiment_dir = os.path.join(workspace_dir, experiment_name)
    mlc_local = None

    @classmethod
    def setUpClass(cls):
        TestHelper.load_default_configuration()
        try:
            os.makedirs(ApplicationTest.workspace_dir)
        except OSError:
            shutil.rmtree(ApplicationTest.workspace_dir)
            os.makedirs(ApplicationTest.workspace_dir)

        # Create the MLCLocal and the workspace of MLC, and create
        # a new experiment to be used to test the callbacks
        set_working_directory(ApplicationTest.workspace_dir)
        ApplicationTest.mlc_local = MLCLocal(working_dir=ApplicationTest.workspace_dir)

    @classmethod
    def tearDownClass(cls):
        # Erase the MLC workspace dir of this tests
        shutil.rmtree(ApplicationTest.workspace_dir)

    def test_numpy_warnings_on_evaluation_script(self):
        # MLC catches the numpy warnings and notify them in its log. By doing this,
        # numpy warnings are set to throw exception. The idea of this test is to
        # prove that this behaviour (numpy warnings as Exceptions) does not affect
        # the evaluation scripts
        experiment_name = "numpy_warnings"

        numpy_ev_script = "numpy_warnings_ev_script.py"
        numpy_ev_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), numpy_ev_script)

        numpy_config = "numpy_warnings_config.ini"
        numpy_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), numpy_config)

        ApplicationTest.mlc_local.new_experiment(experiment_name=experiment_name,
                                                 experiment_configuration=numpy_config_path,
                                                 evaluation_script=numpy_ev_path)

        Config.get_instance().set("EVALUATOR", "evaluation_function", "numpy_warnings_ev_script")

        ApplicationTest.mlc_local.open_experiment(experiment_name)
        try:
            ApplicationTest.mlc_local.go(experiment_name=experiment_name,
                                         to_generation=2,
                                         from_generation=0,
                                         callbacks={})
        except FloatingPointError:
            self.assertEquals(True, False)

        ApplicationTest.mlc_local.close_experiment(experiment_name)
        ApplicationTest.mlc_local.delete_experiment(experiment_name)

        self.assertEquals(True, True)

    def test_callback_on_evaluate(self):
        with saved(Config.get_instance()) as config:
            Config.get_instance().set("POPULATION", "size", "10")
            Config.get_instance().set("BEHAVIOUR", "save", "false")

            def test_on_start_callback():
                ApplicationTest.on_start += 1

            def test_on_evaluate_callback(individual_id, cost):
                ApplicationTest.on_evaluate += 1

            def test_on_new_generation_callback(generation_number):
                ApplicationTest.on_new_generation.append(generation_number)

            def test_on_finish_callback():
                ApplicationTest.on_finish += 1

            callbacks_dict = {MLC_CALLBACKS.ON_START:          test_on_start_callback,
                              MLC_CALLBACKS.ON_EVALUATE:       test_on_evaluate_callback,
                              MLC_CALLBACKS.ON_NEW_GENERATION: test_on_new_generation_callback,
                              MLC_CALLBACKS.ON_FINISH:         test_on_finish_callback}

            ApplicationTest.mlc_local.new_experiment(ApplicationTest.experiment_name,
                                                     ApplicationTest.test_conf_path)
            ApplicationTest.mlc_local.open_experiment(ApplicationTest.experiment_name)
            ApplicationTest.mlc_local.go(experiment_name=ApplicationTest.experiment_name,
                                         to_generation=2,
                                         from_generation=0,
                                         callbacks=callbacks_dict)
            ApplicationTest.mlc_local.close_experiment(ApplicationTest.experiment_name)
            ApplicationTest.mlc_local.delete_experiment(ApplicationTest.experiment_name)

            self.assertEqual(ApplicationTest.on_start,          1)
            self.assertEqual(ApplicationTest.on_evaluate,       2 * 10)
            self.assertEqual(ApplicationTest.on_new_generation, range(1, 2 + 1))
            self.assertEqual(ApplicationTest.on_finish,         1)

    def test_list_of_callbacks(self):
        with saved(Config.get_instance()) as config:
            Config.get_instance().set("POPULATION", "size", "10")
            Config.get_instance().set("BEHAVIOUR", "save", "false")

            ApplicationTest.on_start = 0
            ApplicationTest.on_start_counter_2 = 0

            def test_on_start_callback():
                ApplicationTest.on_start += 1

            def test_on_start_callback_increment_2():
                ApplicationTest.on_start_counter_2 += 1

            start_callbacks = [test_on_start_callback, test_on_start_callback_increment_2]

            ApplicationTest.mlc_local.new_experiment(ApplicationTest.experiment_name,
                                                     ApplicationTest.test_conf_path)
            ApplicationTest.mlc_local.open_experiment(ApplicationTest.experiment_name)
            ApplicationTest.mlc_local.go(experiment_name=ApplicationTest.experiment_name,
                                         to_generation=2,
                                         from_generation=0,
                                         callbacks={MLC_CALLBACKS.ON_START: start_callbacks})
            ApplicationTest.mlc_local.close_experiment(ApplicationTest.experiment_name)
            ApplicationTest.mlc_local.delete_experiment(ApplicationTest.experiment_name)

            self.assertEqual(ApplicationTest.on_start, 1)
            self.assertEqual(ApplicationTest.on_start_counter_2, 1)

    @unittest.skip
    def test_set_custom_gen_creator(self):
        with saved(Config.get_instance()) as config:
            Config.get_instance().set("POPULATION", "size", "5")
            Config.get_instance().set("BEHAVIOUR", "save", "false")

            from MLC.Population.Creation.BaseCreation import BaseCreation
            from MLC.individual.Individual import Individual

            class TestCreator(BaseCreation):

                def __init__(self):
                    BaseCreation.__init__(self)

                def create(self, gen_size):
                    MLCRepository.get_instance().add_individual(Individual("(root 1)"))
                    MLCRepository.get_instance().add_individual(Individual("(root 2)"))
                    MLCRepository.get_instance().add_individual(Individual("(root 3)"))
                    MLCRepository.get_instance().add_individual(Individual("(root 4)"))
                    MLCRepository.get_instance().add_individual(Individual("(root 5)"))

                def individuals(self):
                    return [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]

            simulation = Simulation("")
            mlc = Application(simulation, gen_creator=TestCreator())
            mlc.go(to_generation=1)

            # Assert first Population was filled using the TestCreator
            population = MLCRepository.get_instance().get_population(1)
            self.assertEqual(population.get_individuals(), [1, 2, 3, 4, 5])
