#!/bin/bash

# Put the absolute path where the 'shared' python was installed
NOSETESTS=/opt/mlc-python-2.7.11/bin/mlc_nosetests
$NOSETESTS --with-coverage --cover-package=MLC -v ./mlc/