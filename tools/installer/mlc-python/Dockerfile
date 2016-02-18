# Set the base image
FROM ubuntu:14.04

# Update the current system
RUN apt-get update && apt-get upgrade

# Install packages
RUN apt-get install ssh gcc wget xz-utils make vim -y

# Download python 2.7.11
WORKDIR /tmp
RUN wget -q https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tar.xz
RUN tar xJvf Python-2.7.11.tar.xz
# For more information about the compilation of the Python: http://www.mathworks.com/help/matlab/matlab_external/system-requirements-for-matlab-engine-for-python.html?requestedDomain=www.mathworks.com
RUN cd Python-2.7.11 && ./configure --enable-shared --enable-unicode=ucs4 --prefix=/opt/mlc-python-2.7.11 
RUN cd Python-2.7.11 && make && make install

# Install Python Setuptools
RUN wget -q https://pypi.python.org/packages/source/s/setuptools/setuptools-20.1.1.tar.gz#md5=10a0f4feb9f2ea99acf634c8d7136d6d
RUN tar xzvf setuptools-20.1.1.tar.gz
RUN cd setuptools-20.1.1 && /opt/mlc-python-2.7.11/bin/python2.7 setup.py build && /opt/mlc-python-2.7.11/bin/python2.7 setup.py install 

# Idem with pip
RUN wget -q https://pypi.python.org/packages/source/p/pip/pip-8.0.2.tar.gz#md5=3a73c4188f8dbad6a1e6f6d44d117eeb
RUN tar xzvf pip-8.0.2.tar.gz
RUN cd pip-8.0.2 && /opt/mlc-python-2.7.11/bin/python2.7 setup.py build && /opt/mlc-python-2.7.11/bin/python2.7 setup.py install 


