import unittest
import MLC.Log.log as lg
from MLC.Log.log import set_logger
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Common.LispTreeExpr.LispTreeExpr import LispTreeExpr
from MLC import config as config_path

import os

class ExpressionTreeTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_logger("testing")
        config = Config.get_instance()
        config.read(os.path.join(config_path.get_test_path(), 'mlc/individual/configuration.ini'))

    def setUp(self):
        pass

    def test_tree_depth_root(self):
        expression = '(root S0)'
        tree = LispTreeExpr(expression)

        # root
        root = tree.get_root_node()
        self.assertNode(root, depth=1, childs=1, expr_index=0)

        # S0
        self.assertNode(root._nodes[0], depth=1, childs=0, expr_index=6)

    def test_tree_depth_leaf(self):
        expression = '(root (tanh S0))'
        tree = LispTreeExpr(expression)

        # root
        root = tree.get_root_node()
        self.assertNode(root, depth=1, childs=1, expr_index=0)

        # (tanh S0)
        sub_expression = root._nodes[0]
        self.assertNode(sub_expression, depth=2, childs=1, expr_index=6)

        # S0
        self.assertNode(sub_expression._nodes[0], depth=2, childs=0, expr_index=12)

    def test_tree_subtree(self):
        expression = '(root (+ (tanh S0) (cos S1))))'
        tree = LispTreeExpr(expression)

        # root
        root = tree.get_root_node()
        self.assertNode(root, 1, 1, expr_index=0)

        # (+ (tanh S0) (cos S1)))
        sum_node = root._nodes[0]
        self.assertNode(sum_node, depth=2, childs=2, expr_index=6)

        # (tanh S0)
        subtree_0 = sum_node._nodes[0]
        self.assertNode(subtree_0, depth=3, childs=1, expr_index=9)
        self.assertNode(subtree_0._nodes[0], depth=3, childs=0, expr_index=15)

        # (cos S1)
        subtree_1 = sum_node._nodes[1]
        self.assertNode(subtree_1, depth=3, childs=1, expr_index=19)
        self.assertNode(subtree_1._nodes[0], depth=3, childs=0, expr_index=24)

    def assertNode(self, node, depth, childs, expr_index):
        self.assertEquals(node.get_depth(), depth)
        self.assertEquals(node.get_expr_index(), expr_index)

        if not node.is_leaf():
            self.assertEquals(len(node._nodes), childs)
