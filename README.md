# MLC (Machine Learning Control)

## Abstract
MLC is a framework designed to solve chaotic problems related with the field of fluodynamics.  
The input of the system it's an script which model a problem. This problem is solved evolving populations, which are groups of non related individuals, through the use of a set of genetic algorithms. Every individual is modeled as a linear combination of diffenrent operators (-,+, sin, cos, exp, etc.).

## Installation

### Python Engine and MLC Python
Previous versions of MLC ran in MATLAB&reg;. The last version is being ported to Python, so the actual implementation is a hybrid between this two languages.  

#### MATLAB versions supported
The main program starts running in Python and make calls to MATLAB&reg; when it is needed. To be able to run MATLAB&reg; code inside Python, the module [Python Engine](http://www.mathworks.com/help/matlab/matlab-engine-for-python.html) is used.  
Python Engine is available in versions of MATLAB&reg; 2014b and ahead. 
