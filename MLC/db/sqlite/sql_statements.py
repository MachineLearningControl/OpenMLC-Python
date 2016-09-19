def stmt_create_table_individuals():
    return '''
    CREATE TABLE individuals(indiv_id INTEGER PRIMARY KEY,
                             value text,
                             cost real,
                             evaluation_time real,
                             appearences INTEGER)'''


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