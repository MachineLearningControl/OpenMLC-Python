import yaml
from MLC.mlc_parameters.mlc_parameters import Config
from MLC import config as mlc_paths

import os
class Operations(object):
    """
    Singleton class gives information about the tree functions availables at
    MLC
    """

    _instance = None

    def __init__(self):
        self._config = Config.get_instance()
        operations_config_file = os.path.join(mlc_paths.get_config_path(), 'operations.yaml')
        available_operations = yaml.load(open(operations_config_file))

        opsetrange = self._config.get_list('POPULATION', 'opsetrange')
        self._ops = {}
        for operation_id in opsetrange:
            self._ops[operation_id] = available_operations[operation_id]


    def get_operation_from_op_num(self, op_num):
        try:
            return self._ops[op_num]
        except KeyError:
            raise IndexError("get_operation", "Index must be one of the following values: " + str(self._ops.keys()))

    def get_operation_from_op_string(self, str_op):
        for k, op in self._ops.iteritems():
            if op["op"] == str_op:
                return op
        raise KeyError('Operations', 'Key %s was not found' % str_op)

    def length(self):
        """ Number of operations loaded into the Singleton
        """
        return len(self._ops)

    @staticmethod
    def get_instance():
        if Operations._instance is None:
            Operations._instance = Operations()

        return Operations._instance
