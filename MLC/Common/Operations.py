import numpy as np
import MLC.Log.log as lg
from MLC.mlc_parameters.mlc_parameters import Config


class Operations(object):
    """
    Singleton class gives information about the tree functions availables at
    MLC
    """

    _instance = None

    def __init__(self):
        self._config = Config.get_instance()
        self._ops = {}
        self._load_operations()

        self._range = self._config.get_param('POPULATION', 'opsetrange', type='range')

    def _load_operations(self):
        # FIXME: Hardcoded, ugly. Change it for a config file
        op = {}
        op["op"] = "+"
        op["nbarg"] = 2
        op["complexity"] = 1
        self._ops[1] = op

        op = {}
        op["op"] = "-"
        op["nbarg"] = 2
        op["complexity"] = 1
        self._ops[2] = op

        op = {}
        op["op"] = "*"
        op["nbarg"] = 2
        op["complexity"] = 1
        self._ops[3] = op

        op = {}
        op["op"] = "/"
        op["nbarg"] = 2
        op["complexity"] = 1
        self._ops[4] = op

        op = {}
        op["op"] = "sin"
        op["nbarg"] = 1
        op["complexity"] = 3
        self._ops[5] = op

        op = {}
        op["op"] = "cos"
        op["nbarg"] = 1
        op["complexity"] = 3
        self._ops[6] = op

        op = {}
        op["op"] = "log"
        op["nbarg"] = 1
        op["complexity"] = 5
        self._ops[7] = op

        op = {}
        op["op"] = "exp"
        op["nbarg"] = 1
        op["complexity"] = 5
        self._ops[8] = op

        op = {}
        op["op"] = "tanh"
        op["nbarg"] = 1
        op["complexity"] = 5
        self._ops[9] = op

        op = {}
        op["op"] = "mod"
        op["nbarg"] = 2
        op["complexity"] = 5
        self._ops[10] = op

        op = {}
        op["op"] = "pow"
        op["nbarg"] = 2
        op["complexity"] = 10
        self._ops[11] = op

    def get_operation_from_op_num(self, op_num):
        if not op_num in self._range:
            str_error = "Index of an operation must be one of the following values: " + str(self._range)
            raise IndexError("get_operation", str_error)

        return self._ops[op_num]

    def get_operation_from_op_string(self, str_op):
        for k, op in self._ops.iteritems():
            if op["op"] == str_op:
                return op

        raise KeyError('Operations', 'Key was not found')

    def length(self):
        """ Number of operations loaded into the Singleton
        """
        return len(self._range)

    @staticmethod
    def get_instance():
        if Operations._instance is None:
            Operations._instance = Operations()

        return Operations._instance
