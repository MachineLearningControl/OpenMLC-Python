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

    def _assert_expressions(self, expression):
        expected = self._eng.simplify_my_LISP(expression)
        tree = Lisp_Tree_Expr(expression)
        obtained = tree.get_simplified_tree_as_string()

        self.assertEquals(obtained, expected)

    ########################### PLUS NODE #####################################
    def test_simplify_plus_node_number_and_sensor(self):
        expression = '(root (+ 3.4092 S0))'
        self._assert_expressions(expression)

    def test_simplify_plus_node_sensor_and_number(self):
        expression = '(root (+ S0 4.2123))'
        self._assert_expressions(expression)

    def test_simplify_plus_node_sensor_and_right_identity(self):
        expression = '(root (+ S0 0))'
        self._assert_expressions(expression)

    def test_simplify_plus_node_sensor_and_left_identity(self):
        expression = '(root (+ 0 S0))'
        self._assert_expressions(expression)

    def test_simplify_plus_node_both_numbers(self):
        expression = '(root (+ 3.4092 4.2123))'
        self._assert_expressions(expression)

    ########################### MINUS NODE ####################################
    def test_simplify_minus_node_number_and_sensor(self):
        expression = '(root (- 3.4092 S0))'
        self._assert_expressions(expression)

    def test_simplify_minus_node_sensor_and_number(self):
        expression = '(root (- S0 4.2123))'
        self._assert_expressions(expression)

    def test_simplify_minus_node_sensor_and_right_identity(self):
        expression = '(root (- S0 0))'
        self._assert_expressions(expression)

    def test_simplify_minus_node_sensor_and_left_identity(self):
        expression = '(root (- 0 S0))'
        self._assert_expressions(expression)

    def test_simplify_minus_node_both_numbers(self):
        expression = '(root (- 3.4092 4.2123))'
        self._assert_expressions(expression)

    ########################### MULT NODE #####################################
    def test_simplify_mult_node_number_and_sensor(self):
        expression = '(root (* 3.4092 S0))'
        self._assert_expressions(expression)

    def test_simplify_mult_node_sensor_and_number(self):
        expression = '(root (* S0 4.2123))'
        self._assert_expressions(expression)

    def test_simplify_mult_node_left_zero(self):
        expression = '(root (* S0 0))'
        self._assert_expressions(expression)

    def test_simplify_mult_node_sensor_right_zero(self):
        expression = '(root (* 0 S0))'
        self._assert_expressions(expression)

    def test_simplify_minus_node_sensor_and_right_identity(self):
        expression = '(root (* S0 0))'
        self._assert_expressions(expression)

    def test_simplify_minus_node_sensor_and_left_identity(self):
        expression = '(root (* 0 S0))'
        self._assert_expressions(expression)

    def test_simplify_mult_node_both_numbers(self):
        expression = '(root (* 3.4092 4.2123))'
        self._assert_expressions(expression)

    ########################### DIV NODE #####################################
    def test_simplify_div_node_number_and_sensor(self):
        expression = '(root (/ 3.4092 S0))'
        self._assert_expressions(expression)

    def test_simplify_div_node_sensor_and_number(self):
        expression = '(root (/ S0 4.2123))'
        self._assert_expressions(expression)

    def test_simplify_div_node_zero_and_sensor(self):
        expression = '(root (/ 0 S0))'
        self._assert_expressions(expression)

    def test_simplify_div_node_sensor_and_right_identity(self):
        expression = '(root (/ S0 1))'
        self._assert_expressions(expression)

    def test_simplify_div_node_sensor_left_identity(self):
        expression = '(root (* 0 S0))'
        self._assert_expressions(expression)

    def test_simplify_div_node_both_numbers(self):
        expression = '(root (/ 3.4092 4.2123))'
        self._assert_expressions(expression)

    def test_simplify_div_node_number_and_zero(self):
        expression = '(root (/ 3.4092 0))'
        self._assert_expressions(expression)
