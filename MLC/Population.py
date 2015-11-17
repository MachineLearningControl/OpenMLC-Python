import logging
from Creation.CreationFactory import CreationFactory


class Population(object):
    def __init__(self, eng, config, gen=None):
        self._eng = eng
        self._config = config

        if gen:
            self._gen = gen

        cascade = config.get('OPTIMIZATION', 'cascade', type='array')
        size = config.get('POPULATION', 'size', type='array')

        self._gen = 1 if cascade[1] == 0 else cascade[1]
        self._gensize = cascade[1] \
            if (self._gen > 1 and len(size) > 1) else size[0]
        self._state = 'init'

        logging.getLogger("default").debug("Population created. Number: " +
                                           str(self._gen) + " - Size:" +
                                           str(self._gensize))

    def create(self):
        ev_method = self._config.get('EVALUATOR', 'evaluation_method')
        logging.info("Using " + ev_method + " to generate population")
        gen_creator = CreationFactory.make(ev_method)
        gen_creator.create(self._eng, self._config)







