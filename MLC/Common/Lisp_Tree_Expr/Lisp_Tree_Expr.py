import MLC.Log.log as lg
import md5
from ctypes import *
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Common.Operations import Operations
from MLC.Common.Lisp_Tree_Expr.Tree_Nodes import Leaf_Node
from MLC.Common.Lisp_Tree_Expr.Tree_Nodes import Internal_Node
from MLC.Common.Lisp_Tree_Expr.Operation_Nodes import Op_Node_Factory


class Lisp_Tree_Expr(object):

    def __init__(self, expr):
        self._expanded_tree = expr

        # Remove the root part of the node
        nonroot_expr = expr[expr.find('root') + 5:-1]
        lg.logger_.debug("[LISP_TREE_EXPR] NonRoot Expression: " + nonroot_expr)
        self._root, offset = self._generate_node(nonroot_expr)

        # Get the complexity of the tree before simplifying
        self._complexity = self._root.complexity()
        self._formal = self._root.formal()

        # Now, simplify the tree
        if int(Config.get_instance().get_param('OPTIMIZATION', 'simplify')) != 0:
            self.simplify_tree()

    def simplify_tree(self):
        self._root = self._root.simplify()
        self._simplified_tree = '(root ' + self._root.to_string() + ')'
        lg.logger_.debug("[LISP_TREE_EXPR] Simplified Expression: " + self._simplified_tree)

    def get_root_node(self):
        return self._root

    def get_expanded_tree_as_string(self):
        return '(root ' + self._root.to_string() + ')'

    def get_simplified_tree_as_string(self):
        return self._simplified_tree

    def complexity(self):
        """
        The complexity of the tree is a number given by the weight of every operation and
        the amount of constants/sensors stored
        """
        return self._complexity

    def formal(self):
        """
        Return the tree as a MATLAB expression, in order to calculate the value of the individual
        """
        return self._formal

    def calculate_hash(self):
        """
        Generate a hash with the Individual as a string, and convert that hash to a float value
        """
        # http://stackoverflow.com/questions/1592158/convert-hex-to-float
        expr_hash = md5.new(self._expanded_tree).hexdigest()
        # convert from hex to a Python int
        i = int(expr_hash, 16)
        # make this into a c integer
        cp = pointer(c_int(i))
        # cast the int pointer to a float pointer
        fp = cast(cp, POINTER(c_float))
        # dereference the pointer, get the float
        return fp.contents.value

    def _get_operation(self, expr):
        pos = -1
        expr_op = None
        # Get operation string
        str_op = expr[1:expr.find(' ')]

        # If the operation doesn not exists, an exception is thrown. This
        # shouldn't happen if the expression is valid
        try:
            expr_op = Operations.get_instance().get_operation_from_op_string(str_op)
        except KeyError:
            lg.logger_.error('[LISP_TREE_EXPR] Invalid operation found. Op: ', str_op)
            raise

        return expr_op

    def _generate_leaf_node(self, expr):
        # We found a Leaf Node
        param_len = 0

        find_space = expr.find(' ')
        find_close_parenthesis = expr.find(')')

        # Find the first space or colon
        if find_space != -1 and find_space < find_close_parenthesis:
            param_len = find_space
        elif find_close_parenthesis != -1:
            param_len = find_close_parenthesis
        else:
            param_len = len(expr)

        return Leaf_Node(expr[:param_len]), param_len + 1

    # As a precondition, the expression must be well-formed
    def _generate_node(self, expr):
        if expr[0] != '(':
            return self._generate_leaf_node(expr)

        # We are in the presence of an internal node. Get the operation
        op = self._get_operation(expr)

        # Generate the arguments of the internal node as Child Nodes
        node = Op_Node_Factory.make(op["op"])
        expr_offset = 0
        offset = 0
        child_node = None

        for i in range(op["nbarg"]):
            # 1 colon + op len + 1 space + (expr_offset)
            next_arg_pos = 1 + len(op["op"]) + 1 + expr_offset

            if expr[next_arg_pos] == '(':
                child_node, offset = self._generate_node(expr[next_arg_pos:])
            else:
                child_node, offset = self._generate_leaf_node(expr[next_arg_pos:])

            node.add_child(child_node)
            # print "Offset: " + str(offset)
            expr_offset += offset

        next_arg_pos = 1 + len(op["op"]) + 1 + expr_offset + 1
        return node, next_arg_pos


class TreeVisitor:
    def visit_internal_node(self, node):
        pass

    def visit_leaf_node(self, ndoe):
        pass