#!/bin/bash

# Put the absolute path where the 'shared' python was installed
export PYTHONPATH=$PYTHONPATH:$(dirname "$0")/../
MLCPYTHON=/opt/mlc-python-2.7.11/bin/mlc_python

# Run MLC Comand tool
$MLCPYTHON $(dirname "$0")/mlc_cmd/mlc_cmd.py $@
