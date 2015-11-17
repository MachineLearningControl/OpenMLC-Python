import matlab.engine


class Application(object):
    def __init__(self, eng):
        self._eng = eng
        self._mlc2 = eng.eval("wmlc")

    def go(self, amount_gen, amount_graphics):
        """
        GO start MLC2 problem solving (MLC2 Toolbox)
        OBJ.GO(N) creates (if necessary) the population, evaluate and evolve it
            until N evaluated generations are obtained.
        OBJ.GO(N,1) additionaly displays the best individual if implemented in
            the evaluation function at the end of each generation evaluation
        OBJ.GO(N,2) additionaly displays the convergence graph at the end of
            each generation evaluation
        """
        self._eng.go(self._mlc2, amount_gen, amount_graphics)



