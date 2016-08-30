import numpy as np
import MLC.Log.log as lg
import sys
import time
import serial

ser = None


def initialize_pyserial(config):
    # Init pyserial library
    port = config.get('ARDUINO', 'port')
    baudrate = config.get('ARDUINO', 'baudrate')
    timeout = config.getfloat('ARDUINO', 'read_timeout')
    local_ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)

    # FIXME: FIND ANOTHER WORKAROUND FOR THIS PROBLEM
    # Wait one or two second before sending commands to the serial Port
    time.sleep(1)
    return local_ser


def cost(eng, config, indiv):
    global ser
    if not ser:
        ser = initialize_pyserial(config)

    np.set_printoptions(precision=4, suppress=True)
    x = np.arange(-10, 10 + 0.1, 0.1)

    read_retries = config.getint('ARDUINO', 'read_retries')
    command = config.get('ARDUINO', 'command_opcode')
    period = config.get('ARDUINO', 'wait_period')
    for value in x:
        str_value = str(round(value, 1))
        if str_value == "-0.0":
            str_value = "0.0"

        retries = read_retries
        if command == '1':
            string = '1|' + period + '|' + str_value + '\n'
        elif command == '2':
            string = '1|' + str_value + '\n'
        else:
            lg.logger_.error('[POP][STAND_EVAL] Unknown command received.' +
                             'Aborting simulation.')
            sys.exit(-1)

        ser.write(string)
        response = ser.readline()

        while response.find('\n') < 0 and retries:
            retries -= 1
            lg.logger_.info('[POP][STAND_EVAL] Read failed. Retries ' +
                            'remaining: ' + str(retries))
            response = ser.readline()

        lg.logger_.debug('[POP][STAND_EVAL] Value expected: ' + str_value)
        lg.logger_.debug('[POP][STAND_EVAL] Value received: ' +
                         response.rstrip())

    y = np.tanh(x**3 - x**2 - 1)
    # artificial_noise = config.getint('EVALUATOR', 'artificialnoise')

    # In this test we have no noise by config file. But, if this were the
    # case, we would a have problem because the random of MATLAB is not
    # the random of Python :(
    # WORKAROUND: Generate the noise in matlab and process it in python

    # MAKE SOME NOISE!!!
    # noise = \
    #     eng.eval('rand(length(zeros(1, ' + str(len(x)) + ')))-0.5')
    # np_noise = np.array([s for s in noise[0]])
    # y2 = y + np_noise * 500 * artificial_noise
    y2 = y

    eng.workspace['indiv'] = indiv
    formal = eng.eval('indiv.formal').replace('S0', 'x')
    eng.workspace['x'] = eng.eval('-10:0.1:10')
    eng.workspace['formal'] = formal

    # Calculate J like the sum of the square difference of the
    # functions in every point

    lg.logger_.debug('[POP][TOY_PROBLEM] Individual Formal: ' + formal)
    eng.workspace['y3'] = \
        eng.eval('zeros(1, ' + str(len(x)) + ')')
    eng.eval('eval([formal])')
    y3 = eng.eval('eval([formal])')

    # If the expression doesn't have the term 'x',
    # the eval returns a value (float) instead  of an array.
    # In that case transform it to an array
    try:
        np_y3 = np.array([s for s in y3[0]])
    except TypeError:
        np_y3 = np.repeat(y3, len(x))

    return np.sum((np_y3 - y2)**2)
