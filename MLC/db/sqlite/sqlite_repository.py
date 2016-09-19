from MLC.db.mlc_repository import MLCRepository
from MLC.db.mlc_repository import MemoryMLCRepository
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.individual.Individual import Individual

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
        if ev_time:
            self.__execute( '''UPDATE individuals SET cost = %s, evaluation_time = %s, WHERE indiv_id = %s''' %
                            (cost, ev_time, individual_id))
        else:
            self.__execute('''UPDATE individuals SET cost = %s WHERE indiv_id = %s''' %
                            (cost, individual_id))

    def add_individual(self, individual):
        individual_id, exist = self._memory_repo.add_individual(individual)

        if exist:
            self.__execute('''UPDATE individuals SET value = '%s', cost = %s, evaluation_time = %s, appearences = %s WHERE indiv_id = %s''' %
                            (individual.get_value(), individual.get_cost(), individual.get_evaluation_time(), individual.get_appearences(), individual_id))
        else:
            self.__execute('''INSERT INTO individuals VALUES (%s, '%s', %s, %s, %s)''' %
                            (individual_id, individual.get_value(), individual.get_cost(), individual.get_evaluation_time(), individual.get_appearences()))
        return individual_id, exist

    def __initialize_db(self):
        self.__execute('''CREATE TABLE individuals(indiv_id INTEGER PRIMARY KEY, value text, cost real, evaluation_time real, appearences INTEGER)''')
        self.commit_changes()

    def __get_db_connection(self):
        return sqlite3.connect(self._db_name)

    def __execute(self, statement):
        self.__to_execute.append(statement)

    def __load_individuals(self):
        conn = self.__get_db_connection()
        cursor = conn.execute("SELECT indiv_id, value, cost, evaluation_time, appearences from individuals ORDER BY indiv_id")
        for row in cursor:
            new_individual = Individual()
            new_individual.generate(str(row[1]))
            new_individual.set_cost(row[2])
            new_individual._evaluation_time = int(row[3])
            new_individual._appearences = int(row[4])
            self._memory_repo.add_individual(new_individual)
        conn.close()