import MLC.Log.log as lg
from MLC.Config.Config import Config
from MLC.Common.Operations import Operations
from MLC.LISP_Tree_Expr.Leaf_Node import leaf_node
from MLC.LISP_Tree_Expr.Internal_Node import Internal_Node


class LISP_Tree_Expr(object):
    def __init__(self, expr):
        self._expanded_tree = expr
        self._root = self._generate_node(expr)
        self._simplified_tree = self

    def get_root_node(self):
        return self._root

    def simplify(self):
        self._root = self._root.simplify()
        self._simplified_tree = self._root.to_string()

    def get_expanded_tree_as_string(self):
        return self._expanded_tree

    def get_simplified_tree_as_string(self):
        return self._simplified_tree

    def _get_operation(self, expr):
        pos = -1
        expr_op = None
        # Get operation string
        str_op = expr[:expr.find(' ')

        # If the operation doesn not exists, an exception is thrown. This
        # shouldn't happen if the expression is valid
        try:
            expr_op = Operations.get_instance().get_operation(str_op)
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
        else:
            param_len = find_close_parenthesis

        return Leaf_Node(expr[:param_len]), param_len + 1

    # As a precondition, the expression must be well-formed
    def _generate_node(self, expr):
        if expr[0] != '(':
            return generate_leaf_node(exp)

        # We are in the presence of an internal node. Get the operation
        op = get_operation(expr)

        # Generate the arguments of the internal node as Child Nodes
        node = create_node[op["op"]()
        expr_offset = 0
        offset = 0
        child_node = None

        for i in range(op["nbarg"]):
            # 1 colon + op len + 1 space + (expr_offset)
            next_arg_pos = 1 + len(op["op"]) + 1 + expr_offset

            if expr[next_arg_pos] == '(':
                child_node, offset = generate_node(expr[next_arg_pos:])
            else:
                child_node, offset = generate_leaf_node(expr[next_arg_pos:])

            node.add_child(child_node)
            # print "Offset: " + str(offset)
            expr_offset += offset

        next_arg_pos = 1 + len(op["op"]) + 1 + expr_offset + 1
        return node, next_arg_pos
