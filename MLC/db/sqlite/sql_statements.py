def stmt_create_table_individuals():
    return ''' CREATE TABLE individual(indiv_id INTEGER PRIMARY KEY,
                                       value text,
                                       formal text,
                                       complexity INTEGER)'''


def stmt_create_table_population():
    return '''
    CREATE TABLE population(id INTEGER PRIMARY KEY AUTOINCREMENT,
                            gen INTEGER,
                            cost real,
                            evaluation_time INTEGER,
                            gen_method INTEGER,
                            parents TEXT,
                            indiv_id INTEGER,
                            FOREIGN KEY(indiv_id) REFERENCES individual(indiv_id))'''


def stmt_delete_generation(generation):
    return """DELETE FROM population
              WHERE gen = %s""" % (generation,)

def stmt_delete_from_generations(from_generation):
    return """DELETE FROM population
              WHERE gen >= %s""" % (from_generation,)

def stmt_delete_unused_individuals():
    return '''DELETE FROM individual
              WHERE indiv_id NOT IN (SELECT DISTINCT indiv_id FROM population)'''


def stmt_get_unused_individuals():
    return '''SELECT indiv_id FROM individual
              WHERE indiv_id NOT IN (SELECT DISTINCT indiv_id FROM population)'''


def stmt_delete_unused_individuals():
    return '''DELETE FROM individual
              WHERE indiv_id NOT IN (SELECT DISTINCT indiv_id FROM population)'''

def stmt_get_generations():
    return '''SELECT distinct gen FROM population'''


def stmt_insert_individual_in_population(generation, indiv_id, cost, evaluation_time, gen_method, parents):
    return '''INSERT INTO population (gen, cost, evaluation_time, gen_method, parents, indiv_id)
              VALUES (%s, "%s", %s, %s, "%s", %s)''' % (generation,
                                                        cost,
                                                        evaluation_time,
                                                        gen_method,
                                                        parents,
                                                        indiv_id)


def stmt_get_individuals_from_population(generation):
    return '''SELECT indiv_id, cost, evaluation_time, gen_method, parents, ID
              FROM population
              WHERE gen = %s
              ORDER BY ID''' % generation


class SQLSaveFormal:
    @staticmethod
    def to_sql(indiv_formal):
        if isinstance(indiv_formal, str):
            return indiv_formal
        else:
            return '@'.join(indiv_formal)

    @staticmethod
    def from_sql(indiv_formal_column):
        return indiv_formal_column.split('@')

def stmt_insert_individual(individual_id, individual):
    return '''INSERT INTO individual VALUES (%s, "%s", "%s", %s)''' % (individual_id,
                                                                       individual.get_value(),
                                                                       SQLSaveFormal.to_sql(individual.get_formal()),
                                                                       individual.get_complexity())

def stmt_get_all_individuals():
    return '''SELECT indiv_id, value, formal, complexity
              from individual
              ORDER BY indiv_id'''


def stmt_get_individual_data(indiv_id):
    return '''SELECT gen, cost, evaluation_time
              FROM population
              WHERE indiv_id = %s''' % (indiv_id)


def stmt_update_all_costs(individual_id, cost, evaluation_time):
    return '''UPDATE population
              SET cost = %s, evaluation_time = %s
              WHERE indiv_id = %s''' % (cost, evaluation_time, individual_id)


def stmt_update_cost(individual_id, cost, evaluation_time, generation):
    return '''UPDATE population
              SET cost = %s, evaluation_time = %s
              WHERE indiv_id = %s AND gen = %s''' % (cost,
                                                     evaluation_time,
                                                     individual_id,
                                                     generation)
def stmt_enable_foreign_key():
    return '''PRAGMA foreign_keys = ON'''