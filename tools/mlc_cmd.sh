#!/bin/bash

# Put the absolute path where the 'shared' python was installed
export PYTHONPATH=$PYTHONPATH:../
MLCPYTHON=/opt/mlc-python-2.7.11/bin/mlc_python

# Run MLC Comand tool
$MLCPYTHON ../MLC/mlc_cmd.py $@
