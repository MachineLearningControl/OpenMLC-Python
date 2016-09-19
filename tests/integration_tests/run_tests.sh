#!/bin/bash

# Put the absolute path where the 'shared' python was installed
export PYTHONPATH=$PYTHONPATH:$HOME/workspace_/mlc_v3
NOSETESTS=/opt/mlc-python-2.7.11/bin/python

# Run Integration tests
$NOSETESTS integration_tests.py $@
