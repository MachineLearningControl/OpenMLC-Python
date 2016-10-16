import cmd
import argparse
import os

from MLC.mlc_parameters.mlc_parameters import Config
from MLC.matlab_engine import MatlabEngine
from MLC.Simulation import Simulation
from MLC.Application import Application
from MLC.db.mlc_repository import MLCRepository
from MLC.Population.Evaluation.EvaluatorFactory import EvaluatorFactory
from MLC.Log.log import set_logger
from MLC.mlc_table.MLCTable import MLCTable
from config import get_working_directory, set_working_directory

simulation = None


class MLCCmd(cmd.Cmd):
    def do_show_config_sections(self, line):
        """
            Show available sections in the configuration file.
        """
        print "Available sections:"
        for section in Config.get_instance().sections():
            print "\t%s" % section

    def do_show_config(self, line):
        """
            Show configuration values:
            show_config: show all sections.
            show_config section-name: show speciic section.
        """
        config = Config.get_instance()
        sections_to_show = config.sections()
        if line:
            if line in sections_to_show:
                sections_to_show = [line]
            else:
                print "Invalid section '%s'" % line
                self.do_show_config_sections("")
                return

        for section in sections_to_show:
            print "[%s]" % section
            for option in config.options(section):
                print "\t%s=%s" % (option, config.get(section, option))

    def do_go(self, line):
        """
            Execute MLC Simulation until N_GENERATIONS generations.
            run N_GENERATIONS (7 by default)
        """
        to_generation = int(line) if line else 7
        application = Application(simulation, "console")
        application.go(to_generation=to_generation, fig=False)

    def do_simulation_info(self, line):
        if Config.get_instance().getboolean("BEHAVIOUR", "save"):
            db_name = os.path.join(get_working_directory(),
                                   Config.get_instance().get("BEHAVIOUR", "savedir"))
            print "DB file:%s" % db_name
        else:
            print "DB file: no database file"

        print "Generations: %s" % simulation.number_of_generations()
        print "Individuals per generation: %s" % Config.get_instance().get("POPULATION", "size")
        print "Total individuals: %s" % MLCRepository.get_instance().number_of_individuals()

    def do_show_best(self, line):
        """
            Show best individual from generations.
            show_best: best individual of the last generation
            show_best N: best individual of generation N
        """
        if simulation.number_of_generations() == 0:
            print "Error, no generatios has been created"
            return False

        generation = int(line) if line else simulation.number_of_generations()
        population = simulation.get_generation(generation)

        best_individual_index = population.get_best_index()
        print "Best individual of generation %s: %s" % (generation, best_individual_index)
        best_individual = population.get_best_individual()
        print "Individual: %s" % best_individual

        application = Application(simulation)
        application.show_best(population)

    def do_show_individuals(self, line):
        """
            Show individuals properties.
            show_individuals: Show all individuals (MLCTable content)
            show_individuals N: Show individual N
        """
        individuals_to_show = range(1, MLCRepository.get_instance().number_of_individuals()+1)
        if line:
            if int(line) in individuals_to_show:
                individuals_to_show = [int(line)]
            else:
                print "Error, invalid individual id"
                return False

        for individual_id in individuals_to_show:
            individual = MLCRepository.get_instance().get_individual(individual_id)
            self.__print_individual_one_line(individual_id, individual)
        print "-- Total number of individuals: %s --" % MLCRepository.get_instance().number_of_individuals()

    def do_show_generations(self, line):
        """
            Show generations.
        """
        generations_to_show = range(1, simulation.number_of_generations()+1)
        if line:
            if int(line) in generations_to_show:
                generations_to_show = [int(line)]
            else:
                print "Error: invalid generation id"
                return False

        for generation_id in generations_to_show:
            print "Generation %s/%s, %s individuals" % (generation_id, simulation.number_of_generations(), Config.get_instance().get("POPULATION", "size"))
            for indiv_id in simulation.get_generation(generation_id).get_individuals():
                print "\t %s) value=%s" % (indiv_id, MLCRepository.get_instance().get_individual(indiv_id).get_value())

    def do_remove_generations(self, line):
        """
            Delete generations.
        """
        from_generation = int(line) if line else 1
        to_generation = simulation.number_of_generations()
        if self.__yes_or_no("Are you sure you want to remove generations %s to %s?" % (from_generation, to_generation)):
            print "Removing all generations from %s" % from_generation
            simulation.erase_generations(from_generation)

    def do_reload(self, line):
        """
            Reload generations and individuals from DB (for testing purposes only)
        """

        MLCTable._instance = None
        MLCRepository._instance = None
        simulation = Simulation()

    def __yes_or_no(self, question):
        reply = str(raw_input(question + ' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            return False

    def __print_individual_one_line(self, individual_id, individual):
        print "%s) value=%s, complexity=%s, appearences=%s" % (individual_id,
                                                               individual.get_value(),
                                                               individual.get_complexity(),
                                                               individual.get_appearences())

    def do_exit(self, line):
        return True

    def do_quit(self, line):
        return True

    def do_load_random_file(self, line):
        """
            Load file for random() unction (for testing purposes only).
            load_random_file random_file_path (e.g. ../tests/integration_tests/matlab_randoms.txt)
        """
        try:
            engine = MatlabEngine.engine()
            MatlabEngine.clear_random_values()
            MatlabEngine.load_random_values(line)
        except IOError, err:
            print "ERROR: %s" % err

    def do_rand(self, line):
        """
            Print a random number (for testing purposes only).
        """
        print MatlabEngine.rand()

def parse_arguments():
    parser = argparse.ArgumentParser(description='MLC Command Tool')

    parser.add_argument('-c', '--configuration-file', required=True,
                        type=str, help='MLC configuration file.')

    parser.add_argument('-d', '--working-dir',  type=str, default='.',
                        help='Working directory for the MLC (if persistence is enabled,'
                             'MLC will try to find the database file in the working directory).'
                             'Working dir must be passed as a relative path.')

    return parser.parse_args()

if __name__ == '__main__':
    arguments = parse_arguments()

    if not os.path.exists(arguments.configuration_file):
        print "Configuration file '%s' does not exist!!!" % arguments.configuration_file
        exit()

    if not os.path.exists(arguments.working_dir):
        print "'%s' is an invalid working directory!!!" % arguments.working_dir
        exit()

    set_working_directory(os.path.abspath(arguments.working_dir))

    set_logger('console')
    Config.get_instance().read(arguments.configuration_file)
    simulation = Simulation()
    MLCCmd().cmdloop()
