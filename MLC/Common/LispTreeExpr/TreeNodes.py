# -*- coding: utf-8 -*-
# MLC (Machine Learning Control): A genetic algorithm library to solve chaotic problems
# Copyright (C) 2015-2017, Thomas Duriez (thomas.duriez@gmail.com)
# Copyright (C) 2015, Adrian Durán (adrianmdu@gmail.com)
# Copyright (C) 2015-2017, Ezequiel Torres Feyuk (ezequiel.torresfeyuk@gmail.com)
# Copyright (C) 2016-2017, Marco Germano Zbrun (marco.germano@intraway.com)
# Copyright (C) 2016-2017, Raúl Lopez Skuba (raulopez0@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

class TreeNode(object):
    def __init__(self, node_id):
        self._node_id = node_id
        self._depth = -1
        self._subtreedepth = -1
        self._expr_index = -1

    def get_node_id(self):
        return self._node_id

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

    def construct_tree(self, nx_tree):
        raise NotImplementedError('TreeNode', 'complexity is an abstract method')        

    def formal(self):
        raise NotImplementedError('TreeNode', 'formal is an abstract method')

    def compute(self):
        raise NotImplementedError('TreeNode', 'compute is an abstract method')

    def accept(self, visitor):
        raise NotImplementedError('TreeNode', 'accept is an abstract method')

class LeafNode(TreeNode):

    def __init__(self, node_id, arg):
        TreeNode.__init__(self, node_id)
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

    def construct_tree(self, nx_tree):
        nx_tree.add_node(self._node_id, value=str(self._arg))

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

    def __init__(self, node_id, op, complexity):
        TreeNode.__init__(self, node_id)
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

    def construct_tree(self, nx_tree):
        node_op = self._op
        if not self._op:
            node_op = 'root'
        nx_tree.add_node(self._node_id, value=node_op)

        for node in self._nodes:
            node.construct_tree(nx_tree)
            nx_tree.add_edge(self._node_id, node.get_node_id())

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