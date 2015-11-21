#!/usr/bin/python2.7
import matlab.engine
import numpy as np

eng = matlab.engine.start_matlab()
eng.addpath("./matlab_code")
eng.addpath("./matlab_code/MLC_tools")
eng.addpath("./matlab_code/MLC_tools/Demo")
mlc = eng.MLC2()
eng.workspace["mlc"] = mlc
param = eng.eval("mlc.parameters")
