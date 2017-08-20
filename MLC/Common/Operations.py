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

    def get_operation_from_op_num(self, op_num_index):
        try:
            return list(self._ops.values())[int(op_num_index) - 1]
        except KeyError:
            raise IndexError("get_operation_from_op_num",
                             "Index must be one of the following values: {0}"
                             .format(str(self._ops.keys())))

    def get_operation_from_op_string(self, str_op):
        for k, op in self._ops.items():
            if op["op"] == str_op:
                return op
        raise KeyError('Operations', 'Key %s was not found' % str_op)

    def length(self):
        """ Number of operations loaded into the Singleton
        """
        return len(self._ops)

    @staticmethod
    def get_instance(reload_operations=False):
        if reload_operations or Operations._instance is None:
            Operations._instance = Operations()

        return Operations._instance
