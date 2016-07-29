import math
from MLC.Common.Lisp_Tree_Expr.Tree_Nodes import Tree_Node
from MLC.Common.Lisp_Tree_Expr.Tree_Nodes import Leaf_Node
from MLC.Common.Lisp_Tree_Expr.Tree_Nodes import Internal_Node
from MLC.Config.Config import Config


class Plus_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "+")

    def op_simplify(self):
        arg = float(self._nodes[0].to_string()) + float(self._nodes[1].to_string())
        str_arg = ("%.4f") % (arg)
        return Leaf_Node(str_arg)


class Minus_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "-")

    def op_simplify(self):
        arg = float(self._nodes[0].to_string()) - float(self._nodes[1].to_string())
        str_arg = ("%.4f") % (arg)
        return Leaf_Node(str_arg)


class Mult_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "*")

    def op_simplify(self):
        arg = float(self._nodes[0].to_string()) * float(self._nodes[1].to_string())
        str_arg = ("%.4f") % (arg)
        return Leaf_Node(str_arg)


class Division_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "*")

    def op_simplify(self):
        arg = None
        try:
            arg = float(self._nodes[0].to_string()) * float(self._nodes[1].to_string())
        except ZeroDivisionError:
            arg = float(self._nodes[0].to_string()) * float(0.01)

        str_arg = ("%.4f") % (arg)
        return Leaf_Node(str_arg)


class Sine_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "*")

    def op_simplify(self):
        arg = math.sin(float(self._nodes[0].to_string()))
        str_arg = ("%.4f") % (arg)
        return Leaf_Node(str_arg)


class Cosine_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "*")

    def op_simplify(self):
        arg = math.cos(float(self._nodes[0].to_string()))
        str_arg = ("%.4f") % (arg)
        return Leaf_Node(str_arg)


class Logarithm_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "*")

    def op_simplify(self):
        arg = math.cos(float(self._nodes[0].to_string()))
        str_arg = ("%.4f") % (arg)
        return Leaf_Node(str_arg)


class Exponential_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "*")

    def op_simplify(self):
        arg = math.exp(float(self._nodes[0].to_string()))
        str_arg = ("%.4f") % (arg)
        return Leaf_Node(str_arg)


class Tanh_Node(Internal_Node):

    def __init__(self):
        Internal_Node.__init__(self, "*")

    def op_simplify(self):
        arg = math.tanh(float(self._nodes[0].to_string()))
        str_arg = ("%.4f") % (arg)
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
