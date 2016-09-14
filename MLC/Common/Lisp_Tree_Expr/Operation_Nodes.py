import math
import importlib

import MLC.Log.log as lg
import numpy as np
import sys

from MLC.Common.Lisp_Tree_Expr.Tree_Nodes import Tree_Node
from MLC.Common.Lisp_Tree_Expr.Tree_Nodes import Leaf_Node
from MLC.Common.Lisp_Tree_Expr.Tree_Nodes import Internal_Node
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Common.Operations import Operations


def process_float(arg):
    str_arg = ("%." + Config.get_instance().get('POPULATION', 'precision') + "f") % (arg)
    return str_arg


class Plus_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "+", 1)

    def formal(self):
        return "(" + self._nodes[0].formal() + " + " + self._nodes[1].formal() + ")"

    def op_simplify(self):
        # If one of the arguments is zero, avoid the operation
        if self._node_arg_x_is_y(0, 0):
            return Leaf_Node(self._nodes[1].to_string())
        elif self._node_arg_x_is_y(1, 0):
            return Leaf_Node(self._nodes[0].to_string())

        # Non of the arguments are zero. Make the operation if they are not sensors
        if not self._nodes[0].is_sensor() and not self._nodes[1].is_sensor():
            arg = float(self._nodes[0].to_string()) + float(self._nodes[1].to_string())
            return Leaf_Node(process_float(arg))
        else:
            return self

    def op_compute(self, arg_list):
        return arg_list[0] + arg_list[1]


class Minus_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "-", 1)

    def formal(self):
        return "(" + self._nodes[0].formal() + " - " + self._nodes[1].formal() + ")"

    def op_simplify(self):
        # If the second argument is zero, avoid the operation.
        if self._node_arg_x_is_y(1, 0):
            return Leaf_Node(self._nodes[0].to_string())

        # Non of the arguments are zero. Make the operation if they are not sensors
        if not self._nodes[0].is_sensor() and not self._nodes[1].is_sensor():
            arg = float(self._nodes[0].to_string()) - float(self._nodes[1].to_string())
            return Leaf_Node(process_float(arg))
        else:
            return self

    def op_compute(self, arg_list):
        return arg_list[0] - arg_list[1]


class Mult_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "*", 1)

    def formal(self):
        return "(" + self._nodes[0].formal() + " .* " + self._nodes[1].formal() + ")"

    def op_simplify(self):
        # If one or both of the arguments are zero, return zero
        if self._node_arg_x_is_y(0, 0) or self._node_arg_x_is_y(1, 0):
            return Leaf_Node(process_float(0))

        # If one of the arguments is zero, avoid the operation
        if self._node_arg_x_is_y(0, 1):
            return Leaf_Node(self._nodes[1].to_string())
        elif self._node_arg_x_is_y(1, 1):
            return Leaf_Node(self._nodes[0].to_string())

        if not self._nodes[0].is_sensor() and not self._nodes[1].is_sensor():
            arg = float(self._nodes[0].to_string()) * float(self._nodes[1].to_string())
            return Leaf_Node(process_float(arg))
        else:
            return self

    def op_compute(self, arg_list):
        return arg_list[0] * arg_list[1]


class Division_Node(Internal_Node):
    PROTECTION = 0.001

    def __init__(self):
        Internal_Node.__init__(self, "/", 1)

    def formal(self):
        return "(my_div(" + self._nodes[0].formal() + "," + self._nodes[1].formal() + "))"

    def _process_division(self, dividend, divisor):
        if type(divisor) == np.ndarray:
            # Check if at least one element is below the protection value
            if [x for x in divisor if abs(x) < Division_Node.PROTECTION] != []:
                return np.sign(divisor) * dividend / np.repeat(Division_Node.PROTECTION, len(divisor))
        else:
            if abs(divisor) < Division_Node.PROTECTION:
                return dividend / Division_Node.PROTECTION

        return dividend / divisor

    def op_simplify(self):
        # If the first argument is zero, return zero
        if self._node_arg_x_is_y(0, 0):
            return Leaf_Node(process_float(0))

        # If the second argument is one, return the first argument
        if self._node_arg_x_is_y(1, 1):
            return Leaf_Node(self._nodes[0].to_string())

        if not self._nodes[0].is_sensor() and not self._nodes[1].is_sensor():
            # FIXME: Harcoded number. Change it
            if abs(float(self._nodes[1].to_string())) < 0.01:
                return Leaf_Node(process_float(0))
            else:
                arg = float(self._nodes[0].to_string()) / float(self._nodes[1].to_string())
                return Leaf_Node(process_float(arg))
        else:
            return self

    def op_compute(self, arg_list):
        return self._process_division(arg_list[0], arg_list[1])


class Sine_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "sin", 3)

    def formal(self):
        return "sin(" + self._nodes[0].formal() + ")"

    def op_simplify(self):
        if not self._nodes[0].is_sensor():
            arg = math.sin(float(self._nodes[0].to_string()))
            return Leaf_Node(process_float(arg))
        else:
            return self

    def op_compute(self, arg_list):
        return np.sin(arg_list[0])


class Cosine_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "cos", 3)

    def formal(self):
        return "cos(" + self._nodes[0].formal() + ")"

    def op_simplify(self):
        if not self._nodes[0].is_sensor():
            arg = math.cos(float(self._nodes[0].to_string()))
            return Leaf_Node(process_float(arg))
        else:
            return self

    def op_compute(self, arg_list):
        return np.cos(arg_list[0])


class Logarithm_Node(Internal_Node):
    PROTECTION = 0.00001

    def __init__(self):
        Internal_Node.__init__(self, "log", 5)

    def formal(self):
        return "my_log(" + self._nodes[0].formal() + ")"

    def _process_arg(self, arg):
        if type(arg) == np.ndarray:
            # Check if at least one element is below the protection value
            if [x for x in arg if abs(x) < Logarithm_Node.PROTECTION] != []:
                return np.repeat(Logarithm_Node.PROTECTION, len(arg))
        else:
            if abs(arg) < Logarithm_Node.PROTECTION:
                return Logarithm_Node.PROTECTION

        return abs(arg)

    def op_simplify(self):
        if not self._nodes[0].is_sensor():
            if float(self._nodes[0].to_string()) < 0.01:
                arg = math.log(0.01)
            else:
                arg = math.log(float(self._nodes[0].to_string()))

            return Leaf_Node(process_float(arg))
        else:
            return self

    def op_compute(self, arg_list):
        return np.log(self._process_arg(arg_list[0]))


class Exponential_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "exp", 5)

    def formal(self):
        return "exp(" + self._nodes[0].formal() + ")"

    def op_simplify(self):
        if not self._nodes[0].is_sensor():
            lg.logger_.debug("[EXP NODE] Value: " + self._nodes[0].to_string())
            try:
                arg = math.exp(float(self._nodes[0].to_string()))
            except OverflowError:
                # FIXME: See what to do with this expression, because there are problems with
                # an infinite value is the argumento of a sinusoidal function
                return Leaf_Node(process_float(float("inf")))

            return Leaf_Node(process_float(arg))
        else:
            return self

    def op_compute(self, arg_list):
        return np.exp(arg_list[0])


class Tanh_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "tanh", 5)

    def formal(self):
        return "tanh(" + self._nodes[0].formal() + ")"

    def op_simplify(self):
        if not self._nodes[0].is_sensor():
            arg = math.tanh(float(self._nodes[0].to_string()))
            return Leaf_Node(process_float(arg))
        else:
            return self

    def op_compute(self, arg_list):
        return np.tanh(arg_list[0])


class RootNode(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "", 0)

    def to_string(self):
        return " ".join([n.to_string() for n in self._nodes])

    def simplify(self):
        self._nodes = [node.simplify() for node in self._nodes]
        return self

    def compute(self):
        if len(self._nodes) == 1:
            return self._nodes[0].compute()

        return [node.compute() for node in self._nodes]

    def formal(self):
        if len(self._nodes) == 1:
            return self._nodes[0].formal()

        return [n.formal() for n in self._nodes]

    def accept(self, visitor):
        for node in self._nodes:
            node.accept(visitor)


class Op_Node_Factory:
    @staticmethod
    def make(op):
        if op == 'root':
            return RootNode()

        # instatiate node from string
        operation = Operations.get_instance().get_operation_from_op_string(op)
        node_module_name = ".".join(operation['tree_node_class'].split('.')[:-1])
        node_class_name = ".".join(operation['tree_node_class'].split('.')[-1:])

        node_module = importlib.import_module(node_module_name)
        node_class = getattr(node_module, node_class_name)

        return node_class()
