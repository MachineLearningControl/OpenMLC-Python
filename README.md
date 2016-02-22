# MLC (Machine Learning Control)

## Table of Contents
1. [Abstract](#Abstract)
2. [Project Structure](#Project Structure)
3. [Installation](#Installation)  
3.1 [Python Engine and MLC Python](#Python Engine and MLC Python)  
3.1.1 [MATLAB versions supported](#MATLAB versions supported)


## Abstract
MLC is a framework designed to solve chaotic problems related with the field of fluodynamics.  
The input of the system it's an script which model a problem. This problem is solved evolving populations, which are groups of non related individuals, through the use of a set of genetic algorithms. Every individual is modeled as a linear combination of diffenrent operators (-,+, sin, cos, exp, etc.).

## Project Structure
* **MLC**: The files inside this path are related with the Python code use
* **conf**: Directory where the differents config files of the project are stored. For the moment, the app read config files from this directory, so be sure to persist your desired configuration within them.
* **doc**: Diagrams, user manuals, developer manuals and other stuff can be found inside this directory.
* **matlab_code_**: MATLAB&reg; files of the last version of MLC. Some of the files were modified to access properties and functions on Python scripts. The most likely scenario is that this code cannot be ran on MATLAB&reg; as it is right now.
* **tests**: Tests related with the project (functional, unit tests, etc.) can be found here.
* **tools**: Additional scripts and files are stored in this directory. 

## Installation

### Python Engine and MLC Python
Previous versions of MLC ran in MATLAB&reg;. The last version is being ported to Python, so the actual implementation is a hybrid between this two languages.  

#### MATLAB versions supported
The main program starts running in Python and make calls to MATLAB&reg; when it is needed. To be able to run MATLAB&reg; code inside Python, the module [Python Engine](http://www.mathworks.com/help/matlab/matlab-engine-for-python.html) is used.  
Python Engine is available in versions of MATLAB&reg; 2014b and ahead.

#### MLC Python
In order to succesfully run the [Python Engine Module](http://www.mathworks.com/help/matlab/matlab-engine-for-python.html), Python must compiled in a special way. For more details, the [Python Engine Documentation](http://www.mathworks.com/help/matlab/matlab_external/system-requirements-for-matlab-engine-for-python.html) can be inspected.  
A pre-compiled version of Python can be found in the following [link](https://drive.google.com/file/d/0B1yBBZBneUgZNG5MbHJzUmRpYmc/view?usp=sharing). The file it's a .deb package and it was succesfully installed in the following operating systems:
* Linux Mint 17.1 
* Ubuntu 14.04
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
  -u: uninstall TFTP
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





