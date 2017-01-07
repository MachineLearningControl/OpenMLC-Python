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


def retrieve_methods(mlc_dir):
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


def draw_methods(methods, comments_dict, blacklist=None, whitelist=None):
    # First, show all the methods
    columns = ["File", "Line", "Method"]
    rows = []

    for method in methods:
        word_found = False
        if blacklist is not None:
            for black_word in blacklist:
                black_pos = method[2].find(black_word)
                if black_pos != -1:
                    # Check if the get founded is in the whitelist. In that case,
                    # don't filter the word
                    for white_word in whitelist:
                        white_pos = method[2].find(white_word)
                        if white_pos != black_pos:
                            word_found = True
                            break
        if not word_found:
            # Check if the line is in a comment or it is a comment
            if not method[1] in comments_dict[method[0]]:
                rows.append([method[0], method[1], method[2]])

    print tabulate(rows, columns, tablefmt="fancy_grid")


def get_lines_with_comments_per_file(mlc_dir):
    comments_dict = {}

    for python_file in retrieve_python_files(mlc_dir):
        f = open(python_file, "r")
        i = 0

        # Use this variable as a toggle. When -1, we are inside a multicomment
        toggle_multicomment = 1
        multicomment_regex = re.compile("^ .*\"\"\"")
        simplecomment_regex = re.compile("^ .*#")
        file_lines = []
        for line in f:
            i += 1
            # Check if multicomment
            if multicomment_regex.match(line):
                toggle_multicomment *= -1

            if toggle_multicomment == -1:
                file_lines.append(i)
                continue

            # Check if simplecomment
            if simplecomment_regex.match(line):
                file_lines.append(i)

        comments_dict[python_file] = file_lines
    return comments_dict


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

if not show_all and not no_getters_and_setters and not no_eval:
    nothing_to_show = True

# If the path is not valid,
if not os.path.isdir(mlc_dir):
    print "MLC_Dir must be a valid path. Aborting program."
    usage()
    exit(-1)

# Load in a dict the different posibilities
to_draw = {}
comments_dict = get_lines_with_comments_per_file(mlc_dir)
show_all_string = "Draw all methods"
to_draw[show_all_string] = (draw_methods,
                            None,
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
methods = retrieve_methods(mlc_dir)
for key, value in to_draw.iteritems():
    if value[3]:
        print "\n\n"
        print key
        value[0](methods, comments_dict, value[1], value[2])
