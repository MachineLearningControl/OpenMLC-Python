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

    # def value(self):
    #     raise NotImplementedError('Tree_Node', 'value is an abstract method')


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

    def is_sensor(self):
        try:
            float(self._arg)
            return False
        except ValueError:
            return True


class Internal_Node(Tree_Node):

    def __init__(self, op):
        Tree_Node.__init__(self)
        self._op = op
        self._nodes = []

    """
    { Returns true if the argument of the node x is y. False in other case }
    """
    def _node_arg_x_is_y(self, index, value):
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
        # print "Simplifying: " + self.to_string()
        # First, simplify the child nodes
        for i, node in enumerate(self._nodes):
            # print "Node #", i, " - Type: ", type(node).__name__
            simplified_node = node.simplify()
            self._nodes[i] = simplified_node

        for node in self._nodes:
            # print type(node).__name__
            if not node.is_leaf():
                # print "YO MAMMA"
                return self

        return self.op_simplify()

    def is_leaf(self):
        # Check if the list is empty
        return not self._nodes

    def op_simplify(self):
        raise NotImplementedError('Internal_Node', "op_simplify shouldn't be called")
