#!/usr/bin/python2.7
import matlab.engine

from MLC3 import MLC3


def main():
    mlc3 = MLC3("")
    mlc3.go(3,4)
    raw_input("Press Enter to continue...")

if __name__ == "__main__":
    main()
