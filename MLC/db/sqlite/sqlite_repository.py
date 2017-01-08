import sqlite3

from MLC.db.mlc_repository import MLCRepository
from MLC.db.mlc_repository import MLCRepositoryHelper, IndividualData
from MLC.individual.Individual import Individual
from MLC.Simulation import Simulation
from sql_statements import *


class SQLiteRepository(MLCRepository):
    IN_MEMORY_DB = ":memory:"

    def __init__(self, database, init_db=False):
        self._conn = sqlite3.connect(database)
        if init_db:
            self.__initialize_db()

        self.__execute(stmt_enable_foreign_key())

        # cache for population
        self.__generations = self._how_many_generations()

        # all individuals: {individual_id: (Individual, generated(bool))
        self.__individuals = self.__load_individuals()
        self._hashlist = {}

        # load hashes
        for indiv_id, individual in self.__individuals.items():
            hash = MLCRepositoryHelper.get_hash_for_individual(individual)
            self._hashlist[hash] = indiv_id

        # enhancement
        self.__next_individual_id = 1 if not self.__individuals else max(self.__individuals.keys())+1
        self.__individuals_to_flush = {}

    def __initialize_db(self):
        cursor = self._conn.cursor()
        cursor.execute(stmt_create_table_individuals())
        cursor.execute(stmt_create_table_population())
        cursor.close()
        self._conn.commit()

    def __get_db_connection(self):
        return self._conn

    def __insert_individuals_pending(self, individual):
        individual_id = self.__next_individual_id
        self.__individuals_to_flush[individual_id] = individual
        self.__next_individual_id += 1
        return individual_id

    def __flush_individuals(self):
        conn = self.__get_db_connection()
        cursor = conn.cursor()
        for individual_id in sorted(self.__individuals_to_flush.keys()):
            cursor.execute(stmt_insert_individual(individual_id, self.__individuals_to_flush[individual_id]))
        cursor.close()
        conn.commit()
        self.__individuals_to_flush = {}

    # operation over generations
    def add_population(self, population):
        self.__flush_individuals()

        conn = self.__get_db_connection()
        cursor = conn.cursor()

        try:
            for i in range(len(population._individuals)):
                individual_id = population._individuals[i]
                individual_cost = population._costs[i]
                evaluation_time = population._ev_time[i]
                individual_gen_method = population._gen_method[i]
                individual_parents = ','.join(str(elem) for elem in population._parents[i])
                cursor.execute(stmt_insert_individual_in_population(self.__generations+1,
                                                                    individual_id,
                                                                    individual_cost,
                                                                    evaluation_time,
                                                                    individual_gen_method,
                                                                    individual_parents))
        except sqlite3.IntegrityError:
            raise KeyError("Trying to insert an invalid Individual")

        cursor.close()
        conn.commit()

        self.__generations += 1

    def remove_population(self, generation):
        self.__execute(stmt_delete_generation(generation))
        self.__generations -= 1

    def get_population(self, generation):
        pop = self.__load_population(generation)
        return pop

    def count_population(self):
        return self.__generations

    # special methods
    def remove_population_from(self, from_generation):
        self.__execute(stmt_delete_from_generations(from_generation))
        self.__generations = from_generation-1

    def remove_last_population(self):
        if self.__generations > 0:
            self.remove_population_from(self.__generations)

    def remove_unused_individuals(self):
        to_delete = []

        # get individuals to delete
        conn = self.__get_db_connection()
        cursor = conn.execute(stmt_get_unused_individuals())
        for row in cursor:
            to_delete.append(row[0])
        cursor.close()

        # delete individuals from the DB
        self.__execute(stmt_delete_unused_individuals())

        # delete them from the cache
        for indiv_id in to_delete:
            individual_to_delete = self.__individuals[indiv_id]
            del self.__individuals[indiv_id]
            del self._hashlist[MLCRepositoryHelper.get_hash_for_individual(individual_to_delete)]

        return len(to_delete)

    # operations over individuals
    def add_individual(self, individual):
        hash = MLCRepositoryHelper.get_hash_for_individual(individual)

        if hash in self._hashlist:
            return self._hashlist[hash], True

        individual_id = self.__insert_individuals_pending(individual)

        self.__individuals[individual_id] = individual
        self._hashlist[hash] = individual_id

        return individual_id, False

    def update_individual(self, individual_id, individual):
        raise NotImplementedError("This method must be implemented")

    def remove_individual(self, individual_id):
        raise NotImplementedError("This method must be implemented")

    def get_individual(self, individual_id):
        try:
            return self.__individuals[individual_id]
        except KeyError:
            raise KeyError("Individual N#%s does not exists" % individual_id)

    def get_individual_data(self, individual_id):
        try:
            data = IndividualData(self.__individuals[individual_id].get_value())

            conn = self.__get_db_connection()
            cursor = conn.execute(stmt_get_individual_data(individual_id))
            for row in cursor:
                data._add_data(row[0], row[1], row[2])
            cursor.close()
            conn.commit()

            return data

        except KeyError:
            raise KeyError("Individual N#%s does not exists" % individual_id)

    def count_individual(self):
        return len(self.__individuals)

    # special methods
    def update_individual_cost(self, individual_id, cost, evaluation_time, generation=-1):
        stmt_to_update_cost = None

        if generation == -1:
            stmt_to_update_cost = stmt_update_all_costs(individual_id, cost, evaluation_time)
        else:
            stmt_to_update_cost = stmt_update_cost(individual_id, cost, evaluation_time, generation)

        self.__execute(stmt_to_update_cost)

    def __execute(self, statement):
        conn = self.__get_db_connection()
        cursor = conn.cursor()
        cursor.execute(statement)
        cursor.close()
        conn.commit()
        return cursor.lastrowid

    def _how_many_generations(self):
        generations = []
        conn = self.__get_db_connection()
        cursor = conn.execute(stmt_get_generations())
        for row in cursor:
            generations.append(int(row[0]))
        cursor.close()
        conn.commit()
        return len(sorted(generations))

    def __load_population(self, generation):
        i = 0
        population = Simulation.create_empty_population_for(generation)
        conn = self.__get_db_connection()
        cursor = conn.execute(stmt_get_individuals_from_population(generation))
        for row in cursor:
            population._individuals[i] = row[0]
            population._costs[i] = row[1]
            population._ev_time[i] = row[2]
            population._gen_method[i] = row[3]

            if not row[4] == '':
                population._parents[i] = [int(elem) for elem in row[4].split(',')]
            else:
                population._parents[i] = []

            i += 1
        cursor.close()
        conn.commit()
        return population

    def __load_individuals(self):
        individuals = {}
        conn = self.__get_db_connection()
        cursor = conn.execute(stmt_get_all_individuals())

        for row in cursor:
            new_individual = Individual(str(row[1]))
            new_individual.generate(str(row[1]))
            # new_individual = Individual(value=str(row[1]))
            individuals[row[0]] = new_individual

        cursor.close()
        conn.commit()
        return individuals
