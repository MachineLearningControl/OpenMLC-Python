import unittest
import MLC.Log.log as lg
from MLC.Log.log import set_logger
from MLC.matlab_engine import MatlabEngine
from MLC.Config.Config import Config
from MLC.Common.Lisp_Tree_Expr.Lisp_Tree_Expr import Lisp_Tree_Expr
from MLC import config as config_path

import os

class SimplificationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_logger("testing")
        config = Config.get_instance()
        config.read(os.path.join(config_path.get_test_path(), 'mlc/individual/configuration.ini'))

    def setUp(self):
        self._eng = MatlabEngine.engine()

    def _assert_expressions(self, expression):
        expected = self._eng.simplify_my_LISP(expression)
        tree = Lisp_Tree_Expr(expression)
        tree.simplify_tree()
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

    ########################### DIV NODE ######################################
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
        expression = '(root (* 1 S0))'
        self._assert_expressions(expression)

    def test_simplify_div_node_both_numbers(self):
        expression = '(root (/ 3.4092 4.2123))'
        self._assert_expressions(expression)

    def test_simplify_div_node_number_and_zero(self):
        expression = '(root (/ 3.4092 0))'
        self._assert_expressions(expression)

    ########################### SIN NODE ######################################
    def test_simplify_sin_node_number(self):
        expression = '(root (sin 1.7124))'
        self._assert_expressions(expression)

    def test_simplify_sin_node_sensor(self):
        expression = '(root (sin S0))'
        self._assert_expressions(expression)

    ########################### COS NODE ######################################
    def test_simplify_cos_node_number(self):
        expression = '(root (cos 1.7124))'
        self._assert_expressions(expression)

    def test_simplify_cos_node_sensor(self):
        expression = '(root (cos S0))'
        self._assert_expressions(expression)

    ########################### LOG NODE ######################################
    def test_simplify_log_node_number(self):
        expression = '(root (log 1.7124))'
        self._assert_expressions(expression)

    def test_simplify_log_node_sensor(self):
        expression = '(root (log S0))'
        self._assert_expressions(expression)

    def test_simplify_log_node_zero(self):
        expression = '(root (log 0))'
        self._assert_expressions(expression)

    ########################### EXP NODE ######################################
    def test_simplify_exp_node_number(self):
        expression = '(root (exp 1.7124))'
        self._assert_expressions(expression)

    def test_simplify_exp_node_sensor(self):
        expression = '(root (exp S0))'
        self._assert_expressions(expression)

    ########################### TANH NODE ######################################
    def test_simplify_tanh_node_number(self):
        expression = '(root (tanh 1.7124))'
        self._assert_expressions(expression)

    def test_simplify_tanh_node_sensor(self):
        expression = '(root (tanh S0))'
        self._assert_expressions(expression)

