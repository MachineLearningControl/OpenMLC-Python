class Tree_Node(object):

    def __init__(self):
        pass

    def to_string(self):
        raise NotImplementedError('Tree_Node', 'to_string is an abstract method')

    def simplify(self):
        raise NotImplementedError('Tree_Node', 'simplify is an abstract method')

    # def can_simplify(self):
    #     raise NotImplementedError('Tree_Node', 'can_simplify is an abstract method')

    def is_leaf(self):
        raise NotImplementedError('Tree_Node', 'leaf is an abstract method')

    def complexity(self):
        raise NotImplementedError('Tree_Node', 'complexity is an abstract method')

    # def value(self):
    #     raise NotImplementedError('Tree_Node', 'value is an abstract method')

    def formal(self):
        raise NotImplementedError('Tree_Node', 'formal is an abstract method')

    def accept(self, visitor):
        raise NotImplementedError('Tree_Node', 'accept is an abstract method')

class Leaf_Node(Tree_Node):

    def __init__(self, arg):
        Tree_Node.__init__(self)
        self._arg = arg

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

    def accept(self, visitor):
        visitor.visit_leaf_node(self)

class Internal_Node(Tree_Node):

    def __init__(self, op, complexity):
        Tree_Node.__init__(self)
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
        raise NotImplementedError('Internal_Node', "formal is an abstract method")

    def op_simplify(self):
        raise NotImplementedError('Internal_Node', "op_simplify shouldn't be called")

    def accept(self, visitor):
        for node in self._nodes:
            node.accept(visitor)
        visitor.visit_internal_node(self)