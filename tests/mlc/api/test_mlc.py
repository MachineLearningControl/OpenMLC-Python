import unittest
import os

import MLC.api
from MLC.api.mlc import MLCLocal

from MLC.Simulation import Simulation
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.config import set_working_directory

class MLCWorkspaceTest(unittest.TestCase):
    WORKSPACE_DIR = os.path.abspath("/tmp/mlc_workspace/")
    DEFAULT_CONFIGURATION = {"BEHAVIOUR": {"save_dir"}}

    ORIGINAL_EXPERIMENT = "primer_prueba"
    ORIGINAL_CONFIGURATION = {"BEHAVIOUR": {"save": "true", "savedir": "primer_prueba.mlc", "showeveryitbest": "true"}}

    NEW_EXPERIMENT = "new_experiment"
    NEW_CONFIGURATION = {"PARAMS": {"test_param": "test_value"}}

    @classmethod
    def setUpClass(cls):
        set_working_directory(MLCWorkspaceTest.WORKSPACE_DIR)

        if not os.path.exists(MLCWorkspaceTest.WORKSPACE_DIR):
            os.makedirs(MLCWorkspaceTest.WORKSPACE_DIR)

        experiment_cf, experiment_db = MLCLocal.get_experiment_files(MLCWorkspaceTest.WORKSPACE_DIR,
                                                                     MLCWorkspaceTest.ORIGINAL_EXPERIMENT)

        original_config = Config.from_dictionary(MLCWorkspaceTest.ORIGINAL_CONFIGURATION)
        original_config.write(open(experiment_cf, "wt"))
        Config.get_instance().read(experiment_cf)
        s = Simulation()

    def test_obtain_experiments(self):
        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
        experiments = mlc.get_workspace_experiments()
        self.assertEqual(len(experiments), 1)
        self.assertEqual(experiments[0], MLCWorkspaceTest.ORIGINAL_EXPERIMENT)

    def test_obtain_configuration_from_a_closed_experiment(self):
        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
        try:
            mlc.get_experiment_configuration(MLCWorkspaceTest.ORIGINAL_EXPERIMENT)
            self.assertTrue(False, "Configuration from a closed experiment should not be obtained")
        except MLC.api.mlc.ClosedExperimentException:
            self.assertTrue(True)

    def test_open_invalid_experiment(self):
        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
        try:
            mlc.open_experiment("invalid_name")
            self.assertTrue(False)
        except MLC.api.mlc.ExperimentNotExistException:
            self.assertTrue(True)

    def test_obtain_configuration(self):
        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
        mlc.open_experiment(MLCWorkspaceTest.ORIGINAL_EXPERIMENT)
        configuration = mlc.get_experiment_configuration(MLCWorkspaceTest.ORIGINAL_EXPERIMENT)

        # check configuration structure
        self.assertIsInstance(configuration, dict)
        self.assertTrue(configuration.has_key("BEHAVIOUR"))
        self.assertIsInstance(configuration["BEHAVIOUR"], dict)
        self.assertTrue(configuration["BEHAVIOUR"].has_key("showeveryitbest"))
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
            mlc.new_experiment(MLCWorkspaceTest.ORIGINAL_EXPERIMENT, MLCWorkspaceTest.DEFAULT_CONFIGURATION)
            self.assertTrue(False)
        except MLC.api.mlc.DuplicatedExperimentError:
            self.assertTrue(True)

    def test_create_experiment_and_obtain_configuration(self):
        try:
            mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
            mlc.new_experiment(MLCWorkspaceTest.NEW_EXPERIMENT, MLCWorkspaceTest.NEW_CONFIGURATION)
            mlc.open_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)
            configuration = mlc.get_experiment_configuration(MLCWorkspaceTest.NEW_EXPERIMENT)

            # check configuration structure
            self.assertIsInstance(configuration, dict)
            self.assertTrue(configuration.has_key("PARAMS"))
            self.assertIsInstance(configuration["PARAMS"], dict)
            self.assertTrue(configuration["PARAMS"].has_key("test_param"))
            self.assertEqual(configuration["PARAMS"]["test_param"], "test_value")

        finally:
            # FIXME: use Setup/TearDown testcase
            os.unlink(os.path.join(MLCWorkspaceTest.WORKSPACE_DIR, MLCWorkspaceTest.NEW_EXPERIMENT)+".conf")
            os.unlink(os.path.join(MLCWorkspaceTest.WORKSPACE_DIR, MLCWorkspaceTest.NEW_EXPERIMENT)+".mlc")


    def test_delete_experiment(self):
        mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)

        try:
            # delete an experiment that not exists
            try:
                mlc.delete_experiment_from_workspace(MLCWorkspaceTest.NEW_EXPERIMENT)
                self.assertTrue(False)
            except MLC.api.mlc.ExperimentNotExistException:
                self.assertTrue(True)

            mlc.new_experiment(MLCWorkspaceTest.NEW_EXPERIMENT, MLCWorkspaceTest.NEW_CONFIGURATION)
            mlc.delete_experiment_from_workspace(MLCWorkspaceTest.NEW_EXPERIMENT)
            self.assertFalse(os.path.exists(os.path.join(MLCWorkspaceTest.WORKSPACE_DIR, MLCWorkspaceTest.NEW_EXPERIMENT)+".conf"))
            self.assertFalse(os.path.exists(os.path.join(MLCWorkspaceTest.WORKSPACE_DIR, MLCWorkspaceTest.NEW_EXPERIMENT)+".mlc"))

        finally:
            pass
            # FIXME: use Setup/TearDown testcase
            # os.unlink(os.path.join(MLCWorkspaceTest.WORKSPACE_DIR, MLCWorkspaceTest.NEW_EXPERIMENT) + ".conf")
            # os.unlink(os.path.join(MLCWorkspaceTest.WORKSPACE_DIR, MLCWorkspaceTest.NEW_EXPERIMENT) + ".mlc")

    def test_set_configuration(self):

        try:
            mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)

            # check original configuration
            mlc.new_experiment(MLCWorkspaceTest.NEW_EXPERIMENT, MLCWorkspaceTest.NEW_CONFIGURATION)
            mlc.open_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)
            original_config = mlc.get_experiment_configuration(MLCWorkspaceTest.NEW_EXPERIMENT)
            self.assertEqual(original_config["PARAMS"]["test_param"], "test_value")

            # chage paramenter value
            mlc.set_experiment_configuration(MLCWorkspaceTest.NEW_EXPERIMENT, {"PARAMS": {"test_param": "new_value"}})

            # reload mlc_workspace
            mlc_reloaded = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
            mlc.open_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)
            original_config = mlc.get_experiment_configuration(MLCWorkspaceTest.NEW_EXPERIMENT)
            self.assertEqual(original_config["PARAMS"]["test_param"], "new_value")

            # set specific parameter
            mlc = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
            mlc.open_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)
            mlc.set_experiment_configuration_parameter(MLCWorkspaceTest.NEW_EXPERIMENT, "another_section", "another_param", "another_value")

            # reload mlc_workspace
            mlc_reloaded = MLCLocal(working_dir=MLCWorkspaceTest.WORKSPACE_DIR)
            mlc_reloaded.open_experiment(MLCWorkspaceTest.NEW_EXPERIMENT)
            config = mlc_reloaded.get_experiment_configuration(MLCWorkspaceTest.NEW_EXPERIMENT)
            self.assertEqual(config["PARAMS"]["test_param"], "new_value")

            self.assertIn("another_section", config)
            self.assertIn("another_param", config["another_section"])
            self.assertEqual(config["another_section"]["another_param"], "another_value")

        finally:
            # FIXME: use Setup/TearDown testcase
            os.unlink(os.path.join(MLCWorkspaceTest.WORKSPACE_DIR, MLCWorkspaceTest.NEW_EXPERIMENT) + ".conf")
            os.unlink(os.path.join(MLCWorkspaceTest.WORKSPACE_DIR, MLCWorkspaceTest.NEW_EXPERIMENT) + ".mlc")
            pass