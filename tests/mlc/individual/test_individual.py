import unittest

from MLC.matlab_engine import MatlabEngine
from MLC.individual.Individual import Individual


class IndividualTest(unittest.TestCase):
    def setUp(self):
        self._engine = MatlabEngine.engine()
        self._engine.workspace['wmlc'] = self._engine.MLC2()
        self._params = self._engine.eval('wmlc.parameters')

    def test_generate_from_value(self):
        individual = Individual()
        individual.generate(self._params, "(root (exp (tanh (- (tanh -8.049) (* 9.15 -6.848)))))")

        self.assertEquals(individual.get_value(), "(root (exp (tanh (- (tanh -8.049) (* 9.15 -6.848)))))")
        self.assertEquals(individual.get_type(), 'tree')
        self.assertEquals(len(individual.get_cost_history()), 0)
        self.assertEquals(len(individual.get_evaluation_time()), 0)
        self.assertEquals(individual.get_appearences(), 1)
        self.assertEquals(individual.get_hash(), -1.2245757275056848e-288)
        self.assertEquals(individual.get_formal(), "exp(tanh((tanh((-8.049)) - (9.15 .* (-6.848)))))")
        self.assertEquals(individual.get_complexity(), 20)

    def test_random_generate(self):
        # set random seed
        self._engine.rand('seed', 50.0, nargout=0)
        individual = Individual()
        individual.generate(self._params, 3)

        self.assertEquals(individual.get_value(),"(root (cos (+ (sin (log -0.7648)) (exp (tanh 3.628)))))")
        self.assertEquals(individual.get_type(), 'tree')
        self.assertEquals(len(individual.get_cost_history()), 0)
        self.assertEquals(len(individual.get_evaluation_time()), 0)
        self.assertEquals(individual.get_appearences(), 1)
        self.assertEquals(individual.get_hash(), -1.4777973157426358e-58)
        self.assertEquals(individual.get_formal(),"cos((sin(my_log((-0.7648))) + exp(tanh(3.628))))")
        self.assertEquals(individual.get_complexity(), 24)

    def test_compare(self):
        individual_1 = Individual()
        individual_1.generate(self._params, "(root (exp (tanh (- (tanh -8.049) (* 9.15 -6.848)))))")

        individual_2 = Individual()
        individual_2.generate(self._params, "(root (exp (tanh (- (tanh -8.049) (* 9.15 -6.848)))))")

        self.assertTrue(individual_1.compare(individual_2))
        self.assertEquals(individual_1.get_hash(), individual_2.get_hash())

        individual_different = Individual()
        individual_different.generate(self._params, "(root (cos (+ (sin (log -0.7648)) (exp (tanh 3.628)))))")

        self.assertFalse(individual_1.compare(individual_different))
        self.assertNotEquals(individual_1.get_hash(), individual_different.get_hash())

    def test_compare_random_individuals(self):
        self._engine.rand('seed', 50.0, nargout=0)
        individual_1 = Individual()
        individual_1.generate(self._params, 3)

        self._engine.rand('seed', 50.0, nargout=0)
        individual_2 = Individual()
        individual_2.generate(self._params, 3)

        self.assertTrue(individual_1.compare(individual_2))
        self.assertEquals(individual_1.get_hash(), individual_2.get_hash())

    def test_generate_individuals_types(self):
        self._engine.rand('seed', 50.0, nargout=0)
        individual = Individual()

        individual.generate(self._params, 0)
        self.assertEquals(individual.get_value(),  "(root (cos 5.046))")
        self.assertEquals(individual.get_type(), 'tree')
        self.assertEquals(len(individual.get_cost_history()), 0)
        self.assertEquals(len(individual.get_evaluation_time()), 0)
        self.assertEquals(individual.get_appearences(), 1)
        self.assertEquals(individual.get_hash(), 3.9424597980921636e+70)
        self.assertEquals(individual.get_formal(), "cos(5.046)")
        self.assertEquals(individual.get_complexity(), 4)

        individual.generate(self._params, 1)
        self.assertEquals(individual.get_value(), "(root (log (sin (exp (tanh 3.628)))))")
        self.assertEquals(individual.get_type(), 'tree')
        self.assertEquals(len(individual.get_cost_history()), 0)
        self.assertEquals(len(individual.get_evaluation_time()), 0)
        self.assertEquals(individual.get_appearences(), 1)
        self.assertEquals(individual.get_hash(), 3.4383822393862387e+193)
        self.assertEquals(individual.get_formal(), "my_log(sin(exp(tanh(3.628))))")
        self.assertEquals(individual.get_complexity(), 19)

        individual.generate(self._params, 2)
        self.assertEquals(individual.get_value(), "(root (cos (* (+ (* -1.912 -9.178) (cos S0)) 3.113)))")
        self.assertEquals(individual.get_type(), 'tree')
        self.assertEquals(len(individual.get_cost_history()), 0)
        self.assertEquals(len(individual.get_evaluation_time()), 0)
        self.assertEquals(individual.get_appearences(), 1)
        self.assertEquals(individual.get_hash(), 3.159746489284278e-200)
        self.assertEquals(individual.get_formal(), "cos(((((-1.912) .* (-9.178)) + cos(S0)) .* 3.113))")
        self.assertEquals(individual.get_complexity(), 13)

        individual.generate(self._params, 3)
        self.assertEquals(individual.get_value(), "(root (log (/ (* (sin 4.37) (- -8.815 -3.902)) (log (+ 2.025 -8.685)))))")
        self.assertEquals(individual.get_type(), 'tree')
        self.assertEquals(len(individual.get_cost_history()), 0)
        self.assertEquals(len(individual.get_evaluation_time()), 0)
        self.assertEquals(individual.get_appearences(), 1)
        self.assertEquals(individual.get_hash(), -6.231379895727156e-22)
        self.assertEquals(individual.get_formal(), "my_log((my_div((sin(4.37) .* ((-8.815) - (-3.902))),my_log((2.025 + (-8.685))))))")
        self.assertEquals(individual.get_complexity(), 22)

        individual.generate(self._params, 4)
        self.assertEquals(individual.get_value(), "(root S0)")
        self.assertEquals(individual.get_type(), 'tree')
        self.assertEquals(len(individual.get_cost_history()), 0)
        self.assertEquals(len(individual.get_evaluation_time()), 0)
        self.assertEquals(individual.get_appearences(), 1)
        self.assertEquals(individual.get_hash(), 6.356047396756108e+217)
        self.assertEquals(individual.get_formal(), "S0")
        self.assertEquals(individual.get_complexity(), 1)
