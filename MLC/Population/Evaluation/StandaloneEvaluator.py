import sys

import MLC.Log.log as lg
import numpy as np
import serial
import time

class StandaloneEvaluator(object):
    def __init__(self, eng, config):
        self._eng = eng
        self._config = config

        # Map of functions to execute
        self._callbacks = {}
        self._callbacks['toy_problem'] = self._toy_problem
        self._callbacks['arduino'] = self._arduino

        self._ser = None

    def evaluate(self, eval_idx, indivs, pop_number):
        # TODO: Don't use this value as a callback for the moment. Hardcode
        # the call to the evaluation function
        eval_function = self._config.get('EVALUATOR', 'evaluation_function')
        if eval_function == 'arduino':
            # Init pyserial library
            port = self._config.get('ARDUINO', 'port')
            baudrate = self._config.get('ARDUINO', 'baudrate')
            timeout = self._config.getfloat('ARDUINO', 'read_timeout')
            self._ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)

            # FIXME: FIND ANOTHER WORKAROUND FOR THIS PROBLEM
            # Wait one or two second before sending commands to the serial Port
            time.sleep(1)

        JJ = []

        for i in xrange(len(eval_idx)):
            index = eval_idx[i]
            lg.logger_.info('[POP][STAND_EVAL] Individual N#' + str(index) +
                            ' from generation ' + str(pop_number))

            indiv = self._eng.eval('wtable.individuals(' +
                                   str(indivs[index-1]) + ')')
            value = \
                self._eng.eval('wtable.individuals(' + str(indivs[index-1]) +
                               ').value')
            lg.logger_.debug('[POP][STAND_EVAL] Individual N#' + str(index) +
                             ' Value: ' + value)

            try:
                callback = self._callbacks[eval_function]
                JJ.append(callback(indiv))
            except KeyError:
                lg.logger_.error("[POP][STAND_EVAL] Evaluation Function " +
                                 "doesn't exists. Aborting progam.")
                sys.exit(-1)

        return JJ

    def _arduino(self, indiv):
        read_retries = self._config.getint('ARDUINO', 'read_retries')
        x = np.arange(-10, 10 + 0.1, 0.1)
        np.set_printoptions(precision=4, suppress=True)
        command = self._config.get('ARDUINO', 'command_opcode')
        period = self._config.get('ARDUINO', 'wait_period')
        for value in x:
            retries = read_retries
            if command == '1':
                string = '1|' + period + '|' + str(value) + '\n'
            elif command == '2':
                string = '1|' + str(value) + '\n'
            else:
                lg.logger_.error('[POP][STAND_EVAL] Unknown command received.' +
                                 'Aborting simulation.')
                sys.exit(-1)

            self._ser.write(string)
            response = self._ser.readline()

            while response.find('\n') < 0 and retries:
                retries -= 1
                lg.logger_.info('[POP][STAND_EVAL] Read failed. Retries ' +
                                 'remaining: ' + str(retries))
                response = self._ser.readline()

            lg.logger_.debug('[POP][STAND_EVAL] Value expected: ' + str(value))
            lg.logger_.debug('[POP][STAND_EVAL] Value received: ' +
                             response.rstrip())

        y = np.tanh(x**3 - x**2 - 1)
        artificial_noise = self._config.getint('EVALUATOR', 'artificialnoise')

        # In this test we have no noise by config file. But, if this were the
        # case, we would a have problem because the random of MATLAB is not
        # the random of Python :(
        # WORKAROUND: Generate the noise in matlab and process it in python

        # MAKE SOME NOISE!!!
        noise = \
            self._eng.eval('rand(length(zeros(1, ' + str(len(x)) + ')))-0.5')
        np_noise = np.array([s for s in noise[0]])
        y2 = y + np_noise * 500 * artificial_noise

        self._eng.workspace['indiv'] = indiv
        formal = self._eng.eval('indiv.formal').replace('S0', 'x')
        self._eng.workspace['x'] = self._eng.eval('-10:0.1:10')
        self._eng.workspace['formal'] = formal

        # Calculate J like the sum of the square difference of the
        # functions in every point

        lg.logger_.debug('[POP][TOY_PROBLEM] Individual Formal: ' + formal)
        self._eng.workspace['y3'] = \
            self._eng.eval('zeros(1, ' + str(len(x)) + ')')
        self._eng.eval('eval([formal])')
        y3 = self._eng.eval('eval([formal])')

        # If the expression doesn't have the term 'x',
        # the eval returns a value (float) instead  of an array.
        # In that case transform it to an array
        try:
            np_y3 = np.array([s for s in y3[0]])
        except TypeError:
            np_y3 = np.repeat(y3, len(x))

        return np.sum((np_y3 - y2)**2)

    def _toy_problem(self, indiv):
        x = np.arange(-10, 10 + 0.1, 0.1)
        y = np.tanh(x**3 - x**2 - 1)
        artificial_noise = self._config.getint('EVALUATOR', 'artificialnoise')

        # In this test we have no noise by config file. But, if this were the
        # case, we would a have problem because the random of MATLAB is not
        # the random of Python :(
        # WORKAROUND: Generate the noise in matlab and process it in python

        # MAKE SOME NOISE!!!
        noise = \
            self._eng.eval('rand(length(zeros(1, ' + str(len(x)) + ')))-0.5')
        np_noise = np.array([s for s in noise[0]])
        y2 = y + np_noise * 500 * artificial_noise

        self._eng.workspace['indiv'] = indiv
        formal = self._eng.eval('indiv.formal').replace('S0', 'x')
        self._eng.workspace['x'] = self._eng.eval('-10:0.1:10')
        self._eng.workspace['formal'] = formal

        # Calculate J like the sum of the square difference of the
        # functions in every point

        lg.logger_.debug('[POP][TOY_PROBLEM] Individual Formal: ' + formal)
        self._eng.workspace['y3'] = \
            self._eng.eval('zeros(1, ' + str(len(x)) + ')')
        self._eng.eval('eval([formal])')
        y3 = self._eng.eval('eval([formal])')

        # If the expression doesn't have the term 'x',
        # the eval returns a value (float) instead  of an array.
        # In that case transform it to an array
        try:
            np_y3 = np.array([s for s in y3[0]])
        except TypeError:
            np_y3 = np.repeat(y3, len(x))

        return np.sum((np_y3 - y2)**2)
