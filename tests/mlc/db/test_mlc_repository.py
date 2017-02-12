import unittest
import shutil
import os

from MLC.mlc_parameters.mlc_parameters import Config, saved
from MLC.db.mlc_repository import MLCRepository
from MLC.individual.Individual import Individual
from MLC.Population.Population import Population
from MLC.config import set_working_directory

from MLC.arduino.protocol import ProtocolConfig, REPORT_MODES
from MLC.arduino.boards import Mega, Due


class MLCRepositoryTest(unittest.TestCase):
    WORKSPACE_DIR = os.path.abspath("/tmp/")
    EXPERIMENT_NAME = "test_mlc_repository"

    test_board_config = ProtocolConfig(connection=None,
                                       board_type=Mega,
                                       report_mode=REPORT_MODES.BULK,
                                       read_count=1000,
                                       read_delay=2000,
                                       analog_resolution=12)

    def __create_board_config(self, digital_input_pins, digital_output_pins, analog_input_pins, analog_output_pins, pwm_pins):
        return ProtocolConfig(connection=None, board_type=Mega, report_mode=REPORT_MODES.BULK, read_count=1000, read_delay=2000, analog_resolution=12,
                              digital_input_pins=digital_input_pins ,
                              digital_output_pins=digital_output_pins,
                              analog_input_pins=analog_input_pins,
                              analog_output_pins=analog_output_pins,
                              pwm_pins=pwm_pins)

    @classmethod
    def setUpClass(cls):
        Config._instance = Config.from_dictionary({"BEHAVIOUR": {"save": "false"},
                                                   "POPULATION": {
                                                       "size": "3",
                                                       "range": 0,
                                                       "precision": 0
                                                   },
                                                   "OPTIMIZATION": {
                                                       "probrep": 0,
                                                       "probmut": 0,
                                                       "probcro": 0,
                                                       "cascade": "1,1",
                                                       "simplify": "false"
                                                   }})

        set_working_directory(MLCRepositoryTest.WORKSPACE_DIR)
        if not os.path.exists(MLCRepositoryTest.WORKSPACE_DIR):
            os.makedirs(MLCRepositoryTest.WORKSPACE_DIR)

        os.makedirs(os.path.join(MLCRepositoryTest.WORKSPACE_DIR,
                                 MLCRepositoryTest.EXPERIMENT_NAME))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(os.path.join(MLCRepositoryTest.WORKSPACE_DIR,
                                   MLCRepositoryTest.EXPERIMENT_NAME))

    def __get_new_repo(self):
        MLCRepository._instance = None
        MLCRepository.make("test_mlc_repository")
        return MLCRepository.get_instance()

    def test_add_individual(self):
        mlc_repo = self.__get_new_repo()

        # mlc repository is empty
        self.assertEqual(mlc_repo.count_individual(), 0)

        # add the first individual
        indiv_id, exists = mlc_repo.add_individual(Individual("1+1"))
        self.assertEqual(indiv_id, 1)
        self.assertFalse(exists)
        self.assertEqual(mlc_repo.count_individual(), 1)

        # trying to add an Individual with the same value
        indiv_id, exists = mlc_repo.add_individual(Individual("1+1"))
        self.assertEqual(indiv_id, 1)
        self.assertTrue(exists)
        self.assertEqual(mlc_repo.count_individual(), 1)

        # adds another individual
        indiv_id, exists = mlc_repo.add_individual(Individual("2+2"))
        self.assertEqual(indiv_id, 2)
        self.assertFalse(exists)
        self.assertEqual(mlc_repo.count_individual(), 2)

    def test_get_individuals(self):
        mlc_repo = self.__get_new_repo()
        mlc_repo.add_individual(Individual("1+1"))
        mlc_repo.add_individual(Individual("2+2"))

        # get individuals
        individual = mlc_repo.get_individual(1)
        self.assertEqual(individual.get_value(), "1+1")

        individual = mlc_repo.get_individual(2)
        self.assertEqual(individual.get_value(), "2+2")

        # get individual data
        data = mlc_repo.get_individual_data(1)
        self.assertEqual(data.get_appearances(), 0)
        self.assertEqual(data.get_value(), "1+1")
        self.assertEqual(data.get_cost_history(), {})

        data = mlc_repo.get_individual_data(2)
        self.assertEqual(data.get_appearances(), 0)
        self.assertEqual(data.get_value(), "2+2")
        self.assertEqual(data.get_cost_history(), {})

        # invalid id
        try:
            individual = mlc_repo.get_individual(3)
            self.assertTrue(False)
        except KeyError:
            self.assertTrue(True)

    def test_add_population(self):
        mlc_repo = self.__get_new_repo()

        mlc_repo.add_individual(Individual("1+1"))
        mlc_repo.add_individual(Individual("2+2"))
        mlc_repo.add_individual(Individual("3+3"))
        self.assertEqual(mlc_repo.count_individual(), 3)

        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [1, 2, 3]
        p._costs = [4, 5, 6]
        p._ev_time = [7, 8, 9]
        p._gen_method = [10, 11, 12]

        # add population to the mlc_repository
        self.assertEqual(mlc_repo.count_population(), 0)
        mlc_repo.add_population(p)
        self.assertEqual(mlc_repo.count_population(), 1)

        # obtain population
        p_from_repo = mlc_repo.get_population(1)

        # check population content
        self.assertEqual(p_from_repo._individuals, p._individuals)
        self.assertEqual(p_from_repo._costs, p._costs)
        self.assertEqual(p_from_repo._ev_time, p._ev_time)
        self.assertEqual(p_from_repo._gen_method, p._gen_method)

    def test_add_population_with_invalid_individual(self):
        mlc_repo = self.__get_new_repo()

        # add population with invalid individual
        p = Population(1, 0, Config.get_instance(), mlc_repo)
        p._individuals = [100]

        try:
            mlc_repo.add_population(p)
            self.assertTrue(False)
        except KeyError:
            self.assertTrue(True)

    def test_get_individual_data(self):
        mlc_repo = self.__get_new_repo()

        # add individuals
        mlc_repo.add_individual(Individual("1+1"))
        mlc_repo.add_individual(Individual("2+2"))
        mlc_repo.add_individual(Individual("3+3"))
        mlc_repo.add_individual(Individual("4+4"))

        # first population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [1, 2, 1]
        p._costs = [4, 5, 6]
        p._ev_time = [5, 6, 7]
        mlc_repo.add_population(p)

        # second population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [3, 4, 2]
        p._costs = [7, 4, 9]
        p._ev_time = [8, 5, 10]

        mlc_repo.add_population(p)

        # check idividuals data loaded from the mlc_repo
        self.assertEqual(mlc_repo.count_population(), 2)

        # Individual 1 have two appearances in the first generation
        data = mlc_repo.get_individual_data(1)
        self.assertEqual(data.get_value(), "1+1")
        self.assertEqual(data.get_appearances(), 2)
        self.assertEqual(data.get_cost_history(), {1: [(4.0, 5), (6.0, 7)]})

        # Individual 2 have two appearances
        data = mlc_repo.get_individual_data(2)
        self.assertEqual(data.get_value(), "2+2")
        self.assertEqual(data.get_appearances(), 2)
        self.assertEqual(data.get_cost_history(), {1: [(5.0, 6)], 2: [(9.0, 10)]})

        # Individual 3 have one appearances
        data = mlc_repo.get_individual_data(3)
        self.assertEqual(data.get_value(), "3+3")
        self.assertEqual(data.get_appearances(), 1)
        self.assertEqual(data.get_cost_history(), {2: [(7.0, 8)]})

        # Individual 4 have one appearances
        data = mlc_repo.get_individual_data(4)
        self.assertEqual(data.get_value(), "4+4")
        self.assertEqual(data.get_appearances(), 1)
        self.assertEqual(data.get_cost_history(), {2: [(4.0, 5)]})

        # get individual data from invalid individual
        try:
            data = mlc_repo.get_individual_data(100)
            self.assertTrue(False)
        except KeyError, ex:
            self.assertTrue(True)

    def test_update_individual_cost(self):
        mlc_repo = self.__get_new_repo()

        # add individuals
        mlc_repo.add_individual(Individual("1+1"))
        mlc_repo.add_individual(Individual("2+2"))

        # add first population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [1, 2, 1]
        p._costs = [4, 5, 6]
        p._ev_time = [5, 6, 7]
        mlc_repo.add_population(p)

        # add second population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [2, 1, 2]
        p._costs = [8, 9, 10]
        p._ev_time = [11, 12, 13]
        mlc_repo.add_population(p)

        # update cost for individual 1
        mlc_repo.update_individual_cost(1, 45, 46)

        # check cost update in the first population
        p = mlc_repo.get_population(1)
        self.assertEqual(p._individuals, [1, 2, 1])
        self.assertEqual(p._costs, [45.0, 5.0, 45.0])
        self.assertEqual(p._ev_time, [46, 6, 46])

        # check cost update in the second population
        p = mlc_repo.get_population(2)
        self.assertEqual(p._individuals, [2, 1, 2])
        self.assertEqual(p._costs, [8, 45, 10])
        self.assertEqual(p._ev_time, [11, 46, 13])

    def test_update_individual_cost_in_generation(self):
        mlc_repo = self.__get_new_repo()

        # add individuals
        mlc_repo.add_individual(Individual("1+1"))
        mlc_repo.add_individual(Individual("2+2"))

        # add first population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [1, 2, 1]
        p._costs = [4, 5, 6]
        p._ev_time = [5, 6, 7]
        mlc_repo.add_population(p)

        # add second population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [2, 1, 2]
        p._costs = [8, 9, 10]
        p._ev_time = [11, 12, 13]
        mlc_repo.add_population(p)

        # update cost for individual 1
        mlc_repo.update_individual_cost(1, 45, 46, generation=1)

        # check cost update in the first population
        p = mlc_repo.get_population(1)
        self.assertEqual(p._individuals, [1, 2, 1])
        self.assertEqual(p._costs, [45, 5, 45])
        self.assertEqual(p._ev_time, [46, 6, 46])

        # check cost update in the second population
        p = mlc_repo.get_population(2)
        self.assertEqual(p._individuals, [2, 1, 2])
        self.assertEqual(p._costs, [8, 9, 10])
        self.assertEqual(p._ev_time, [11, 12, 13])

    def test_reload_individuals_in_memory_loss_data(self):
        mlc_repo = self.__get_new_repo()

        # add individuals
        mlc_repo.add_individual(Individual("1+1"))
        mlc_repo.add_individual(Individual("2+2"))

        # add population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [2, 1, 2]

        # reload mlc_repository using another instance
        mlc_repo = self.__get_new_repo()
        self.assertEqual(mlc_repo.count_individual(), 0)
        self.assertEqual(mlc_repo.count_population(), 0)

    def test_reload_individuals_from_file(self):
        with saved(Config.get_instance()) as config:
            config.set("BEHAVIOUR", "save", "true")
            config.set("BEHAVIOUR", "savedir", "test.db")
            config.set("POPULATION", "sensor_spec", "false")
            config.set("POPULATION", "sensors", "0")
            config.set("OPTIMIZATION", "simplify", "false")

            mlc_repo = self.__get_new_repo()

            # add individuals
            mlc_repo.add_individual(Individual("1+1"))
            mlc_repo.add_individual(Individual("2+2"))

            # add population
            p = Population(3, 0, Config.get_instance(), mlc_repo)
            p._individuals = [2, 1, 2]
            mlc_repo.add_population(p)

            # check status
            self.assertEqual(mlc_repo.count_individual(), 2)
            self.assertEqual(mlc_repo.count_population(), 1)

            # reload mlc_repository using another instance
            mlc_repo = self.__get_new_repo()
            self.assertEqual(mlc_repo.count_individual(), 2)
            self.assertEqual(mlc_repo.count_population(), 1)

    def test_remove_from_population(self):
        mlc_repo = self.__get_new_repo()

        # add individuals
        mlc_repo.add_individual(Individual("1+1"))
        mlc_repo.add_individual(Individual("2+2"))
        mlc_repo.add_individual(Individual("3+3"))
        mlc_repo.add_individual(Individual("4+4"))

        # add first population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [1, 2, 1]
        mlc_repo.add_population(p)

        # add second population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [1, 2, 3]
        mlc_repo.add_population(p)

        # add third population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [1, 2, 4]
        mlc_repo.add_population(p)

        # remove last population
        mlc_repo.remove_population_from(2)

        # last generation must be removed
        self.assertEqual(mlc_repo.count_population(), 1)

        # first generation exists
        p = mlc_repo.get_population(1)
        self.assertEqual(p._individuals, [1, 2, 1])

        # all individuals exists and the third individual do not appear in any generation
        self.assertEqual(mlc_repo.count_individual(), 4)

        # remove unused individuals
        deleted = mlc_repo.remove_unused_individuals()
        self.assertEqual(deleted, 2)
        self.assertEqual(mlc_repo.count_individual(), 2)

        individual = mlc_repo.get_individual(1)
        self.assertEqual(individual.get_value(), "1+1")

        individual = mlc_repo.get_individual(2)
        self.assertEqual(individual.get_value(), "2+2")

        try:
            individual = mlc_repo.get_individual(3)
            self.assertTrue(False)
        except KeyError:
            self.assertTrue(True)

    def test_remove_population_to(self):
        mlc_repo = self.__get_new_repo()

        # add individuals
        mlc_repo.add_individual(Individual("1+1"))
        mlc_repo.add_individual(Individual("2+2"))
        mlc_repo.add_individual(Individual("3+3"))
        mlc_repo.add_individual(Individual("4+4"))
        mlc_repo.add_individual(Individual("5+5"))

        # add  population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [1, 1, 1]
        mlc_repo.add_population(p)

        # add population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [2, 2, 2]
        mlc_repo.add_population(p)

        # add population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [3, 3, 3]
        mlc_repo.add_population(p)

        # add population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [4, 4, 4]
        mlc_repo.add_population(p)

        self.assertEqual(mlc_repo.count_population(), 4)

        # remove generations 1 to 2
        mlc_repo.remove_population_to(2)
        self.assertEqual(mlc_repo.count_population(), 2)

        p = mlc_repo.get_population(1)
        self.assertEqual(p._individuals, [3, 3, 3])

        p = mlc_repo.get_population(2)
        self.assertEqual(p._individuals, [4, 4, 4])

        # New generation must be number 3
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [5, 5, 5]
        mlc_repo.add_population(p)

        self.assertEqual(mlc_repo.count_population(), 3)

        p = mlc_repo.get_population(1)
        self.assertEqual(p._individuals, [3, 3, 3])

        p = mlc_repo.get_population(2)
        self.assertEqual(p._individuals, [4, 4, 4])

        p = mlc_repo.get_population(3)
        self.assertEqual(p._individuals, [5, 5, 5])

    def test_remove_population_to_clear_generations(self):
        mlc_repo = self.__get_new_repo()

        # add individuals
        mlc_repo.add_individual(Individual("1+1"))
        mlc_repo.add_individual(Individual("2+2"))
        mlc_repo.add_individual(Individual("3+3"))
        mlc_repo.add_individual(Individual("4+4"))
        mlc_repo.add_individual(Individual("5+5"))

        # add  population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [1, 1, 1]
        mlc_repo.add_population(p)

        # add population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [2, 2, 2]
        mlc_repo.add_population(p)

        # add population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [3, 3, 3]
        mlc_repo.add_population(p)

        self.assertEqual(mlc_repo.count_population(), 3)

        # Remove all generations (1 to 3)
        mlc_repo.remove_population_to(3)
        self.assertEqual(mlc_repo.count_population(), 0)

        # Insert populations again
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [3, 3, 3]
        mlc_repo.add_population(p)

        # add population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [4, 4, 4]
        mlc_repo.add_population(p)

        # add population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [5, 5, 5]
        mlc_repo.add_population(p)

        self.assertEqual(mlc_repo.count_population(), 3)

        p = mlc_repo.get_population(1)
        self.assertEqual(p._individuals, [3, 3, 3])

        p = mlc_repo.get_population(2)
        self.assertEqual(p._individuals, [4, 4, 4])

        p = mlc_repo.get_population(3)
        self.assertEqual(p._individuals, [5, 5, 5])

    def test_cut_generation(self):
        """
        Cut a generation using remove_population_from/remove_population_last
        :return:
        """
        mlc_repo = self.__get_new_repo()

        # add individuals
        mlc_repo.add_individual(Individual("1+1"))
        mlc_repo.add_individual(Individual("2+2"))
        mlc_repo.add_individual(Individual("3+3"))
        mlc_repo.add_individual(Individual("4+4"))
        mlc_repo.add_individual(Individual("5+5"))

        # add  population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [1, 1, 1]
        mlc_repo.add_population(p)

        # add population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [2, 2, 2]
        mlc_repo.add_population(p)

        # add population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [3, 3, 3]
        mlc_repo.add_population(p)

        # add population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [4, 4, 4]
        mlc_repo.add_population(p)

        # add population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [5, 5, 5]
        mlc_repo.add_population(p)

        self.assertEqual(mlc_repo.count_population(), 5)

        # Cut population 4
        mlc_repo.remove_population_from(4+1)
        mlc_repo.remove_population_to(4-1)

        # remove unused individuals
        mlc_repo.remove_unused_individuals()

        self.assertEqual(mlc_repo.count_population(), 1)
        self.assertEqual(mlc_repo.count_individual(), 1)

        p = mlc_repo.get_population(1)
        self.assertEqual(p._individuals, [4, 4, 4])

        individual = mlc_repo.get_individual(4)
        self.assertEqual(individual.get_value(), "4+4")

    def test_remove_population_to_from_bad_values(self):
        mlc_repo = self.__get_new_repo()

        # add individuals
        mlc_repo.add_individual(Individual("1+1"))
        mlc_repo.add_individual(Individual("2+2"))
        mlc_repo.add_individual(Individual("3+3"))
        mlc_repo.add_individual(Individual("4+4"))
        mlc_repo.add_individual(Individual("5+5"))

        # add  population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [1, 1, 1]
        mlc_repo.add_population(p)

        # add population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [2, 2, 2]
        mlc_repo.add_population(p)

        # add population
        p = Population(3, 0, Config.get_instance(), mlc_repo)
        p._individuals = [3, 3, 3]
        mlc_repo.add_population(p)

        self.assertEqual(mlc_repo.count_population(), 3)

        # Remove all generations (1 to 3)
        mlc_repo.remove_population_to(10)
        self.assertEqual(mlc_repo.count_population(), 0)

    def test_save_board_configuration_empty_pins(self):
        mlc_repo = self.__get_new_repo()
        board_id = mlc_repo.save_board_configuration(board_config=MLCRepositoryTest.test_board_config)
        board_config = mlc_repo.load_board_configuration(board_id)

        self.assertEqual(board_id, 1)
        self.assertEqual(board_config.board_type, MLCRepositoryTest.test_board_config.board_type)
        self.assertEqual(board_config.report_mode, MLCRepositoryTest.test_board_config.report_mode)
        self.assertEqual(board_config.read_count, MLCRepositoryTest.test_board_config.read_count)
        self.assertEqual(board_config.read_delay, MLCRepositoryTest.test_board_config.read_delay)
        self.assertEqual(board_config.analog_resolution, MLCRepositoryTest.test_board_config.analog_resolution)

    def test_update_board_config(self):
        # add board configuration
        mlc_repo = self.__get_new_repo()
        board_id = mlc_repo.save_board_configuration(board_config=MLCRepositoryTest.test_board_config)

        # update board configuration
        new_board_config = ProtocolConfig(connection=None, board_type=Due, report_mode=REPORT_MODES.AVERAGE, read_count=2000, read_delay=3000, analog_resolution=10)
        updated_board_id = mlc_repo.save_board_configuration(board_config=new_board_config, board_id=board_id)
        self.assertEqual(updated_board_id, board_id)

        # load board configuration and check values
        board_config = mlc_repo.load_board_configuration(updated_board_id)
        self.assertEqual(board_config.board_type, new_board_config.board_type)
        self.assertEqual(board_config.report_mode, new_board_config.report_mode)
        self.assertEqual(board_config.read_count, new_board_config.read_count)
        self.assertEqual(board_config.read_delay, new_board_config.read_delay)
        self.assertEqual(board_config.analog_resolution, new_board_config.analog_resolution)

    def test_update_board_config_invalid_id(self):
        # add board configuration
        mlc_repo = self.__get_new_repo()
        board_id = mlc_repo.save_board_configuration(board_config=MLCRepositoryTest.test_board_config)

        try:
            updated_board_id = mlc_repo.save_board_configuration(board_config=MLCRepositoryTest.test_board_config, board_id=board_id+1)
            self.assertTrue(False)
        except KeyError:
            self.assertTrue(True)

    def test_load_invalid_id(self):
        mlc_repo = self.__get_new_repo()
        board_id = mlc_repo.save_board_configuration(board_config=MLCRepositoryTest.test_board_config)

        try:
            board_config = mlc_repo.load_board_configuration(board_id+1)
            self.assertTrue(False)
        except KeyError:
            self.assertTrue(True)

    def test_save_board_pins(self):
        mlc_repo = self.__get_new_repo()

        board = self.__create_board_config(digital_input_pins=[1, 2, 3],
                                           digital_output_pins=[4, 5, 6],
                                           analog_input_pins=[7, 8, 9],
                                           analog_output_pins=[10, 11, 12],
                                           pwm_pins=[13, 14, 15])

        board_id = mlc_repo.save_board_configuration(board)
        board_config = mlc_repo.load_board_configuration(board_id)

        self.assertEqual(board_id, 1)
        self.assertEqual(board_config.digital_input_pins,  [1, 2, 3])
        self.assertEqual(board_config.digital_output_pins, [4, 5, 6])
        self.assertEqual(board_config.analog_input_pins,   [7, 8, 9])
        self.assertEqual(board_config.analog_output_pins,  [10, 11, 12])
        self.assertEqual(board_config.pwm_pins,            [13, 14, 15])

    def test_update_board_pins(self):
        mlc_repo = self.__get_new_repo()

        # save a board configuration
        board = self.__create_board_config(digital_input_pins=[1, 2, 3],
                                           digital_output_pins=[4, 5, 6],
                                           analog_input_pins=[7, 8, 9],
                                           analog_output_pins=[10, 11, 12],
                                           pwm_pins=[13, 14, 15])

        board_id = mlc_repo.save_board_configuration(board)

        # update board configuration
        updated_board = self.__create_board_config(digital_input_pins=[21, 22, 23],
                                                   digital_output_pins=[24, 25, 26],
                                                   analog_input_pins=[27, 28, 29],
                                                   analog_output_pins=[30, 31, 32],
                                                   pwm_pins=[33, 34, 35])

        updated_board_id = mlc_repo.save_board_configuration(updated_board, board_id=board_id)

        # check pin values update
        self.assertEqual(updated_board_id, board_id)
        self.assertEqual(updated_board.digital_input_pins, [21, 22, 23])
        self.assertEqual(updated_board.digital_output_pins, [24, 25, 26])
        self.assertEqual(updated_board.analog_input_pins, [27, 28, 29])
        self.assertEqual(updated_board.analog_output_pins, [30, 31, 32])
        self.assertEqual(updated_board.pwm_pins, [33, 34, 35])
