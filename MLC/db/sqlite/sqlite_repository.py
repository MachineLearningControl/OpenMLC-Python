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

import sqlite3
import time

from MLC.db.mlc_repository import MLCRepository
from MLC.db.mlc_repository import MLCRepositoryHelper, IndividualData
from MLC.individual.Individual import Individual
from MLC.Log.log import get_gui_logger
from MLC.Simulation import Simulation
from MLC.db.sqlite.sql_statements import *
from MLC.db.sqlite.sql_statements_board_configuration import *
from MLC.arduino.protocol import ProtocolConfig
from MLC.arduino.connection.serialconnection import SerialConnectionConfig
from MLC.arduino.boards import types
import traceback

logger = get_gui_logger()


class SQLiteRepository(MLCRepository):
    IN_MEMORY_DB = ":memory:"

    def __init__(self, database, init_db=False):
        self._conn = sqlite3.connect(database)
        self._database = database

        if init_db:
            self.__initialize_db()

        self.__execute(stmt_enable_foreign_key())

        # cache for population
        gen_numbers = self._get_generations()
        self.__generations = len(gen_numbers)
        self.__base_gen = gen_numbers[0] if gen_numbers else 1

        # all individuals: {individual_id: (Individual, generated(bool))
        self.__individuals = self.__load_individuals()
        self._hashlist = {}

        # load hashes
        for indiv_id, individual in self.__individuals.items():
            hash = MLCRepositoryHelper.get_hash_for_individual(individual)
            self._hashlist[hash] = indiv_id

        # enhancement
        self.__next_individual_id = 1 if not self.__individuals else max(self.__individuals.keys()) + 1
        self.__individuals_to_flush = {}

    def close(self):
        self._conn.close()

    def __initialize_db(self):
        cursor = self._conn.cursor()

        # MLC Population tables
        cursor.execute(stmt_create_table_individuals())
        cursor.execute(stmt_create_table_population())

        # Board configuration tables
        cursor.execute(stmt_create_table_board())
        cursor.execute(stmt_create_table_serial_connection())
        cursor.execute(stmt_create_table_digital_pin())
        cursor.execute(stmt_create_table_analog_pin())
        cursor.execute(stmt_create_table_pwm_pin())

        cursor.close()
        self._conn.commit()

    def __get_db_connection(self, reopen_connection=False):
        # TODO: Workaround. SQLite throw an exception when a connection is used
        # in different threads. To solve it, we create a new connection
        # every time a new connection is delivered
        if self._database != SQLiteRepository.IN_MEMORY_DB:
            # Close the previous connection
            try:
                self._conn.close()
            except sqlite3.ProgrammingError:
                # FIXME: There are open connections that cannot be closed for
                # the Thread bug. See what can be done
                pass

            self._conn = sqlite3.connect(self._database)
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
            next_gen_id = self.__base_gen + self.__generations
            for i in range(len(population._individuals)):
                individual_id = population._individuals[i]
                individual_cost = population._costs[i]
                evaluation_time = population._ev_time[i]
                individual_gen_method = population._gen_method[i]
                individual_parents = ','.join(str(elem) for elem in population._parents[i])
                cursor.execute(stmt_insert_individual_in_population(next_gen_id,
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

    def get_population(self, generation):
        gen_id = self.__base_gen + generation - 1
        pop = self.__load_population(gen_id)
        return pop

    def count_population(self):
        return self.__generations

    # special methods
    def remove_population_from(self, from_generation):
        if from_generation > self.__generations:
            return

        gen_id = self.__base_gen + from_generation - 1
        self.__execute(stmt_delete_from_generations(gen_id))
        self.__generations = from_generation - 1
        if from_generation == 1:
            self.__base_gen = 1

    def remove_population_to(self, to_generation):
        if to_generation > self.__generations:
            to_generation = self.__generations

        gen_id = self.__base_gen + to_generation - 1
        self.__execute(stmt_delete_to_generations(gen_id))
        self.__generations = self.__generations - to_generation
        if self.__generations == 0:
            self.__base_gen = 1
        else:
            self.__base_gen = self.__base_gen + to_generation

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

    def get_individual_with_min_cost_in_last_pop(self):
        conn = self.__get_db_connection()
        cursor = conn.execute(stmt_get_individual_with_min_cost_in_last_pop())

        # We are expecting just one resultte
        min_indiv_id = cursor.fetchone()[0]
        cursor.close()
        return min_indiv_id

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
                data._add_data(row[0] - self.__base_gen + 1, row[1], row[2])

            cursor.close()
            conn.commit()

            return data

        except KeyError:
            raise KeyError("Individual N#%s does not exists" % individual_id)

    def get_individuals_data(self):
        indiv_data_dict = {}
        conn = self.__get_db_connection()
        cursor = conn.execute(stmt_get_individuals_data())

        for row in cursor:
            indiv_id = row[0]
            if indiv_id not in indiv_data_dict:
                data = IndividualData(self.__individuals[indiv_id].get_value())
                indiv_data_dict[indiv_id] = data

            indiv_data_dict[indiv_id]._add_data(row[1], row[2], row[3])

        cursor.close()
        conn.commit()
        return indiv_data_dict

    def count_individual(self):
        return len(self.__individuals)

    # special methods
    def update_individual_cost(self, individual_id, cost, evaluation_time, generation=-1):
        stmt_to_update_cost = None

        if generation == -1:
            stmt_to_update_cost = stmt_update_all_costs(individual_id, cost, evaluation_time)
        else:
            stmt_to_update_cost = stmt_update_cost(individual_id, cost,
                                                   evaluation_time,
                                                   generation + self.__base_gen - 1)

        logger.debug("[SQLITE_REPO] [UPDATE_INDIV_COST] - Query executed: {0}"
                     .format(stmt_to_update_cost))
        self.__execute(stmt_to_update_cost)

    def __execute(self, statement):
        # print ">>> %s" % statement
        conn = self.__get_db_connection()
        cursor = conn.cursor()
        cursor.execute(statement)
        cursor.close()
        conn.commit()
        return cursor.lastrowid

    def _get_generations(self):
        generations = []
        conn = self.__get_db_connection()
        cursor = conn.execute(stmt_get_generations())
        for row in cursor:
            generations.append(int(row[0]))
        cursor.close()
        conn.commit()
        return sorted(generations)

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
            new_individual = Individual(str(row[1]), SQLSaveFormal.from_sql(row[2]), row[3])
            individuals[row[0]] = new_individual

        cursor.close()
        conn.commit()
        return individuals

    # board configuration
    def save_board_configuration(self, board_config, board_id=None):

        conn = self.__get_db_connection()
        cursor = conn.cursor()

        try:
            # save/update board configuration
            if board_id is None:
                cursor.execute(stmt_insert_board(board_config.board_type["SHORT_NAME"],
                                                 0,  # serial connection hardcoded
                                                 board_config.read_count,
                                                 board_config.read_delay,
                                                 board_config.report_mode,
                                                 board_config.analog_resolution))
                board_id = cursor.lastrowid
            else:
                cursor.execute(stmt_update_board(board_id,
                                                 board_config.board_type["SHORT_NAME"],
                                                 0,
                                                 board_config.read_count,
                                                 board_config.read_delay,
                                                 board_config.report_mode,
                                                 board_config.analog_resolution))
                if cursor.rowcount < 1:
                    raise KeyError("Board %s does not exist" % board_id)

            # if board update is successful, update board pins
            # delete board pin configuration
            cursor.execute(stmt_delete_digital_pin(board_id))
            cursor.execute(stmt_delete_analog_pin(board_id))
            cursor.execute(stmt_delete_pwm_pin(board_id))

            # update digital pins
            self.__insert_pins(board_config.digital_input_pins, cursor, stmt_insert_digital_pin, board_id, 0)
            self.__insert_pins(board_config.digital_output_pins, cursor, stmt_insert_digital_pin, board_id, 1)

            # update analog pins
            self.__insert_pins(board_config.analog_input_pins, cursor, stmt_insert_analog_pin, board_id, 0)
            self.__insert_pins(board_config.analog_output_pins, cursor, stmt_insert_analog_pin, board_id, 1)

            # update pwm pins
            for pin_id in board_config.pwm_pins:
                cursor.execute(stmt_insert_pwm_pin(board_id, pin_id))

        except Exception:
            raise
        finally:
            cursor.close()
            conn.commit()

        return board_id

    def __insert_pins(self, pin_list, cursor, stmt_insert_pin, board_id, pin_type):
        for pin_id in pin_list:
            cursor.execute(stmt_insert_pin(board_id, pin_id, pin_type))

    def __get_pins(self, cursor, stmt_get_pins, board_id):
        input_pins = []
        output_pins = []

        for row in cursor.execute(stmt_get_pins(board_id)):
            pin_id, pin_type = row[0], row[1]
            if pin_type == 0:
                input_pins.append(pin_id)
            else:
                output_pins.append(pin_id)
        return input_pins, output_pins

    def get_board_configuration_ids(self):
        board_ids = []
        conn = self.__get_db_connection()
        cursor = conn.execute(stmt_get_board_configuration_ids())
        for row in cursor:
            board_ids.append(row[0])
        cursor.close()
        return board_ids

    def load_board_configuration(self, board_id):
        protocol = None
        conn = self.__get_db_connection()
        cursor = conn.execute(stmt_get_board(board_id))

        for row in cursor:
            board_type = filter(lambda x: x["SHORT_NAME"] == row[0], types)

            protocol = ProtocolConfig(connection=None,
                                      board_type=next(board_type),
                                      report_mode=row[1],
                                      read_count=row[2],
                                      read_delay=row[3],
                                      analog_resolution=row[4])
            break

        if protocol is None:
            raise KeyError("Board %s dows not exists" % board_id)

        # load pins
        input_pins, output_pins = self.__get_pins(cursor, stmt_get_analog_pins, board_id)
        protocol.analog_input_pins.extend(input_pins)
        protocol.analog_output_pins.extend(output_pins)

        input_pins, output_pins = self.__get_pins(cursor, stmt_get_digital_pins, board_id)
        protocol.digital_input_pins.extend(input_pins)
        protocol.digital_output_pins.extend(output_pins)

        for row in cursor.execute(stmt_get_pwm_pins(board_id)):
            protocol.pwm_pins.append(row[0])

        cursor.close()

        return protocol

    def save_serial_connection(self, serial_connection, board_id, connection_id=None):
        conn = self.__get_db_connection()
        cursor = conn.cursor()

        try:
            # save/update board configuration
            if connection_id is None:
                cursor.execute(stmt_insert_serial_connection(board_id,
                                                             serial_connection.port,
                                                             serial_connection.baudrate,
                                                             serial_connection.parity,
                                                             serial_connection.stopbits,
                                                             serial_connection.bytesize))
                connection_id = cursor.lastrowid
            else:
                cursor.execute(stmt_update_serial_connection(connection_id,
                                                             board_id,
                                                             serial_connection.port,
                                                             serial_connection.baudrate,
                                                             serial_connection.parity,
                                                             serial_connection.stopbits,
                                                             serial_connection.bytesize))
                if cursor.rowcount < 1:
                    raise KeyError("Connection %s does not exist" % board_id)
        except sqlite3.IntegrityError:
            raise KeyError("Board %s does not exist" % board_id)
        except Exception:
            raise
        finally:
            cursor.close()
            conn.commit()

        return connection_id

    def load_serial_connection(self, board_id):
        serial_connection = None

        conn = self.__get_db_connection()
        cursor = conn.execute(stmt_get_serial_connection(board_id))

        for row in cursor:
            serial_connection = SerialConnectionConfig(port=row[0],
                                                       baudrate=row[1],
                                                       parity=row[2],
                                                       stopbits=row[3],
                                                       bytesize=row[4])
            break

        if serial_connection is None:
            raise KeyError("Serial Connectio %s doess not exists" % board_id)

        return serial_connection
