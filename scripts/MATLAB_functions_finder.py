import os
import re
from tabulate import tabulate


def retrieve_python_files():
    list = []
    files_regex = re.compile("^.*py$")
    no_init = re.compile("^(.(?!(__init__)))*$")

    for root, directories, filenames in os.walk('./MLC'):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            if files_regex.match(file_path) and no_init.match(file_path):
                list.append(file_path)

    return list


def retrieve_methods(file_list):
    engine_regex = re.compile("^.*(self\._eng\..*)$")
    methods = []

    for python_file in retrieve_python_files():
        f = open(python_file, "r")
        i = 0
        for line in f:
            i += 1
            r = engine_regex.match(line)
            if r:
                methods.append([python_file, i, r.group(1)])

    return methods


def draw_methods(methods, blacklist = None):
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


methods = retrieve_methods(retrieve_python_files())
print "Draw all methods"
draw_methods(methods)

print "Draw all methods filtering getters and setters"
blacklist = ["get_", "set_"]
draw_methods(methods, blacklist)

blacklist.append("eval")
print "Draw all methods filtering getters and setters and eval calls"
draw_methods(methods, blacklist)

