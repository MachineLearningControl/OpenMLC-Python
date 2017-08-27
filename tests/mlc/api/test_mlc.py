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

from nose.tools import nottest
import configparser
import MLC.api
import os
import shutil
import unittest

from collections import OrderedDict
from MLC.api.MLCLocal import MLCLocal
from MLC.api.Experiment import Experiment

from MLC.config import set_working_directory
from MLC.Common.RandomManager import RandomManager
from MLC.db.mlc_repository import IndividualData
from MLC.individual.Individual import Individual as MLCIndividual
from MLC.Log.log import set_logger
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Population.Population import Population as MLCPopulation
from MLC.Simulation import Simulation

from MLC.arduino import boards
from MLC.arduino.protocol import ProtocolConfig
from MLC.arduino.connection.serialconnection import SerialConnectionConfig


class MLCWorkspaceTest(unittest.TestCase):
    WORKSPACE_DIR = os.path.abspath("/tmp/mlc_workspace/")
    FILE_WITH_RANDOMS = None
    ORIGINAL_EXPERIMENT = "test_first_experiment"
    ORIGINAL_CONFIGURATION = None
    NEW_EXPERIMENT = "test_new_experiment"
    NEW_CONFIGURATION = None

    def setUp(self):
        try:
            os.makedirs(MLCWorkspaceTest.WORKSPACE_DIR)
        except OSError:
            shutil.rmtree(MLCWorkspaceTest.WORKSPACE_DIR)
            os.makedirs(MLCWorkspaceTest.WORKSPACE_DIR)

        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
        # general settings for MLC
        set_logger('testing')
        set_working_directory(MLCWorkspaceTest.WORKSPACE_DIR)

        this_dir = os.path.dirname(os.path.abspath(__file__))
        MLCWorkspaceTest.ORIGINAL_CONFIGURATION = os.path.join(this_dir,
                                                               MLCWorkspaceTest.ORIGINAL_EXPERIMENT + ".conf")
        MLCWorkspaceTest.NEW_CONFIGURATION = os.path.join(this_dir,
                                                          MLCWorkspaceTest.NEW_EXPERIMENT + ".conf")
        mlc.new_experiment(MLCWorkspaceTest.ORIGINAL_EXPERIMENT,
                           MLCWorkspaceTest.ORIGINAL_CONFIGURATION)

        # random file for simulations
        MLCWorkspaceTest.FILE_WITH_RANDOMS = os.path.join(this_dir, "matlab_randoms.txt")

    def tearDown(self):
        shutil.rmtree(MLCWorkspaceTest.WORKSPACE_DIR)

    def test_obtain_experiments(self):
        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
        experiments = mlc.get_workspace_experiments()
        self.assertEqual(len(experiments), 1)
        self.assertEqual(experiments[0], MLCWorkspaceTest.ORIGINAL_EXPERIMENT)

    def test_obtain_configuration_from_a_closed_experiment(self):
        try:
            mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
            mlc.get_experiment_configuration(MLCWorkspaceTest.ORIGINAL_EXPERIMENT)
            self.assertTrue(False, "Configuration from a closed experiment should not be obtained")
        except MLC.api.mlc.ClosedExperimentException:
            self.assertTrue(True)

    def test_open_invalid_experiment(self):
        try:
            mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
            mlc.open_experiment("invalid_name")
            self.assertTrue(False)
        except MLC.api.mlc.ExperimentNotExistException:
            self.assertTrue(True)

    def test_obtain_configuration(self):
        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
        mlc.open_experiment(MLCWorkspaceTest.ORIGINAL_EXPERIMENT)
        configuration = mlc.get_experiment_configuration(MLCWorkspaceTest.ORIGINAL_EXPERIMENT)
        mlc.close_experiment(MLCWorkspaceTest.ORIGINAL_EXPERIMENT)

        # check configuration structure
        self.assertIsInstance(configuration, dict)
        self.assertTrue("BEHAVIOUR" in configuration)
        self.assertIsInstance(configuration["BEHAVIOUR"], dict)
        self.assertTrue("showeveryitbest" in configuration["BEHAVIOUR"])
        self.assertEqual(configuration["BEHAVIOUR"]["showeveryitbest"], "true")

    def test_open_and_close_experiment(self):
        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
        mlc.open_experiment(MLCWorkspaceTest.ORIGINAL_EXPERIMENT)
        mlc.close_experiment(MLCWorkspaceTest.ORIGINAL_EXPERIMENT)
        try:
            mlc.get_experiment_configuration(MLCWorkspaceTest.ORIGINAL_EXPERIMENT)
            self.assertTrue(False, "Configuration from a closed experiment should not be obtained")
        except MLC.api.mlc.ClosedExperimentException:
            self.assertTrue(True)

    def test_create_duplicated_experiment(self):
        try:
            mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
            mlc.new_experiment(MLCWorkspaceTest.ORIGINAL_EXPERIMENT,
                               MLCWorkspaceTest.ORIGINAL_CONFIGURATION)
            self.assertTrue(False)
        except MLC.api.mlc.DuplicatedExperimentError:
            self.assertTrue(True)

    def test_create_experiment_and_obtain_configuration(self):
        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
        mlc.new_experiment(MLCWorkspaceTest.NEW_EXPERIMENT,
                           MLCWorkspaceTest.NEW_CONFIGURATION)
        mlc.open_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)
        configuration = mlc.get_experiment_configuration(MLCWorkspaceTest.NEW_EXPERIMENT)
        mlc.close_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)
        mlc.delete_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)

        # check configuration structure
        self.assertIsInstance(configuration, dict)
        self.assertTrue(configuration.has_key("PARAMS"))
        self.assertIsInstance(configuration["PARAMS"], dict)
        self.assertTrue(configuration["PARAMS"].has_key("test_param"))
        self.assertEqual(configuration["PARAMS"]["test_param"], "test_value")

    def test_delete_experiment(self):
        # delete an experiment that not exists
        try:
            mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
            mlc.delete_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)
            self.assertTrue(False)
        except MLC.api.mlc.ExperimentNotExistException:
            self.assertTrue(True)

        mlc.new_experiment(MLCWorkspaceTest.NEW_EXPERIMENT,
                           MLCWorkspaceTest.NEW_CONFIGURATION)
        mlc.delete_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)
        self.assertFalse(os.path.exists(os.path.join(MLCWorkspaceTest.WORKSPACE_DIR,
                                                     MLCWorkspaceTest.NEW_EXPERIMENT)))

    def test_set_configuration(self):
        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)

        # check original configuration
        mlc.new_experiment(MLCWorkspaceTest.NEW_EXPERIMENT, MLCWorkspaceTest.NEW_CONFIGURATION)
        mlc.open_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)
        original_config = mlc.get_experiment_configuration(MLCWorkspaceTest.NEW_EXPERIMENT)
        self.assertEqual(original_config["PARAMS"]["test_param"], "test_value")
        # chage paramenter value
        mlc.set_experiment_configuration(MLCWorkspaceTest.NEW_EXPERIMENT, {"PARAMS": {"test_param": "new_value"}})
        mlc.close_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)

        # reload mlc_workspace
        mlc_reloaded = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
        mlc_reloaded.open_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)
        original_config = mlc_reloaded.get_experiment_configuration(MLCWorkspaceTest.NEW_EXPERIMENT)
        self.assertEqual(original_config["PARAMS"]["test_param"], "new_value")
        mlc_reloaded.close_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)

        # set specific parameter
        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
        mlc.open_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)
        mlc.set_experiment_configuration_parameter(MLCWorkspaceTest.NEW_EXPERIMENT,
                                                   "another_section", "another_param",
                                                   "another_value")
        mlc.close_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)

        # reload mlc_workspace
        mlc_reloaded = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
        mlc_reloaded.open_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)
        config = mlc_reloaded.get_experiment_configuration(MLCWorkspaceTest.NEW_EXPERIMENT)
        mlc_reloaded.close_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)
        mlc.delete_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)

        self.assertEqual(config["PARAMS"]["test_param"], "new_value")
        self.assertIn("another_section", config)
        self.assertIn("another_param", config["another_section"])
        self.assertEqual(config["another_section"]["another_param"], "another_value")

    def test_get_info_empty_simulation(self):
        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
        mlc.open_experiment(MLCWorkspaceTest.ORIGINAL_EXPERIMENT)
        info = mlc.get_experiment_info(MLCWorkspaceTest.ORIGINAL_EXPERIMENT)

        self._assert_key_value(info, "name", MLCWorkspaceTest.ORIGINAL_EXPERIMENT)
        self._assert_key_value(info, "generations", 0)
        self._assert_key_value(info, "individuals", 0)
        self._assert_key_value(info, "individuals_per_generation", 10)

        mlc.close_experiment(MLCWorkspaceTest.ORIGINAL_EXPERIMENT)
        mlc.delete_experiment(MLCWorkspaceTest.ORIGINAL_EXPERIMENT)

    def test_create_experiment_and_obtain_configuration(self):
        try:
            mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
            mlc.new_experiment(MLCWorkspaceTest.NEW_EXPERIMENT,
                               MLCWorkspaceTest.NEW_CONFIGURATION)
            mlc.open_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)
            configuration = mlc.get_experiment_configuration(
                MLCWorkspaceTest.NEW_EXPERIMENT)
            mlc.close_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)

            # check configuration structure
            self.assertIsInstance(configuration, dict)
            self.assertTrue("PARAMS" in configuration)
            self.assertIsInstance(configuration["PARAMS"], dict)
            self.assertTrue("test_param" in configuration["PARAMS"])
            self.assertEqual(configuration["PARAMS"]["test_param"],
                             "test_value")

        finally:
            # FIXME: use Setup/TearDown testcase
            mlc.delete_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)

    def test_get_default_board_configuration(self):
        try:
            mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
            mlc.new_experiment(MLCWorkspaceTest.NEW_EXPERIMENT,
                               MLCWorkspaceTest.NEW_CONFIGURATION)
            mlc.open_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)

            board_configuration, serial_connection = mlc.get_board_configuration(MLCWorkspaceTest.NEW_EXPERIMENT)

            self.assertEqual(board_configuration.board_type, boards.Due)
            self.assertEqual(board_configuration.read_count, 2)
            self.assertEqual(board_configuration.read_delay, 0)
            self.assertEqual(board_configuration.report_mode, 0)
            self.assertEqual(board_configuration.analog_resolution, 12)

            self.assertEqual(serial_connection.port, "/dev/ttyACM0")
            self.assertEqual(serial_connection.baudrate, 115200)
            self.assertEqual(serial_connection.parity, "N")
            self.assertEqual(serial_connection.stopbits, 1)
            self.assertEqual(serial_connection.bytesize, 8)

        finally:
            # FIXME: use Setup/TearDown testcase
            mlc.delete_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)

    def test_update_board_configuration(self):
        try:
            mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
            mlc.new_experiment(MLCWorkspaceTest.NEW_EXPERIMENT, MLCWorkspaceTest.NEW_CONFIGURATION)
            mlc.open_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)

            board_configuration, serial_connection = mlc.get_board_configuration(MLCWorkspaceTest.NEW_EXPERIMENT)

            new_board_config = ProtocolConfig(None, report_mode=12, read_count=10, read_delay=11,
                                              board_type=boards.Leonardo, analog_resolution=13)
            new_connection = SerialConnectionConfig("/dev/ttyACM1", baudrate=5000, parity="P", stopbits=2, bytesize=6)
            mlc.save_board_configuration(MLCWorkspaceTest.NEW_EXPERIMENT, new_board_config, new_connection)

            loaded_board_configuration, loaded_connection = mlc.get_board_configuration(MLCWorkspaceTest.NEW_EXPERIMENT)

            self.assertEqual(loaded_board_configuration.board_type, boards.Leonardo)
            self.assertEqual(loaded_board_configuration.read_count, 10)
            self.assertEqual(loaded_board_configuration.read_delay, 11)
            self.assertEqual(loaded_board_configuration.report_mode, 12)
            self.assertEqual(loaded_board_configuration.analog_resolution, 13)

            self.assertEqual(loaded_connection.port, "/dev/ttyACM1")
            self.assertEqual(loaded_connection.baudrate, 5000)
            self.assertEqual(loaded_connection.parity, "P")
            self.assertEqual(loaded_connection.stopbits, 2)
            self.assertEqual(loaded_connection.bytesize, 6)

        finally:
            # FIXME: use Setup/TearDown testcase
            mlc.delete_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)

    @nottest
    def test_go_and_check_simulation_info(self):
        # load random values for the simulation
        self._load_random_values()

        # Execute a simulation
        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
        mlc.new_experiment("test_go_and_check", MLCWorkspaceTest.ORIGINAL_CONFIGURATION)
        mlc.open_experiment("test_go_and_check")
        mlc.go("test_go_and_check", 2)

        # check simulation info
        info = mlc.get_experiment_info("test_go_and_check")
        self._assert_key_value(info, "name", "test_go_and_check")
        self._assert_key_value(info, "generations", 2)
        self._assert_key_value(info, "individuals", 11)
        self._assert_key_value(info, "individuals_per_generation", 10)

        mlc.close_experiment("test_go_and_check")
        mlc.delete_experiment("test_go_and_check")

    def test_go_and_get_individuals(self):
        # load random values for the simulation
        self._load_random_values()

        # Execute a simulation
        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
        mlc.new_experiment("test_go_and_check", MLCWorkspaceTest.ORIGINAL_CONFIGURATION)
        mlc.open_experiment("test_go_and_check", True)
        mlc.go("test_go_and_check", 2)

        # obtain individuals
        individuals = mlc.get_individuals("test_go_and_check")

        # check number of individuals
        self.assertEqual(len(individuals), 11)

        # TODO: Check individual values
        for indiv_id, indiv_data in individuals.items():
            self.assertIsInstance(indiv_data, IndividualData)

        # Test Update Individual Cost in all generations
        mlc.update_individual_cost("test_go_and_check", 2, 1000, 1001)

        indiv_data = mlc.get_individuals("test_go_and_check")[2]
        self.assertEqual(indiv_data.get_appearances(), 2)
        self.assertEqual(indiv_data.get_cost_history(), {1: [(1000.0, 1001)], 2: [(1000.0, 1001)]})
        mlc.close_experiment("test_go_and_check")
        mlc.delete_experiment("test_go_and_check")

    @nottest  # Don't remove this
    def test_go_and_get_generations(self):
        try:
                # load random values for the simulation
            self._load_random_values()

            # Execute a simulation
            mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
            mlc.new_experiment("test_go_and_check", MLCWorkspaceTest.ORIGINAL_CONFIGURATION)
            mlc.open_experiment("test_go_and_check")
            mlc.go("test_go_and_check", 2)

            # get first population
            first_generation = mlc.get_generation("test_go_and_check", 1)
            self.assertIsInstance(first_generation, MLCPopulation)

            # get second generation
            second_generation = mlc.get_generation("test_go_and_check", 2)
            self.assertIsInstance(second_generation, MLCPopulation)

            # third generation does not exist and must raise an Exception
            # TODO: Use a specific exception instead of IndexError

            try:
                third_generation = mlc.get_generation("test_go_and_check", 3)
                self.assertIsInstance(third_generation, MLCPopulation)
                self.assertTrue(False)
            except IndexError:
                self.assertTrue(True)

        finally:
            # FIXME: use Setup/TearDown testcase
            os.unlink(os.path.join(MLCWorkspaceTest.WORKSPACE_DIR, "test_go_and_check") + ".conf")
            os.unlink(os.path.join(MLCWorkspaceTest.WORKSPACE_DIR, "test_go_and_check") + ".mlc")
            pass

    def test_import_non_existent_experiment(self):
        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)

        import_experiment_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              "test4.mlc")
        mlc.import_experiment(import_experiment_path)
        self.assertTrue("test4" in mlc.get_workspace_experiments())
        mlc.delete_experiment("test4")

    def test_import_existent_experiment(self):
        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
        mlc.new_experiment("test4", MLCWorkspaceTest.ORIGINAL_CONFIGURATION)

        import_experiment_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              "test4.mlc")
        try:
            mlc.import_experiment(import_experiment_path)
            self.assertTrue(False)
        except MLC.api.mlc.DuplicatedExperimentError:
            self.assertTrue(True)
        finally:
            mlc.delete_experiment("test4")

    def test_import_experiment_with_erroneous_path(self):
        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
        import_experiment_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              "test5.mlc")
        try:
            mlc.import_experiment(import_experiment_path)
            self.assertTrue(False)
            mlc.delete_experiment("test5")
        except MLC.api.mlc.ImportExperimentPathNotExistException:
            self.assertTrue(True)
            self.assertFalse("test5" in mlc.get_workspace_experiments())

    def _assert_key_value(self, dictionary, key, value):
        self.assertIsInstance(dictionary, OrderedDict)
        self.assertIn(key, dictionary)
        self.assertEqual(dictionary[key], value)

    def _load_random_values(self):
        RandomManager.clear_random_values()
        RandomManager.load_random_values(MLCWorkspaceTest.FILE_WITH_RANDOMS)
