#!/bin/bash

# Put the absolute path where the 'shared' python was installed
export PYTHONPATH=$PYTHONPATH:$(dirname "$0")/../
MLCPYTHON=python

# Run MLC Comand tool
$MLCPYTHON $(dirname "$0")/mlc_cmd/mlc_cmd.py $@
