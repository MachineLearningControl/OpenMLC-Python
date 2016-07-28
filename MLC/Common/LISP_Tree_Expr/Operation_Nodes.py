import math
from MLC.Common.LISP_Tree-Expr.Tree_Nodes import Tree_Node
from MLC.Common.LISP_Tree-Expr.Tree_Nodes import Leaf_Node
from MLC.Common.LISP_Tree-Expr.Tree_Nodes import Internal_Node


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


class Div_Node(Internal_Node):
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


class Op_Node_Factory:
    _nodes = {'+': Plus_Node,
              '-': Minus_Node,
              '*': Mult_Node,
              '/': Div_Node,
              'sin': Sine_Node,
              'cos': Cosine_Node,
              'exp': Exp_Node,
              'tanh': Tanh_Node}

    @staticmethod
    def make(op):
        return _nodes[op]()
