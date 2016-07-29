import unittest

from MLC.matlab_engine import MatlabEngine
from MLC.Common.Lisp_Tree_Expr.Lisp_Tree_Expr import Lisp_Tree_Expr


class SimplificationTest(unittest.TestCase):
    def setUp(self):
    	self._eng = MatlabEngine.engine()

    def test_simplify_plus_nodes(self):
    	expression = '(+ 3.4092 4.2123)'
    	expected = self._eng.simplify_my_LISP(expression)

    	tree = Lisp_Tree_Exp(expression)
    	obtained = tree.get_simplified_tree_as_string()

    	self.assertEquals(obtained, expected) 







