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
import importlib
import os.path

from MLC.config import get_mlc_root_directory


def set_population_size(old_size, new_size, simulation):
    if simulation.number_of_generations() > 0:
        raise Exception("Cannot modify the size of a non empty simulation")
    return True


class ParamTypes:
    @staticmethod
    def string(value):
        v = str(value)

    @staticmethod
    def int(value):
        v = int(value)

    @staticmethod
    def unsigned_int(value):
        v = int(value)
        if v < 0:
            raise ValueError()

    @staticmethod
    def set_type(set_values):
        def check_set(value):
            if value not in set_values:
                raise ValueError("Value must be in %s" % set_values)
        return check_set


class ConfigRule:
    def __init__(self, description, param_type, set_function):
        self._description = description
        self._param_type = param_type
        self._set_function = set_function

    def apply(self, value, simulation):
        if self._param_type:
            self._param_type(value)

        if self._set_function:
            self._set_function("", value, simulation)


class MLCConfigRules:
    _instance = None

    @staticmethod
    def get_instance():
        if MLCConfigRules._instance is None:
            this_file = os.path.abspath(__file__)
            mlc_rules_path = os.path.join(os.path.dirname(this_file), "mlc_rules.yaml")
            MLCConfigRules._instance = MLCConfigRules(mlc_rules_path)
        return MLCConfigRules._instance

    def __init__(self, rules_file):
        rules_file = yaml.load(open(rules_file, 'r'))
        self._rules = {}

        for section, params in rules_file.iteritems():
            self._rules[section] = {}
            for param_name, param_rule in params.iteritems():
                self._rules[section][param_name] = self.__build_config_rule(param_rule)

    def apply(self, section, name, value, simulation):
        if section not in self._rules:
            return True

        if name not in self._rules[section]:
            return True

        self._rules[section][name].apply(value, simulation)

    def __build_config_rule(self, param_rule):
        set_function = param_rule.get("set_function", None)
        if set_function:
            set_function_module = ".".join(set_function.split('.')[:-1])
            set_function_method = ".".join(set_function.split('.')[-1:])

            function_module = importlib.import_module(set_function_module)
            function_method = getattr(function_module, set_function_method)
            set_function = function_method

        param_type = param_rule.get("type", None)
        if param_type:
            if isinstance(param_type, list):
                param_type = ParamTypes.set_type(param_type)

            if param_type == "unsigned_int":
                param_type = ParamTypes.unsigned_int

        return ConfigRule(param_rule["description"], param_type, set_function)

if __name__ == "__main__":
    rules = MLCConfigRules('mlc_rules.yaml')
    print rules.apply("POPULATION", "size", 45, None)