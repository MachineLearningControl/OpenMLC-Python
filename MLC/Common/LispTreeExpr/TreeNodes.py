class TreeNode(object):

    def __init__(self):
        self._depth = -1
        self._subtreedepth = -1
        self._expr_index = -1

    def get_depth(self):
        return self._depth

    def set_depth(self, depth):
        self._depth = depth

    def get_subtreedepth(self):
        return self._subtreedepth

    def set_subtreedepth(self, depth):
        self._subtreedepth = depth

    def get_expr_index(self):
        return self._expr_index

    def set_expr_index(self, expr_index):
        self._expr_index = expr_index

    def to_string(self):
        raise NotImplementedError('TreeNode', 'to_string is an abstract method')

    def simplify(self):
        raise NotImplementedError('TreeNode', 'simplify is an abstract method')

    # def can_simplify(self):
    #     raise NotImplementedError('TreeNode', 'can_simplify is an abstract method')

    def is_leaf(self):
        raise NotImplementedError('TreeNode', 'leaf is an abstract method')

    def complexity(self):
        raise NotImplementedError('TreeNode', 'complexity is an abstract method')

    # def value(self):
    #     raise NotImplementedError('TreeNode', 'value is an abstract method')

    def formal(self):
        raise NotImplementedError('TreeNode', 'formal is an abstract method')

    def compute(self):
        raise NotImplementedError('TreeNode', 'compute is an abstract method')

    def accept(self, visitor):
        raise NotImplementedError('TreeNode', 'accept is an abstract method')

class LeafNode(TreeNode):

    def __init__(self, arg):
        TreeNode.__init__(self)
        # String value of the node
        self._arg = arg
        # Numerical value of the node
        self._value = None

    def to_string(self):
        return str(self._arg)

    def simplify(self):
        return self

    def is_leaf(self):
        return True

    def complexity(self):
        return 1

    def is_sensor(self):
        try:
            float(self._arg)
            return False
        except ValueError:
            return True

    def formal(self):
        try:
            value = float(self._arg)
            if value < 0:
                return "(" + self._arg + ")"
        except ValueError:
            pass

        return str(self._arg)

    def compute(self):
        return self._value

    def accept(self, visitor):
        visitor.visit_leaf_node(self)

class InternalNode(TreeNode):

    def __init__(self, op, complexity):
        TreeNode.__init__(self)
        self._op = op
        self._complexity = complexity
        self._nodes = []

    def _node_arg_x_is_y(self, index, value):
        """
        Returns true if the argument of the node x is y. False in other case
        """
        try:
            if float(self._nodes[index].to_string()) == value:
                return True
        except ValueError:
            return False

        return False

    def add_child(self, node):
        self._nodes.append(node)

    def to_string(self):
        string = '(' + self._op + ' '

        for node in self._nodes:
            string += node.to_string() + ' '

        string = string[:-1]
        string += ')'
        return string

    def simplify(self):
        # First, simplify the child nodes
        for i, node in enumerate(self._nodes):
            simplified_node = node.simplify()
            self._nodes[i] = simplified_node

        for node in self._nodes:
            if not node.is_leaf():
                return self

        return self.op_simplify()

    def is_leaf(self):
        # Check if the list is empty
        return not self._nodes

    def complexity(self):
        counter = 0
        for node in self._nodes:
            counter += node.complexity()

        return counter + self._complexity

    def formal(self):
        raise NotImplementedError('InternalNode', "formal is an abstract method")

    def op_simplify(self):
        raise NotImplementedError('InternalNode', "op_simplify shouldn't be called")

    def op_compute(self):
        raise NotImplementedError('InternalNode', "op_compute shouldn't be called")

    def compute(self):
        arg_list = []
        for node in self._nodes:
            arg_list.append(node.compute())

        return self.op_compute(arg_list)

    def accept(self, visitor):
        for node in self._nodes:
            node.accept(visitor)
        visitor.visit_internal_node(self)