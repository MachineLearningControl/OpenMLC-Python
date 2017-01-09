import MLC.Log.log as lg
import sqlite3
import os
import time

from MLC.config import get_working_directory
from MLC.db.mlc_repository import MLCRepository, MemoryMLCRepository
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.individual.Individual import Individual
from MLC.Population.Population import Population
from MLC.Simulation import Simulation
from sql_statements import *




class SQLiteRepository(MLCRepository):
    def __init__(self):
        self.__to_execute = []
        self._memory_repo = MemoryMLCRepository()
        self._db_name = Config.get_instance().get("BEHAVIOUR", "savedir")
        self._db_file = os.path.join(get_working_directory(), self._db_name)
        # lg.logger_.info("[SQLITE_REPO] Using DB: {0}".format(self._db_file))

        if not os.path.exists(self._db_file):
            self.__initialize_db()

        self.__load_individuals()

    def add_population(self, population):
        generation = population._gen
        conn = self.__get_db_connection()
        c = conn.cursor()
        for i in range(len(population._individuals)):
            individual_id = population._individuals[i]
            individual_cost = population._costs[i]
            individual_gen_method = population._gen_method[i]
            individual_parents = ','.join(str(elem) for elem in population._parents[i])
            c.execute(stmt_insert_individual_in_population(generation,
                                                           individual_id,
                                                           individual_cost,
                                                           individual_gen_method,
                                                           individual_parents))
        c.close()
        conn.commit()

    def get_populations(self):
        populations = []
        for gen in self._how_many_generations():
            populations.append(self.__load_population(gen))
        return populations

    def erase_generations(self, from_generation, remove_unused_individuals=True):
        self.__execute(stmt_delete_from_generations(from_generation))
        self.commit_changes()

        if remove_unused_individuals:
            conn = self.__get_db_connection()
            cursor = conn.execute(stmt_get_unused_individuals())
            unused_individuals = [row[0] for row in cursor]
            conn.close()
            self._memory_repo.remove_individuals(unused_individuals)
            self.__execute(stmt_delete_unused_individuals())

        self.commit_changes()

    def commit_changes(self):
        conn = self.__get_db_connection()
        c = conn.cursor()
        for stmt in self.__to_execute:
            c.execute(stmt)
        c.close()
        conn.commit()
        self.__to_execute = []

    def get_individual(self, individual_id):
        return self._memory_repo.get_individual(individual_id)

    def update_individual(self, individual_id, cost, ev_time=None):
        self._memory_repo.update_individual(individual_id, cost, ev_time)
        self.__execute(stmt_update_individual_cost(individual_id, cost, ev_time))

    def add_individual(self, individual):
        individual_id, exist = self._memory_repo.add_individual(individual)

        if exist:
            self.__execute(stmt_update_individual(individual_id, individual))
        else:
            self.__execute(stmt_insert_individual(individual_id, individual))

        return individual_id, exist

    def number_of_individuals(self):
        return self._memory_repo.number_of_individuals()

    def __initialize_db(self):
        self.__execute(stmt_create_table_individuals())
        self.__execute(stmt_create_table_population())
        self.commit_changes()

    def _how_many_generations(self):
        generations = []
        conn = self.__get_db_connection()
        cursor = conn.execute(stmt_get_generations())
        for row in cursor:
            generations.append(int(row[0]))
        conn.close()
        return sorted(generations)

    def __get_db_connection(self):
        return sqlite3.connect(self._db_file)

    def __execute(self, statement):
        self.__to_execute.append(statement)

    def __load_population(self, generation):
        i = 0
        population = Simulation.create_empty_population_for(generation)
        conn = self.__get_db_connection()
        cursor = conn.execute(stmt_get_individuals_from_population(generation))
        for row in cursor:
            population._individuals[i] = row[0]
            population._costs[i] = row[1]
            population._gen_method[i] = row[2]

            if not row[3] == '':
                population._parents[i] = [int(elem) for elem in row[3].split(',')]
            else:
                population._parents[i] = []

            i += 1
        conn.close()
        return population

    def __load_individuals(self):
        conn = self.__get_db_connection()
        cursor = conn.execute(stmt_get_all_individuals())

        for row in cursor:
            new_individual = Individual()
            new_individual.generate(str(row[1]))
            # new_individual = Individual(value=str(row[1]))
            new_individual.set_cost(row[2])
            new_individual._evaluation_time = int(row[3])
            new_individual._appearences = int(row[4])
            self._memory_repo.add_individual(new_individual)
        conn.close()