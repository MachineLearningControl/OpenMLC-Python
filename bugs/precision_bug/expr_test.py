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
raw_input("Press Enter to continue...")

import sys
sys.path.append("../..")
import binascii
import numpy as np
import struct
import MLC.Log.log as lg
raw_input("Press Enter to continue...")

from MLC.Common.LispTreeExpr.LispTreeExpr import LispTreeExpr
raw_input("Press Enter to continue...")
from MLC.Log.log import set_logger
from MLC.mlc_parameters.mlc_parameters import Config


def initialize_config():
    config = Config.get_instance()
    config.read('../../conf/configuration.ini')
    return config

# Set printable resolution (don't alter numpy interval resolution)
np.set_printoptions(precision=9)
# Show full arrays, no matter what size do they have
np.set_printoptions(threshold=np.inf)
# Don't show scientific notation
np.set_printoptions(suppress=True)

initialize_config()
set_logger('console')

# Full expression
expr6 = "(root (- (+ (cos (/ (cos (/ 132.7707 (cos (/ (/ (log (log S2)) (/ (/ (/ 7.1798 (/ (log S6) (log S2))) (/ (log (tanh S4)) (/ 1103.5980 S3))) (log (log S2)))) (log S5))))) (log (/ (cos (/ (/ (log (log S2)) -0.6449) (/ 1103.5980 S3))) (* -1.0000 (tanh (cos (/ (/ (sin (log S0)) (/ (* S1 S3) (log (log S2)))) (/ 1103.5980 S3))))))))) 648.1562) (- 0.0100 (+ S4 (/ 6.7623 (/ (cos (* -1.0000 (tanh (cos (/ (/ (sin (log S0)) (/ (* S1 S3) (log S6))) (/ (/ (exp (/ 1744.7186 S0)) (/ S1 207.4462)) (/ (* S1 S3) (exp S5)))))))) (log (/ (/ (+ (/ S3 (/ (/ 7.1798 (sin (log S0))) (/ (* S1 S3) (/ 1103.5980 S3)))) 0.0000) (/ (/ (exp S5) (/ (sin (log S0)) (/ (* S1 S3) (log S6)))) (/ (* S1 S3) (/ (/ (exp (/ 1744.7186 S0)) (/ S1 207.4462)) (/ (* S1 S3) (exp S5)))))) (/ (/ 1103.5980 S3) (/ (/ -329.1023 (/ (log (sin (log S0))) (sin (log S0)))) (/ (log (sin (log S0))) -4.6052)))))))))))"
expr61 = "(root (exp (- -6.3726 (* -7.1746 S0))))"
expr612 = "(root (- -6.3726 (* -7.1746 S0)))"

raw_input("Press Enter to continue...")
tree = LispTreeExpr(expr6)
raw_input("Press Enter to continue...")

x = np.linspace(-10.0, 10.0, num=201)
mlc_y = tree.calculate_expression([x,x,x,x,x,x,x])
raw_input("Press Enter to continue...")

# Calculate the Mean squared error
y = np.tanh(x**3 - x**2 - 1)
evaluation = float(np.sum((mlc_y - y)**2))
raw_input("Press Enter to continue...")

# print mlc_y
with open("./costs_python.txt", "w") as f:
    for elem in mlc_y:
        f.write("%50.50f\n" % elem)

print evaluation
print np.sum(mlc_y)
