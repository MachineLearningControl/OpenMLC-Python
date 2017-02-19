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

from MLC.GUI.Tables.ConfigTableModel import ConfigTableModel


class ConfigParserTableModel(ConfigTableModel):

    def __init__(self, name, config_parser, header, parent=None, *args):
        adapted_data = self._config_parser_to_list_of_lists(config_parser)
        ConfigTableModel.__init__(self, name, adapted_data, header, parent, *args)

    def _config_parser_to_list_of_lists(self, config_parser):
        data = []
        for each_section in config_parser.sections():
            for (each_key, each_val) in config_parser.items(each_section):
                data.append([each_key, each_section, each_val])
        return data
