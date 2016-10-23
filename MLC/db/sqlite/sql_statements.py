def stmt_create_table_individuals():
    return '''
    CREATE TABLE individuals(indiv_id INTEGER PRIMARY KEY,
                             value text,
                             cost real,
                             evaluation_time real,
                             appearences INTEGER)'''


def stmt_delete_from_generations(from_generation):
    return """DELETE FROM population
              WHERE gen >= %s""" % (from_generation,)


def stmt_delete_unused_individuals():
    return '''DELETE FROM individuals
              WHERE indiv_id NOT IN (SELECT DISTINCT indiv_id FROM population)'''


def stmt_get_unused_individuals():
    return '''SELECT indiv_id FROM individuals
              WHERE indiv_id NOT IN (SELECT DISTINCT indiv_id FROM population)'''


def stmt_create_table_population():
    return '''
    CREATE TABLE population( ID INTEGER PRIMARY KEY AUTOINCREMENT,
                             gen INTEGER,
                             cost real,
                             gen_method INTEGER,
                             parents TEXT,
                             indiv_id INTEGER,
                             FOREIGN KEY(indiv_id) REFERENCES individuals(indiv_id))'''


def stmt_get_generations():
    return '''select distinct gen from population'''


def stmt_insert_individual_in_population(generation, indiv_id, cost, gen_method, parents):
    return '''INSERT INTO population (gen, cost, gen_method, parents, indiv_id)
              VALUES (%s, '%s', %s, '%s', %s)''' % (generation,
                                                    cost,
                                                    gen_method,
                                                    parents,
                                                    indiv_id)


def stmt_get_individuals_from_population(generation):
    return '''SELECT indiv_id, cost, gen_method, parents, ID
              FROM population
              WHERE gen = %s
              ORDER BY ID''' % generation


def stmt_insert_individual(individual_id, individual):
    return '''INSERT INTO individuals VALUES (%s, '%s', %s, %s, %s)''' % (individual_id,
                                                                          individual.get_value(),
                                                                          individual.get_cost(),
                                                                          individual.get_evaluation_time(),
                                                                          individual.get_appearences())


def stmt_update_individual_cost(individual_id, cost, ev_time=None):
    if ev_time:
        return '''UPDATE individuals SET cost = %s, evaluation_time = %s,
                                     WHERE indiv_id = %s''' % (cost, ev_time,
                                                               individual_id)
    else:
        return '''UPDATE individuals SET cost = %s WHERE indiv_id = %s''' % (cost,
                                                                             individual_id)


def stmt_update_individual(individual_id, individual):
    return '''UPDATE individuals SET value = '%s', cost = %s, evaluation_time = %s, appearences = %s
                                 WHERE indiv_id = %s''' % (individual.get_value(),
                                                           individual.get_cost(),
                                                           individual.get_evaluation_time(),
                                                           individual.get_appearences(),
                                                           individual_id)


def stmt_get_all_individuals():
    return '''SELECT indiv_id, value, cost, evaluation_time, appearences
              from individuals
              ORDER BY indiv_id'''
