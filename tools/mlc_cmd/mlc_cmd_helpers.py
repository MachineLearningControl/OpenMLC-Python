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

import ConfigParser
from MLC.mlc_parameters.mlc_parameters import Config


def validate_params(param_types, err_handler, fail_message=""):
    def decorator(func):
        def real_decorator(*args, **kwargs):
            self, line = args
            input_values = line.split()

            if len(input_values) > len(param_types):
                print "Bad command arguments, %s" % fail_message
                return False

            input_values = input_values + [None]*(len(param_types) - len(input_values))
            validated_values = None

            try:
                type_values = zip(param_types, input_values)
                validated_values = [t(v) for t, v in type_values]
            except Exception, err:
                print "Bad command arguments, %s" % fail_message
                return False

            try:
                return func(self, *validated_values)
            except Exception, err:
                err_handler(err)

        return real_decorator
    return decorator


def string(value):
    if value is None:
        raise ValueError("null_value, expected string_value")
    return str(value)


def optional(value_type):
    def validate(value):
        if value is not None:
            return value_type(value)
    return validate


def load_configuration(configuration_file):
    config_parser = ConfigParser.ConfigParser()
    config_parser.read(configuration_file)
    return Config.to_dictionary(config_parser)
