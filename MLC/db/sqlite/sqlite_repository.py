from MLC.db.mlc_repository import MLCRepository, MemoryMLCRepository
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.individual.Individual import Individual
from sql_statements import *

import sqlite3
import os


class SQLiteRepository(MLCRepository):
    def __init__(self):
        self.__to_execute = []
        self._memory_repo = MemoryMLCRepository()
        self._db_name = Config.get_instance().get("BEHAVIOUR", "savedir")
        if not os.path.exists(self._db_name):
            self.__initialize_db()
        self.__load_individuals()

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

    def __initialize_db(self):
        self.__execute(stmt_create_table_individuals())
        self.commit_changes()

    def __get_db_connection(self):
        return sqlite3.connect(self._db_name)

    def __execute(self, statement):
        self.__to_execute.append(statement)

    def __load_individuals(self):
        conn = self.__get_db_connection()
        cursor = conn.execute(stmt_get_all_individuals())
        for row in cursor:
            new_individual = Individual()
            new_individual.generate(str(row[1]))
            new_individual.set_cost(row[2])
            new_individual._evaluation_time = int(row[3])
            new_individual._appearences = int(row[4])
            self._memory_repo.add_individual(new_individual)
        conn.close()