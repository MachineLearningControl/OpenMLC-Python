#!/bin/bash

# Put the absolute path where the 'shared' python was installed
export PYTHONPATH=$PYTHONPATH:../../
NOSETESTS=/opt/mlc-python-3.4.7/bin/mlc_python

# Run Integration tests
$NOSETESTS integration_tests.py $@
