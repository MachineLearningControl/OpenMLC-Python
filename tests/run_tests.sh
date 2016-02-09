#!/bin/bash

# Put the absolute path where the 'shared' python was installed
PYTHON_DIR=/usr/local/python-2.7.10

# ConfigTest
echo "Proceed to run ConfigTest"
$PYTHON_DIR/bin/nosetests -v ConfigTest/ConfigTest.py 

# IntegrationTest1
echo "Proceed to run IntegrationTest1"
cd IntegrationTest1
$PYTHON_DIR/bin/nosetests -v IntegrationTest1.py





