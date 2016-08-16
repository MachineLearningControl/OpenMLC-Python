#!/bin/bash

# Put the absolute path where the 'shared' python was installed
NOSETESTS=/opt/mlc-python-2.7.11/bin/mlc_nosetests

# IntegrationTest1
echo "Proceed to run IntegrationTest1"
cd IntegrationTest1
$NOSETESTS -v IntegrationTest1.py
