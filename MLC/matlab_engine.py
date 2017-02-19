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

import matlab.engine
import config as mlcv3_config
import os
import MLC.Log.log as lg
import random


class MatlabEngine:
    """
    Singleton class that allow to call matlab code from python using the
    matlab engine.
    """
    _engine_instance = None
    _rand_counter = 0
    _randoms = []

    @staticmethod
    def engine():
        if MatlabEngine._engine_instance is None:
            lg.logger_.info("[MATLAB_ENGINE] Loading MATLAB environment. Please wait...")
            matlab_code_dir = mlcv3_config.get_matlab_path()

            # Check if a MATLAB session exists.
            try:
                sessions = matlab.engine.find_matlab()
                if len(sessions) > 0:
                    MatlabEngine._engine_instance = matlab.engine.connect_matlab(sessions[0])
                else:
                    MatlabEngine._engine_instance = matlab.engine.start_matlab()
            except AttributeError:
                # This version of MATLAB is not compatible with Shared sessions
                # Init the MATLAB engine in the regular way
                MatlabEngine._engine_instance = matlab.engine.start_matlab()

            MatlabEngine._engine_instance.addpath(matlab_code_dir)
            MatlabEngine._engine_instance.addpath(os.path.join(matlab_code_dir, "MLC_tools"))
            MatlabEngine._engine_instance.addpath(os.path.join(matlab_code_dir, "MLC_tools/Demo"))
            lg.logger_.info("[MATLAB_ENGINE] MATLAB environment loaded succesfully.")

        return MatlabEngine._engine_instance
