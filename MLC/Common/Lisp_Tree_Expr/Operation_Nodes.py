import math
from MLC.Common.Lisp_Tree_Expr.Tree_Nodes import Tree_Node
from MLC.Common.Lisp_Tree_Expr.Tree_Nodes import Leaf_Node
from MLC.Common.Lisp_Tree_Expr.Tree_Nodes import Internal_Node
from MLC.Config.Config import Config


class Plus_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "+")

    def op_simplify(self):
        # If one of the arguments is zero, avoid the operation
        if self._node_arg_x_is_y(0, 0):
            return Leaf_Node(self._nodes[1].to_string())
        elif self._node_arg_x_is_y(1, 0):
            return Leaf_Node(self._nodes[0].to_string())

        # Non of the arguments are zero. Make the operation if they are not sensors
        if not self._nodes[0].is_sensor() and not self._nodes[1].is_sensor():
            arg = float(self._nodes[0].to_string()) + float(self._nodes[1].to_string())
            str_arg = ("%." + Config.get_instance().get_param('POPULATION', 'precision') + "f") % (arg)
            return Leaf_Node(str_arg)
        else:
            return self


class Minus_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "-")

    def op_simplify(self):
        # If the second argument is zero, avoid the operation.
        if self._node_arg_x_is_y(1, 0):
            return Leaf_Node(self._nodes[0].to_string())

        # Non of the arguments are zero. Make the operation if they are not sensors
        if not self._nodes[0].is_sensor() and not self._nodes[1].is_sensor():
            arg = float(self._nodes[0].to_string()) - float(self._nodes[1].to_string())
            str_arg = ("%." + Config.get_instance().get_param('POPULATION', 'precision') + "f") % (arg)
            return Leaf_Node(str_arg)
        else:
            return self


class Mult_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "*")

    def op_simplify(self):
        # If one or both of the arguments are zero, return zero
        if self._node_arg_x_is_y(0, 0) or self._node_arg_x_is_y(1, 0):
            return Leaf_Node("0")

        # If one of the arguments is zero, avoid the operation
        if self._node_arg_x_is_y(0, 1):
            return Leaf_Node(self._nodes[1].to_string())
        elif self._node_arg_x_is_y(1, 1):
            return Leaf_Node(self._nodes[0].to_string())

        if not self._nodes[0].is_sensor() and not self._nodes[1].is_sensor():
            arg = float(self._nodes[0].to_string()) * float(self._nodes[1].to_string())
            str_arg = ("%." + Config.get_instance().get_param('POPULATION', 'precision') + "f") % (arg)
            return Leaf_Node(str_arg)
        else:
            return self


class Division_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "/")

    def op_simplify(self):
        # If the first argument is zero, return zero
        if self._node_arg_x_is_y(0, 0):
            return Leaf_Node("0")

        # If the second argument is one, return the first argument
        if self._node_arg_x_is_y(1, 1):
            return Leaf_Node(self._nodes[0].to_string())

        if not self._nodes[0].is_sensor() and not self._nodes[1].is_sensor():
            # FIXME: Harcoded number. Change it
            if float(self._nodes[1].to_string()) < 0.01:
                return Leaf_Node("0")
            else:
                arg = float(self._nodes[0].to_string()) / float(self._nodes[1].to_string())
                str_arg = ("%." + Config.get_instance().get_param('POPULATION', 'precision') + "f") % (arg)
                return Leaf_Node(str_arg)
        else:
            return self


class Sine_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "sin")

    def op_simplify(self):
        arg = math.sin(float(self._nodes[0].to_string()))
        str_arg = ("%." + Config.get_instance().get_param('POPULATION', 'precision') + "f") % (arg)
        return Leaf_Node(str_arg)


class Cosine_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "cos")

    def op_simplify(self):
        arg = math.cos(float(self._nodes[0].to_string()))
        str_arg = ("%." + Config.get_instance().get_param('POPULATION', 'precision') + "f") % (arg)
        return Leaf_Node(str_arg)


class Logarithm_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "log")

    def op_simplify(self):
        arg = math.cos(float(self._nodes[0].to_string()))
        str_arg = ("%." + Config.get_instance().get_param('POPULATION', 'precision') + "f") % (arg)
        return Leaf_Node(str_arg)


class Exponential_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "exp")

    def op_simplify(self):
        arg = math.exp(float(self._nodes[0].to_string()))
        str_arg = ("%." + Config.get_instance().get_param('POPULATION', 'precision') + "f") % (arg)
        return Leaf_Node(str_arg)


class Tanh_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "tanh")

    def op_simplify(self):
        arg = math.tanh(float(self._nodes[0].to_string()))
        str_arg = ("%." + Config.get_instance().get_param('POPULATION', 'precision') + "f") % (arg)
        return Leaf_Node(str_arg)


class Op_Node_Factory:
    _nodes = {'+': Plus_Node,
              '-': Minus_Node,
              '*': Mult_Node,
              '/': Division_Node,
              'sin': Sine_Node,
              'cos': Cosine_Node,
              'log': Logarithm_Node,
              'exp': Exponential_Node,
              'tanh': Tanh_Node}

    @staticmethod
    def make(op):
        return Op_Node_Factory._nodes[op]()
