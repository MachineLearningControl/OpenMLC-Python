import unittest
import MLC.Log.log as lg
from MLC.Log.log import set_logger
from MLC.matlab_engine import MatlabEngine
from MLC.individual.Individual import Individual

from MLC.mlc_parameters.mlc_parameters import Config, saved
from MLC import config as mlc_config_path

import os
from nose.tools import nottest


class IndividualTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        set_logger("testing")
        cls._engine = MatlabEngine.engine()

        # Load randoms from file
        cls._random_file = './mlc/unit_matlab_randoms.txt'
        MatlabEngine.load_random_values(cls._random_file)

        cls._engine.workspace['wmlc'] = cls._engine.MLC2()
        config = Config.get_instance()
        config.read(os.path.join(mlc_config_path.get_test_path(), 'mlc/individual/configuration.ini'))
        Individual._maxdepthfirst = config.getint('GP', 'maxdepthfirst')

        cls._individual_l0 = Individual()
        cls._individual_l0.generate("(root (cos 5.046))")

        cls._individual_l1 = Individual()
        cls._individual_l1.generate("(root (log (sin (exp (tanh 3.6284)))))")

        cls._individual_l2 = Individual()
        cls._individual_l2.generate("(root (cos (* (+ (* -1.912 -9.178) (cos S0)) 3.113)))")

        cls._individual_l3 = Individual()
        cls._individual_l3.generate("(root (log (/ (* (sin 4.37) (- -8.815 -3.902)) (log (+ 2.025 -8.685)))))")

        cls._individual_l4 = Individual()
        cls._individual_l4.generate("(root S0)")

    def setUp(self):
        set_logger("testing")
        self._engine = MatlabEngine.engine()

        # Load randoms from file
        random_file = './mlc/unit_matlab_randoms.txt'
        MatlabEngine.clear_random_values()
        MatlabEngine.load_random_values(random_file)

        self._engine.workspace['wmlc'] = self._engine.MLC2()
        config = Config.get_instance()
        config.read(os.path.join(mlc_config_path.get_test_path(), 'mlc/individual/configuration.ini'))

        self._individual_l0 = Individual()
        self._individual_l0.generate("(root (cos 5.046))")

        self._individual_l1 = Individual()
        self._individual_l1.generate("(root (log (sin (exp (tanh 3.6284)))))")

        self._individual_l2 = Individual()
        self._individual_l2.generate("(root (cos (* (+ (* -1.912 -9.178) (cos S0)) 3.113)))")

        self._individual_l3 = Individual()
        self._individual_l3.generate("(root (log (/ (* (sin 4.37) (- -8.815 -3.902)) (log (+ 2.025 -8.685)))))")

        self._individual_l4 = Individual()
        self._individual_l4.generate("(root S0)")

    def test_generate_from_value(self):
        individual = Individual()
        individual.generate("(root (exp (tanh (- (tanh -8.049) (* 9.15 -6.848)))))")

        self.assertEquals(individual.get_value(), "(root (exp (tanh (- (tanh -8.049) (* 9.15 -6.848)))))")
        self.assertEquals(individual.get_type(), 'tree')
        self.assertEquals(len(individual.get_cost_history()), 0)
        self.assertEquals(individual.get_evaluation_time(), 0.0)
        self.assertEquals(individual.get_appearences(), 1)
        self.assertEquals(individual.get_hash(), "7a759235fc08876a665bf4188f11cfeb")
        self.assertEquals(individual.get_formal(), "exp(tanh((tanh((-8.049)) - (9.15 .* (-6.848)))))")
        self.assertEquals(individual.get_complexity(), 20)

    def test_random_generate(self):
        individual = Individual()
        individual.generate(3)

        self.assertEquals(individual.get_value(), "(root (sin (/ (+ (exp -2.6118) (cos S0)) (/ (log 5.9383) (log -4.5037)))))")
        self.assertEquals(individual.get_type(), 'tree')
        self.assertEquals(len(individual.get_cost_history()), 0)
        self.assertEquals(individual.get_evaluation_time(), 0.0)
        self.assertEquals(individual.get_appearences(), 1)
        self.assertEquals(individual.get_hash(), "48dfadaf63d552523b58e42fadc7eab4")
        self.assertEquals(individual.get_formal(), "sin((my_div((exp((-2.6118)) + cos(S0)),(my_div(my_log(5.9383),my_log((-4.5037)))))))")
        self.assertEquals(individual.get_complexity(), 28)

    def test_compare(self):
        individual_1 = Individual()
        individual_1.generate("(root (exp (tanh (- (tanh -8.049) (* 9.15 -6.848)))))")

        individual_2 = Individual()
        individual_2.generate("(root (exp (tanh (- (tanh -8.049) (* 9.15 -6.848)))))")

        self.assertTrue(individual_1.compare(individual_2))
        self.assertEquals(individual_1.get_hash(), individual_2.get_hash())

        individual_different = Individual()
        individual_different.generate("(root (cos (+ (sin (log -0.7648)) (exp (tanh 3.6284)))))")

        self.assertFalse(individual_1.compare(individual_different))
        self.assertNotEquals(individual_1.get_hash(), individual_different.get_hash())

    def test_compare_random_individuals(self):
        individual_1 = Individual()
        individual_1.generate(3)

        MatlabEngine.clear_random_values()
        MatlabEngine.load_random_values(self._random_file)
        individual_2 = Individual()
        individual_2.generate(3)

        self.assertTrue(individual_1.compare(individual_2))
        self.assertEquals(individual_1.get_hash(), individual_2.get_hash())

    def test_generate_individuals_types(self):
        individual = Individual()

        individual.generate(0)
        self._assert_individual(individual, complexity=120,
                                hash=3.9424597980921636e+70,
                                value="(root (sin (+ (/ (cos -3.0973) (exp (log (* (* -1.3423 (tanh (log -3.5094))) (+ (/ (/ (* -9.1213 (cos (exp 3.6199))) (cos (* S0 (cos (- 5.0161 (sin 4.2656)))))) S0) (- (cos (* (+ (sin -9.8591) (exp S0)) -9.4159)) (log (* (- (tanh -8.5969) S0) (/ (exp (/ 8.2118 S0)) (* (* S0 (* 1.6755 -0.0699)) (log (exp -3.2288)))))))))))) S0)))",
                                formal="sin(((my_div(cos((-3.0973)),exp(my_log((((-1.3423) .* tanh(my_log((-3.5094)))) .* ((my_div((my_div(((-9.1213) .* cos(exp(3.6199))),cos((S0 .* cos((5.0161 - sin(4.2656))))))),S0)) + (cos(((sin((-9.8591)) + exp(S0)) .* (-9.4159))) - my_log(((tanh((-8.5969)) - S0) .* (my_div(exp((my_div(8.2118,S0))),((S0 .* (1.6755 .* (-0.0699))) .* my_log(exp((-3.2288))))))))))))))) + S0))")

        individual.generate(1)
        self._assert_individual(individual, complexity=24,
                                hash=3.4383822393862387e+193,
                                value="(root (- (sin (* (log -3.7260) (+ -5.0573 -6.2191))) (* 7.3027 (/ (cos S0) (* 4.7410 6.7097)))))",
                                formal="(sin((my_log((-3.7260)) .* ((-5.0573) + (-6.2191)))) - (7.3027 .* (my_div(cos(S0),(4.7410 .* 6.7097)))))")

        individual.generate(2)
        self._assert_individual(individual, complexity=15,
                                hash=3.159746489284278e-200,
                                value="(root (tanh (cos (+ (+ 5.4434 -3.1258) (+ S0 5.1136)))))",
                                formal="tanh(cos(((5.4434 + (-3.1258)) + (S0 + 5.1136))))")

        individual.generate(3)
        self._assert_individual(individual, complexity=18,
                                hash=-6.231379895727156e-22,
                                value="(root (log (sin (+ (log -6.2620) (* 8.3709 -6.7676)))))",
                                formal="my_log(sin((my_log((-6.2620)) + (8.3709 .* (-6.7676)))))")

        individual.generate(4)
        self._assert_individual(individual, complexity=1,
                                hash=6.356047396756108e+217,
                                value="(root -0.6212)",
                                formal="(-0.6212)")

    def test_crossover_same_level_0(self):
        individual_1 = Individual()
        individual_1.generate("(root (cos 5.046))")
        individual_2 = Individual()
        individual_2.generate("(root (cos 5.046))")
        new_ind_1, new_ind_2, fail = individual_1.crossover(individual_2)

        self.assertFalse(fail)

        self._assert_individual(new_ind_1, complexity=4,
                                hash=3.9424597980921636e+70,
                                value="(root (cos 5.046))",
                                formal="cos(5.046)")

        self._assert_individual(new_ind_2, complexity=4,
                                hash=3.9424597980921636e+70,
                                value="(root (cos 5.046))",
                                formal="cos(5.046)")

    def test_crossover_same_level_2(self):
        individual_1 = Individual()
        individual_1.generate("(root (cos (* (+ (* -1.912 -9.178) (cos S0)) 3.113)))")
        individual_2 = Individual()
        individual_2.generate("(root (cos (* (+ (* -1.912 -9.178) (cos S0)) 3.113)))")
        new_ind_1, new_ind_2, fail = individual_1.crossover(individual_2)

        self._assert_individual(new_ind_1, complexity=8,
                                hash=3.988734956834988e-46,
                                value="(root (cos (* (* -1.912 -9.178) 3.113)))",
                                formal="cos((((-1.912) .* (-9.178)) .* 3.113))")

        self._assert_individual(new_ind_2, complexity=18,
                                hash=-4.5180143959687205e-194,
                                value="(root (cos (* (+ (+ (* -1.912 -9.178) (cos S0)) (cos S0)) 3.113)))",
                                formal="cos((((((-1.912) .* (-9.178)) + cos(S0)) + cos(S0)) .* 3.113))")

    def test_crossover_same_level_4(self):
        individual_1 = Individual()
        individual_1.generate("(root S0)")
        individual_2 = Individual()
        individual_2.generate("(root S0)")
        new_ind_1, new_ind_2, fail = individual_1.crossover(individual_2)

        # crossover with individual type 4 should fail
        self.assertTrue(fail)
        self.assertIsNone(new_ind_1)
        self.assertIsNone(new_ind_2)

    def test_crossover_same_individual(self):
        new_ind_1, new_ind_2, fail = self._individual_l2.crossover(self._individual_l2)

        self._assert_individual(new_ind_1, complexity=8,
                                hash=-5.513419727757863e-64,
                                value="(root (cos (* (* -1.912 -9.178) 3.113)))",
                                formal="cos((((-1.912) .* (-9.178)) .* 3.113))")

        self._assert_individual(new_ind_2, complexity=18,
                                hash=1.0176840735245977e-58,
                                value="(root (cos (* (+ (+ (* -1.912 -9.178) (cos S0)) (cos S0)) 3.113)))",
                                formal="cos((((((-1.912) .* (-9.178)) + cos(S0)) + cos(S0)) .* 3.113))")

    def test_crossover_different_levels_2_3(self):
        # self._engine.rand('seed', 40.0, nargout=0)
        new_ind_1, new_ind_2, fail = self._individual_l2.crossover(self._individual_l3)

        self.assertFalse(fail)

        self._assert_individual(new_ind_1, complexity=8,
                                hash=-9.469742614799921e-82,
                                value="(root (cos (* (- -8.815 -3.902) 3.113)))",
                                formal="cos((((-8.815) - (-3.902)) .* 3.113))")

        self._assert_individual(new_ind_2, complexity=27,
                                hash=1.1086575260573593e-164,
                                value="(root (log (/ (* (sin 4.37) (+ (* -1.912 -9.178) (cos S0))) (log (+ 2.025 -8.685)))))",
                                formal="my_log((my_div((sin(4.37) .* (((-1.912) .* (-9.178)) + cos(S0))),my_log((2.025 + (-8.685))))))")

        # make another to crossover in order to check randomness
        new_ind_1, new_ind_2, fail = self._individual_l2.crossover(self._individual_l3)

        self.assertFalse(fail)

        self._assert_individual(new_ind_1, complexity=8,
                                hash=1.4944726960633078e+183,
                                value="(root (log (+ 2.025 -8.685)))",
                                formal="my_log((2.025 + (-8.685)))")

        self._assert_individual(new_ind_2, complexity=27,
                                hash=-2.8342820253446463e-170,
                                value="(root (log (/ (* (sin 4.37) (- -8.815 -3.902)) (cos (* (+ (* -1.912 -9.178) (cos S0)) 3.113)))))",
                                formal="my_log((my_div((sin(4.37) .* ((-8.815) - (-3.902))),cos(((((-1.912) .* (-9.178)) + cos(S0)) .* 3.113)))))")

    def test_crossover_different_levels_0_3(self):
        # self._engine.rand('seed', 40.0, nargout=0)
        new_ind_1, new_ind_2, fail = self._individual_l0.crossover(self._individual_l3)

        self.assertFalse(fail)

        self._assert_individual(new_ind_1, complexity=3,
                                hash=1.4944726960633078e+183,
                                value="(root (- -8.815 -3.902))",
                                formal="((-8.815) - (-3.902))")

        self._assert_individual(new_ind_2, complexity=23,
                                hash=-1.2921173740151353e-34,
                                value="(root (log (/ (* (sin 4.37) (cos 5.046)) (log (+ 2.025 -8.685)))))",
                                formal="my_log((my_div((sin(4.37) .* cos(5.046)),my_log((2.025 + (-8.685))))))")

    def test_crossover_different_levels_0_4(self):
        # self._engine.rand('seed', 40.0, nargout=0)
        new_ind_1, new_ind_2, fail = self._individual_l0.crossover(self._individual_l4)

        # crossover with individual type 4 should fail
        self.assertTrue(fail)
        self.assertIsNone(new_ind_1)
        self.assertIsNone(new_ind_2)

    def test_mutate_remove_subtree_and_replace(self):
        # self._engine.rand('seed', 40.0, nargout=0)
        new_ind, fail = self._individual_l3.mutate(Individual.MUTATION_REMOVE_SUBTREE_AND_REPLACE)

        self.assertFalse(fail)
        self._assert_individual(new_ind, complexity=143,
                                hash=-1.3367784216959267e-151,
                                value="(root (log (/ (* (+ (/ (cos -3.0973) (exp (log (* (* -1.3423 (tanh (log -3.5094))) (+ (/ (/ (* -9.1213 (cos (exp S0))) (sin (exp (+ S0 1.7471)))) (- 5.0161 (sin (log S0)))) (- (cos (* (+ (sin S0) 6.2042) S0)) -9.4159)))))) (log (* (- (tanh -8.5969) S0) (/ (exp (/ 8.2118 S0)) (* (* S0 (* (cos (sin (log (exp -3.2288)))) S0)) 0.0290))))) (- -8.815 -3.902)) (log (+ 2.025 -8.685)))))",
                                formal="my_log((my_div((((my_div(cos((-3.0973)),exp(my_log((((-1.3423) .* tanh(my_log((-3.5094)))) .* ((my_div((my_div(((-9.1213) .* cos(exp(S0))),sin(exp((S0 + 1.7471))))),(5.0161 - sin(my_log(S0))))) + (cos(((sin(S0) + 6.2042) .* S0)) - (-9.4159)))))))) + my_log(((tanh((-8.5969)) - S0) .* (my_div(exp((my_div(8.2118,S0))),((S0 .* (cos(sin(my_log(exp((-3.2288))))) .* S0)) .* 0.0290)))))) .* ((-8.815) - (-3.902))),my_log((2.025 + (-8.685))))))")

        # do a second mutation
        new_ind, fail = self._individual_l3.mutate(Individual.MUTATION_REMOVE_SUBTREE_AND_REPLACE)

        self.assertFalse(fail)
        self._assert_individual(new_ind, complexity=83,
                                hash=-3.1357260586196107e+180,
                                value="(root (log (/ (* (sin 4.37) (- -8.815 -3.902)) (tanh (/ (/ -5.0573 (- S0 (/ (cos (log 4.7410)) (exp (/ (log -8.6795) (log (/ (+ 1.4783 (log (+ 2.3213 S0))) (tanh (- (sin 3.7830) (+ -7.5027 3.9792)))))))))) (/ 2.2245 (exp 8.8633)))))))",
                                formal="my_log((my_div((sin(4.37) .* ((-8.815) - (-3.902))),tanh((my_div((my_div((-5.0573),(S0 - (my_div(cos(my_log(4.7410)),exp((my_div(my_log((-8.6795)),my_log((my_div((1.4783 + my_log((2.3213 + S0))),tanh((sin(3.7830) - ((-7.5027) + 3.9792)))))))))))))),(my_div(2.2245,exp(8.8633)))))))))")

    def test_mutate_reparametrization(self):
        # self._engine.rand('seed', 40.0, nargout=0)
        new_ind, fail = self._individual_l3.mutate(Individual.MUTATION_REPARAMETRIZATION)

        self.assertFalse(fail)
        self._assert_individual(new_ind, complexity=22,
                                hash=14269175.128717355,
                                value="(root (log (/ (* (sin 0.3271) (- -1.6130 -9.6837)) (log (+ 6.0366 -3.0632)))))",
                                formal="my_log((my_div((sin(0.3271) .* ((-1.6130) - (-9.6837))),my_log((6.0366 + (-3.0632))))))")

        # do a second mutation
        new_ind, fail = self._individual_l3.mutate(Individual.MUTATION_REPARAMETRIZATION)

        self.assertFalse(fail)
        self._assert_individual(new_ind, complexity=22,
                                hash=-1.116096220690224e+75,
                                value="(root (log (/ (* (sin -2.6118) (- 2.7746 -7.5323)) (log (+ 5.4023 -3.0973)))))",
                                formal="my_log((my_div((sin((-2.6118)) .* (2.7746 - (-7.5323))),my_log((5.4023 + (-3.0973))))))")

    def test_mutate_hoist(self):
        new_ind, fail = self._individual_l3.mutate(Individual.MUTATION_HOIST)

        self.assertFalse(fail)
        self._assert_individual(new_ind, complexity=17,
                                hash=2.066009957759577e+180,
                                value="(root (/ (* (sin 4.37) (- -8.815 -3.902)) (log (+ 2.025 -8.685))))",
                                formal="(my_div((sin(4.37) .* ((-8.815) - (-3.902))),my_log((2.025 + (-8.685)))))")

        # do a second mutation
        new_ind, fail = self._individual_l3.mutate(Individual.MUTATION_HOIST)

        self.assertFalse(fail)
        self._assert_individual(new_ind, complexity=4,
                                hash=1.4944726960633078e+183,
                                value="(root (sin 4.37))",
                                formal="sin(4.37)")

    def test_mutate_shrink(self):
        # self._engine.rand('seed', 40.0, nargout=0)
        new_ind, fail = self._individual_l3.mutate(Individual.MUTATION_SHRINK)

        self.assertFalse(fail)
        self._assert_individual(new_ind, complexity=19,
                                hash=-2.277899705381213e+222,
                                value="(root (log (/ (* -9.6837 (- -8.815 -3.902)) (log (+ 2.025 -8.685)))))",
                                formal="my_log((my_div(((-9.6837) .* ((-8.815) - (-3.902))),my_log((2.025 + (-8.685))))))")

        # do a second mutation
        new_ind, fail = self._individual_l3.mutate(Individual.MUTATION_SHRINK)

        self.assertFalse(fail)
        self._assert_individual(new_ind, complexity=15,
                                hash=1.2070346203022018e+173,
                                value="(root (log (/ (* (sin 4.37) (- -8.815 -3.902)) -2.6118)))",
                                formal="my_log((my_div((sin(4.37) .* ((-8.815) - (-3.902))),(-2.6118))))")

    def test_mutate_random_choice(self):
        # mutate random: 4
        new_ind, fail = self._individual_l3.mutate()
        self.assertFalse(fail)
        self._assert_individual(new_ind, complexity=8,
                                hash=1.2070346203022018e+173,
                                value="(root (log (+ 2.025 -8.685)))",
                                formal="my_log((2.025 + (-8.685)))")

        # mutate random: 1
        new_ind, fail = self._individual_l3.mutate()
        self.assertFalse(fail)
        self._assert_individual(new_ind, complexity=22,
                                hash=-9.739328993463583e+261,
                                value="(root (log (/ (* (sin -2.6118) (- 2.7746 -7.5323)) (log (+ 5.4023 -3.0973)))))",
                                formal="my_log((my_div((sin((-2.6118)) .* (2.7746 - (-7.5323))),my_log((5.4023 + (-3.0973))))))")

        # mutate random: 2
        new_ind, fail = self._individual_l3.mutate()
        self.assertFalse(fail)
        self._assert_individual(new_ind, complexity=8,
                                hash=1.5210419679169233e+36,
                                value="(root (log (+ 2.025 -8.685)))",
                                formal="my_log((2.025 + (-8.685)))")

    def test_sensor_list(self):
        # save and restore original configuration
        with saved(Config.get_instance()):
            Config.get_instance().set("POPULATION", "sensor_list", "2,4,6,8,10,15")
            Config.get_instance().set("POPULATION", "sensors", "6")
            Config.get_instance().set("POPULATION", "sensor_spec", "true")
            Config.get_instance().set("POPULATION", "sensor_prob", "1.0")

            # test generate and mutate using sensor list
            individual = Individual()
            individual.generate(3)
            self.assertEqual(individual.get_value(), '(root (sin (/ (+ (exp S6) (cos S10)) (/ (log S10) (log S4)))))')

            individual.generate(3)
            self.assertEqual(individual.get_value(), '(root (exp (* (- (tanh S6) (tanh S10)) (- (/ S6 S6) (/ S6 S4)))))')

            new_ind, fail = self._individual_l2.mutate(Individual.MUTATION_REMOVE_SUBTREE_AND_REPLACE)
            self.assertEqual(individual.get_value(), '(root (exp (* (- (tanh S6) (tanh S10)) (- (/ S6 S6) (/ S6 S4)))))')

            new_ind, fail = self._individual_l2.mutate(Individual.MUTATION_REMOVE_SUBTREE_AND_REPLACE)
            self.assertEqual(individual.get_value(), '(root (exp (* (- (tanh S6) (tanh S10)) (- (/ S6 S6) (/ S6 S4)))))')

            new_ind, fail = self._individual_l2.mutate(Individual.MUTATION_SHRINK)
            self.assertEqual(individual.get_value(), '(root (exp (* (- (tanh S6) (tanh S10)) (- (/ S6 S6) (/ S6 S4)))))')

            new_ind, fail = self._individual_l2.mutate(Individual.MUTATION_SHRINK)
            self.assertEqual(individual.get_value(), '(root (exp (* (- (tanh S6) (tanh S10)) (- (/ S6 S6) (/ S6 S4)))))')

    def _assert_individual(self, individual, value, hash, formal, complexity):
        self.assertEquals(individual.get_value(), value)
        self.assertEquals(individual.get_type(), 'tree')
        self.assertEquals(len(individual.get_cost_history()), 0)
        self.assertEquals(individual.get_evaluation_time(), 0.0)
        self.assertEquals(individual.get_appearences(), 1)
        # self.assertEquals(individual.get_hash(), hash)
        self.assertEquals(individual.get_formal(), formal)
        self.assertEquals(individual.get_complexity(), complexity)
