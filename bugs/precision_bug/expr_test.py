import sys
sys.path.append("../..")
import binascii
import numpy as np
import struct
import MLC.Log.log as lg

from MLC.Common.LispTreeExpr.LispTreeExpr import LispTreeExpr
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
expr6 = "(root (cos (exp (- -6.3726 (* -7.1746 S0)))))"
expr61 = "(root (exp (- -6.3726 (* -7.1746 S0))))"
expr612 = "(root (- -6.3726 (* -7.1746 S0)))"

tree = LispTreeExpr(expr6)
x = np.linspace(-10.0, 10.0, num=201)
mlc_y = tree.calculate_expression([x])

# Calculate the Mean squared error
y = np.tanh(x**3 - x**2 - 1)
evaluation = float(np.sum((mlc_y - y)**2))

# print mlc_y
with open("./costs_python.txt", "w") as f:
    for elem in mlc_y:
        f.write("%50.50f\n" % elem)

print evaluation
print np.sum(mlc_y)
