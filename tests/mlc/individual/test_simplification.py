import unittest
import MLC.Log.log as lg
from MLC.Log.log import set_logger
from MLC.matlab_engine import MatlabEngine
from MLC.Config.Config import Config
from MLC.Common.Lisp_Tree_Expr.Lisp_Tree_Expr import Lisp_Tree_Expr


class SimplificationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_logger("testing")
        config = Config.get_instance()
        config.read('configuration.ini')

    def setUp(self):
        self._eng = MatlabEngine.engine()

    def test_simplify_plus_nodes(self):
        expression = '(root (+ 3.4092 4.2123))'
        expected = self._eng.simplify_my_LISP(expression)

        tree = Lisp_Tree_Expr(expression)
        obtained = tree.get_simplified_tree_as_string()

        self.assertEquals(obtained, expected)
