import os
import re
import argparse
from tabulate import tabulate


def usage():
    print """
./MATLAB_functions_finder.py [-d|MLC_dir] OPTIONS
    -d|--MLC_dir:                Absolute or Relative Path to the directory containing the Python implementation of MLC. Mandatory!!
    -a|--show_all:               Show all the functions matched without any filter
    -n|--no_getters_and_setters: Don't show getters and setters calls
    -e|--no_eval:                Don't show getters and setters and eval calls 
"""


def retrieve_python_files(mlc_dir):
    list = []
    files_regex = re.compile("^.*py$")
    no_init = re.compile("^(.(?!(__init__)))*$")

    for root, directories, filenames in os.walk(mlc_dir):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            if files_regex.match(file_path) and no_init.match(file_path):
                list.append(file_path)

    return list


def retrieve_methods():
    engine_regex = re.compile("^.*(self\._eng\..*)$")
    methods = []

    for python_file in retrieve_python_files(mlc_dir):
        f = open(python_file, "r")
        i = 0
        for line in f:
            i += 1
            r = engine_regex.match(line)
            if r:
                methods.append([python_file, i, r.group(1)])

    return methods


def draw_methods(methods, blacklist=None):
    # First, show all the methods
    columns = ["File", "Line", "Method"]
    rows = []

    for method in methods:
        word_found = False
        if blacklist is not None:
            for word in blacklist:
                if method[2].find(word) != -1:
                    word_found = True
                    break
        if not word_found:
            rows.append([method[0], method[1], method[2]])

    print tabulate(rows, columns, tablefmt="fancy_grid")

# Parse program arguments
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--MLC_dir', required=True)
parser.add_argument('-a', '--show_all', required=False, action='store_true')
parser.add_argument('-g', '--no_getters_and_setters', required=False, action='store_true')
parser.add_argument('-e', '--no_eval', required=False, action='store_true')
args = parser.parse_args()
args = vars(args)

mlc_dir = args['MLC_dir']
show_all = args['show_all']
no_getters_and_setters = args['no_getters_and_setters']
no_eval = args['no_eval']
nothing_to_show = False

if not show_all and \
        not no_getters_and_setters and \
        not no_eval:
    nothing_to_show = True

# If the path is not valid,
if not os.path.isdir(mlc_dir):
    print "MLC_Dir must be a valid path. Aborting program."
    usage()
    exit(-1)

# Load in a dict the different posibilities
to_draw = {}
show_all_string = "Draw all methods"
to_draw[show_all_string] = (draw_methods,
                              None,
                              nothing_to_show or show_all)

no_get_and_set_string = "Draw all methods filtering getters and setters"
to_draw[no_get_and_set_string] = (draw_methods,
                                  ["get_", "set_"],
                                  nothing_to_show or no_getters_and_setters)

no_eval_string = "Draw all methods filtering getters and setters and eval calls"
to_draw[no_eval_string] = (draw_methods,
                           ["get_", "set_", "eval"],
                           nothing_to_show or no_eval)

# Show the results
methods = retrieve_methods()
for key, value in to_draw.iteritems():
    if value[2]:
        print "\n\n"
        print key
        value[0](methods, value[1])