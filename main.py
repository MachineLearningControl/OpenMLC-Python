#!/usr/bin/python2.7
import matlab.engine


def main():
    eng = matlab.engine.start_matlab()
    # Add path
    eng.addpath("./matlab_code")
    eng.addpath("./matlab_code/MLC_tools")
    eng.addpath("./matlab_code/MLC_tools/Demo")

    mlc = eng.MLC2()
    eng.go(mlc, 3, 2)
    raw_input("Press Enter to continue...")


if __name__ == "__main__":
    main()