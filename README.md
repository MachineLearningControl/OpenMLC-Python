<p align="center">
  <img src="https://raw.githubusercontent.com/Ezetowers/MLC/master/MLC/GUI/images/mlc_icon.png" width="350"/>
</p>

# MLC (Machine Learning Control)
[![Build Status](https://travis-ci.org/MachineLearningControl/OpenMLC-Python.svg?branch=master)](https://travis-ci.org/MachineLearningControl/OpenMLC-Python)


## Table of Contents
1. [Abstract](#abstract)
2. [Project Structure](#project-structure)
3. [Installation](#installation)  
3.1 [Python Engine and MLC Python](#python-engine-and-mlc-python)    
3.2 [MATLAB versions supported](#matlab-versions-supported)    
3.3 [MLC Python](#mlc-python)  
4. [Configuration](#configuration)  
4.1 [Parameters](#parameters)  
4.2 [Logging](#logging)
5. [How To Run MLC](#how-to-run-mlc)
6. [Testing](#testing)

## Abstract
MLC is a framework designed to solve chaotic problems related with the field of fluodynamics.  
The input of the system it's an script which models a problem. This problem is solved evolving populations, which are groups of non related individuals, through the use of a set of genetic algorithms. Every individual is modeled as a linear combination of diffenrent operators (-,+, sin, cos, exp, etc.).

## Project Structure
* **[MLC](MLC)**: The files inside this path are related with the Python code use
* **[conf](conf)**: Directory where the differents config files of the project are stored. For the moment, the app read config files from this directory, so be sure to persist your desired configuration within them.
* **[doc](doc)**: Diagrams, user manuals, developer manuals and other stuff can be found inside this directory.
* **[matlab_code](matlab_code)**: MATLAB&reg; files of the last version of MLC. Some of the files were modified to access properties and functions on Python scripts. The most likely scenario is that this code cannot be ran on MATLAB&reg; as it is right now.
* **[tests](tests)**: Tests related with the project (functional, unit tests, etc.) can be found here.
* **[tools](tools)**: Additional scripts and files are stored in this directory.

## Installation

### Python Engine and MLC Python
Previous versions of MLC ran in MATLAB&reg;. The last version is being ported to Python, so the actual implementation is a hybrid between this two languages.  

#### MATLAB versions supported
The main program starts running in Python and make calls to MATLAB&reg; when it is needed. To be able to run MATLAB&reg; code inside Python, the module [Python Engine](http://www.mathworks.com/help/matlab/matlab-engine-for-python.html) is used.  
Python Engine is available in versions of MATLAB&reg; 2014b and ahead.

#### MLC Python
In order to succesfully run the [Python Engine Module](http://www.mathworks.com/help/matlab/matlab-engine-for-python.html), Python must compiled in a special way. For more details, the [Python Engine Documentation](http://www.mathworks.com/help/matlab/matlab_external/system-requirements-for-matlab-engine-for-python.html) can be inspected.  
A pre-compiled version of Python can be found in the following [link](https://drive.google.com/file/d/0B1yBBZBneUgZb2gwb1hOTDF4Tjg/view). The file it's a .deb package and it was succesfully installed in the following operating systems:
* Linux Mint 18
* Ubuntu 16.04
* Debian 8 (Jessie)


To avoid difficulties, an [installer](tools/installer/install.sh) can be found inside the directory tools of the present project. The installer expects as input the absolute path of the already mentioned .deb package and the absolute path of the MATLAB installed in the system. **It must be executed with root priviligies**. The usage of this script and a brief example with the output of the installer are printed to show the installation details:

```
root@hostname:/path/to/MLC_Project/tools/installer# ./install.sh -h
############################
#     MLC Installer        #
############################
Saving log to /tmp/MLC_install_log_2016-02-22_002224.log
MLC Installer. Available options:
  -h: Show this help
  -u: uninstall MLC
  -p <file>: MLC's deb file. Mandatory!
  -d <dir>: Absolute path where MATLAB is installed in the system. Mandatory!


root@hostname:/path/to/MLC_Project/tools/installer# ./install.sh -p /tmp/mlc-python_0.1_amd64.deb -d /path/to/MATLAB
############################
#     MLC Installer        #
############################
Saving log to /tmp/MLC_install_log_2016-02-22_001931.log
Searching for previous version of MLC
Proceed to install MLC Python.
Selecting previously unselected package mlc-python.
(Reading database ... 212725 files and directories currently installed.)
Preparing to unpack /tmp/mlc-python_0.1_amd64.deb ...
Unpacking mlc-python (0.1) ...
Setting up mlc-python (0.1) ...
MLC Python succesfully installed
```

The new Python is installed in the directory **/opt/mlc-python-2.7.11**. This version of Python must be executed by the following scripts:
* **/opt/mlc-python-2.7.11/bin/mlc_python**: Script that run the desired Python binary. All the python files within this project must be executed with the following script.
* **/opt/mlc-python-2.7.11/bin/mlc_pip**: All new Python dependencies that would like to be installed, must be installed with this version of pip. In other case, the dependencies must be built and installed with the mlc_python script.
* **/opt/mlc-python-2.7.11/bin/mlc_nosetests**: The project tests must be executed with the following script.

## Configuration
*All the configuration files of the application can be found in the [conf directory](conf). **MLC consumes them directly
from there,*** so beware of make all your desired changes in files inside this folder.

### Parameters
All the parameters associated with the MLC must be set in the file [configuration.conf](conf/configuration.conf).  
A short description of every parameter and also the valid values supported can be found in the [Wiki](https://github.com/Ezetowers/taller3_final/wiki/Configuration-Parameters).

### Logging
MLC provides log facilities based on the [Python Logging Module](https://docs.python.org/2/library/logging.html). The   application consumes the file [logging.conf](conf/logging.conf) in order to retrieve the different log configuration   available. The present available log configuration are the following:
* **console**: Redirects the output of the MLC to standard output. The log-level is set to *DEBUG*.
* **file**: Redirects the output of the MLC to a file in the filesystem. As it is configured at the moment, the  
content is stored in */tmp/mlc.log*.
* **testing**: It doesn't log anything to console neither a file. It is used in tests to avoid unnecessary outputs.   
* **root**: Default Python Logging Module log configuration. It is configured as console mode.

The log configuration can be changed modifying the parameter **logmode** in the **LOGGING** section of the  
[config file](conf/configuration.conf). Take care to put a valid value in order to avoid problems running the application.

## How to Run MLC
For the moment, MLC does not receive any parameters to run. As it was said in previous sections, it retrieves the  
desired configuration from the [configuration file](conf/configuration.conf) and redirects the output obeying the rules dictated by the [logging config file](conf/logging.conf).  
So, in order to run the application you must enter to the root path of the repository and run the main.py file as  
follows:

```
user@hostname:/path/to/MLC_Project$ ./opt/mlc-python-2.7.11/bin/mlc_python main.py
```

## Testing
By default, tests (Unit tests, Integration tests, Smoke tests, etc.) are placed in the folder [test](tests).  
The tests are designed using the [Python Unittest Module](https://docs.python.org/2/library/unittest.html). To avoid
problems related with the output and the way the modules are imported,
[the nose app](http://pythontesting.net/framework/nose/nose-introduction/) is used.  
Nevertheless, if you don't want to have take a look to the Python Testing links above, [a script](tests/run_tests.sh) is provided to run all the tests designed to this moment.  
To run all the tests, enter to the [tests](tests) folder and execute the script as it is show:
```
user@hostname:/path/to/MLC_Project/tests$ ./run_tests.sh
```
In order to enable test coverage coverage python module should be installed:
```
user@hostname:/opt/mlc-python-2.7.11/bin/mlc_pip install coverage
```
