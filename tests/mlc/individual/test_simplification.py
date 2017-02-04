import unittest
import MLC.Log.log as lg
import sys
from MLC.Log.log import set_logger
from MLC.mlc_parameters.mlc_parameters import Config
from MLC.Common.LispTreeExpr.LispTreeExpr import LispTreeExpr
from MLC import config as config_path

import os


class SimplificationTest(unittest.TestCase):
    # Instead of calculate the Lisp Expression using MATLAB, consume them
    # from this dictionary. Take into consideration that the dictionary
    # has to be regenerated if some test is changed
    simplified_expressions = {"test_simplify_cos_node_number": "(root -0.1411)",
                              "test_simplify_cos_node_sensor": "(root (cos S0))",
                              "test_simplify_div_node_both_numbers": "(root 0.8093)",
                              "test_simplify_div_node_number_and_sensor": "(root (/ 3.4092 S0))",
                              "test_simplify_div_node_number_and_zero": "(root 0.0000)",
                              "test_simplify_div_node_sensor_and_number": "(root (/ S0 4.2123))",
                              "test_simplify_div_node_sensor_and_right_identity": "(root S0)",
                              "test_simplify_div_node_sensor_left_identity": "(root S0)",
                              "test_simplify_div_node_zero_and_sensor": "(root 0.0000)",
                              "test_simplify_exp_node_number": "(root 5.5422)",
                              "test_simplify_exp_node_sensor": "(root (exp S0))",
                              "test_simplify_log_node_number": "(root 0.5379)",
                              "test_simplify_log_node_sensor": "(root (log S0))",
                              "test_simplify_log_node_zero": "(root -4.6052)",
                              "test_simplify_minus_node_both_numbers": "(root -0.8031)",
                              "test_simplify_minus_node_number_and_sensor": "(root (- 3.4092 S0))",
                              "test_simplify_minus_node_sensor_and_left_identity": "(root 0.0000)",
                              "test_simplify_minus_node_sensor_and_number": "(root (- S0 4.2123))",
                              "test_simplify_minus_node_sensor_and_right_identity": "(root 0.0000)",
                              "test_simplify_mult_node_both_numbers": "(root 14.3606)",
                              "test_simplify_mult_node_left_zero": "(root 0.0000)",
                              "test_simplify_mult_node_number_and_sensor": "(root (* 3.4092 S0))",
                              "test_simplify_mult_node_sensor_and_number": "(root (* S0 4.2123))",
                              "test_simplify_mult_node_sensor_right_zero": "(root 0.0000)",
                              "test_simplify_plus_node_both_numbers": "(root 7.6215)",
                              "test_simplify_plus_node_number_and_sensor": "(root (+ 3.4092 S0))",
                              "test_simplify_plus_node_sensor_and_left_identity": "(root S0)",
                              "test_simplify_plus_node_sensor_and_number": "(root (+ S0 4.2123))",
                              "test_simplify_plus_node_sensor_and_right_identity": "(root S0)",
                              "test_simplify_sin_node_number": "(root 0.9900)",
                              "test_simplify_sin_node_sensor": "(root (sin S0))",
                              "test_simplify_tanh_node_number": "(root 0.9369)",
                              "test_simplify_tanh_node_sensor": "(root (tanh S0))"}

    @classmethod
    def setUpClass(cls):
        set_logger("file")
        config = Config.get_instance()
        config.read(os.path.join(config_path.get_test_path(), 'mlc/individual/configuration.ini'))

    def _assert_expressions(self, expression, function_name):
        # expected = self._eng.simplify_my_LISP(expression)
        expected = SimplificationTest.simplified_expressions[function_name]
        tree = LispTreeExpr(expression)
        tree.simplify_tree()
        obtained = tree.get_simplified_tree_as_string()
        self.assertEquals(obtained, expected)

    ########################### PLUS NODE #####################################
    def test_simplify_plus_node_number_and_sensor(self):
        expression = '(root (+ 3.4092 S0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_plus_node_sensor_and_number(self):
        expression = '(root (+ S0 4.2123))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_plus_node_sensor_and_right_identity(self):
        expression = '(root (+ S0 0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_plus_node_sensor_and_left_identity(self):
        expression = '(root (+ 0 S0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_plus_node_both_numbers(self):
        expression = '(root (+ 3.4092 4.2123))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    ########################### MINUS NODE ####################################
    def test_simplify_minus_node_number_and_sensor(self):
        expression = '(root (- 3.4092 S0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_minus_node_sensor_and_number(self):
        expression = '(root (- S0 4.2123))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_minus_node_sensor_and_right_identity(self):
        expression = '(root (- S0 0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_minus_node_sensor_and_left_identity(self):
        expression = '(root (- 0 S0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_minus_node_both_numbers(self):
        expression = '(root (- 3.4092 4.2123))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    ########################### MULT NODE #####################################
    def test_simplify_mult_node_number_and_sensor(self):
        expression = '(root (* 3.4092 S0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_mult_node_sensor_and_number(self):
        expression = '(root (* S0 4.2123))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_mult_node_left_zero(self):
        expression = '(root (* S0 0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_mult_node_sensor_right_zero(self):
        expression = '(root (* 0 S0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_minus_node_sensor_and_right_identity(self):
        expression = '(root (* S0 0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_minus_node_sensor_and_left_identity(self):
        expression = '(root (* 0 S0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_mult_node_both_numbers(self):
        expression = '(root (* 3.4092 4.2123))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    ########################### DIV NODE ######################################
    def test_simplify_div_node_number_and_sensor(self):
        expression = '(root (/ 3.4092 S0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_div_node_sensor_and_number(self):
        expression = '(root (/ S0 4.2123))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_div_node_zero_and_sensor(self):
        expression = '(root (/ 0 S0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_div_node_sensor_and_right_identity(self):
        expression = '(root (/ S0 1))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_div_node_sensor_left_identity(self):
        expression = '(root (* 1 S0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_div_node_both_numbers(self):
        expression = '(root (/ 3.4092 4.2123))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_div_node_number_and_zero(self):
        expression = '(root (/ 3.4092 0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    ########################### SIN NODE ######################################
    def test_simplify_sin_node_number(self):
        expression = '(root (sin 1.7124))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_sin_node_sensor(self):
        expression = '(root (sin S0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    ########################### COS NODE ######################################
    def test_simplify_cos_node_number(self):
        expression = '(root (cos 1.7124))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_cos_node_sensor(self):
        expression = '(root (cos S0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    ########################### LOG NODE ######################################
    def test_simplify_log_node_number(self):
        expression = '(root (log 1.7124))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_log_node_sensor(self):
        expression = '(root (log S0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_log_node_zero(self):
        expression = '(root (log 0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    ########################### EXP NODE ######################################
    def test_simplify_exp_node_number(self):
        expression = '(root (exp 1.7124))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_exp_node_sensor(self):
        expression = '(root (exp S0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    ########################### TANH NODE ######################################
    def test_simplify_tanh_node_number(self):
        expression = '(root (tanh 1.7124))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)

    def test_simplify_tanh_node_sensor(self):
        expression = '(root (tanh S0))'
        self._assert_expressions(expression, sys._getframe().f_code.co_name)
