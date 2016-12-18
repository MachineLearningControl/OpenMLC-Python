# Set the base image
FROM ubuntu:16.04

# Update the current system
RUN apt-get update && apt-get upgrade -y

# Install packages
RUN apt-get install cmake \
                    liblapack-dev \
                    gfortran \
                    libxml2-dev \
                    libxslt1-dev \
                    libshiboken-dev \
                    ruby-dev \
                    libqt4-dev \
                    tcl-dev \
                    tcl \
                    tk \
                    tk-dev \
                    ssh \
                    gcc \
                    g++ \
                    wget \
                    xz-utils \
                    make \
                    vim \
                    libssl-dev \
                    libsqlite3-dev \
                    qt5-default \
                    qt5-qmake \
                    qtbase5-dev \
                    git \
                    -y

# Download python 2.7.11
WORKDIR /tmp
# For more information about the compilation of the Python: http://www.mathworks.com/help/matlab/matlab_external/system-requirements-for-matlab-engine-for-python.html?requestedDomain=www.mathworks.com
RUN wget -q https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tar.xz && \
    tar xJvf Python-2.7.11.tar.xz && \
    cd Python-2.7.11 && ./configure --enable-shared --enable-unicode=ucs4 --prefix=/opt/mlc-python-2.7.11 && make && make install

# Create .sh who will load the desired enviroment to run python within it
RUN echo '#!/bin/bash' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo "" >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo "# Add the correct path to the LD_LIBRARY_PATH enviroment variable" >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo 'export LD_LIBRARY_PATH=/opt/mlc-python-2.7.11/lib:$LD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo 'PYTHON="/opt/mlc-python-2.7.11/bin/python2.7"' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo "" >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo "# Run the dynamically compiled python for matlab" >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo 'if [ "$#" -ne 0 ]; then' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo '        $PYTHON $@' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo "else" >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo '        $PYTHON' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo "fi" >> /opt/mlc-python-2.7.11/bin/mlc_python && \
chmod 755 /opt/mlc-python-2.7.11/bin/mlc_python



# Install Python Setuptools
RUN wget -q https://pypi.python.org/packages/source/s/setuptools/setuptools-20.1.1.tar.gz#md5=10a0f4feb9f2ea99acf634c8d7136d6d && \
    tar xzvf setuptools-20.1.1.tar.gz && \
    cd setuptools-20.1.1 && chmod 755 /opt/mlc-python-2.7.11/bin/mlc_python; sync ; /opt/mlc-python-2.7.11/bin/mlc_python setup.py build && /opt/mlc-python-2.7.11/bin/mlc_python setup.py install


# Idem with pip
RUN wget -q https://pypi.python.org/packages/source/p/pip/pip-8.0.2.tar.gz#md5=3a73c4188f8dbad6a1e6f6d44d117eeb && \
    tar xzvf pip-8.0.2.tar.gz && \
    cd pip-8.0.2 && /opt/mlc-python-2.7.11/bin/mlc_python setup.py build && /opt/mlc-python-2.7.11/bin/mlc_python setup.py install 

# Create .sh who will load the desired enviroment to run pip within it
RUN echo '#!/bin/bash' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo "" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo "# Add the correct path to the LD_LIBRARY_PATH enviroment variable" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo 'export LD_LIBRARY_PATH=/opt/mlc-python-2.7.11/lib:$LD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo 'PIP="/opt/mlc-python-2.7.11/bin/pip2.7"' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo "" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo "# Run the dynamically compiled pip" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo 'if [ "$#" -ne 0 ]; then' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo '        $PIP $@' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo "else" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo '        $PIP' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo "fi" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    chmod 755  /opt/mlc-python-2.7.11/bin/mlc_pip



# Install mlc dependencies
# Create .sh who will load the desired enviroment to run nosetests within it
RUN chmod 755 /opt/mlc-python-2.7.11/bin/mlc_pip; sync; /opt/mlc-python-2.7.11/bin/mlc_pip install flask requests pyserial nose matplotlib pyside numpy scipy pyyaml && echo '#!/bin/bash' > /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo "" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo "# Add the correct path to the LD_LIBRARY_PATH enviroment variable" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo 'export LD_LIBRARY_PATH=/opt/mlc-python-2.7.11/lib:$LD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo 'NOSETESTS="/opt/mlc-python-2.7.11/bin/nosetests"' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo "" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo "# Run the dynamically compiled nosetests" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo 'if [ "$#" -ne 0 ]; then' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo '        $NOSETESTS $@' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo "else" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo '        $NOSETESTS' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo "fi" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    chmod 755 /opt/mlc-python-2.7.11/bin/mlc_nosetests

# Add PyQt5 Support
RUN wget https://sourceforge.net/projects/pyqt/files/sip/sip-4.18.1/sip-4.18.1.tar.gz && \
    tar xzvf sip-4.18.1.tar.gz && \
    cd sip-4.18.1 && \
    /opt/mlc-python-2.7.11/bin/mlc_python configure.py && \
    make && make install

RUN wget https://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.7/PyQt5_gpl-5.7.tar.gz && \
    tar xzvf PyQt5_gpl-5.7.tar.gz && \
    cd PyQt5_gpl-5.7 && \
    /opt/mlc-python-2.7.11/bin/mlc_python configure.py --confirm-license --sip /opt/mlc-python-2.7.11/bin/sip && \
    make && make install

# Create .sh who will load the desired enviroment to run pip within it
RUN echo '#!/bin/bash' >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo "" >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo "# Add the correct path to the LD_LIBRARY_PATH enviroment variable" >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo 'export LD_LIBRARY_PATH=/opt/mlc-python-2.7.11/lib:$LD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo 'PYUIC="/opt/mlc-python-2.7.11/bin/pyuic5"' >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo "" >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo "# Run the dynamically compiled pip" >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo 'if [ "$#" -ne 0 ]; then' >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo '        $PYUIC $@' >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo "else" >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo '        $PYUIC' >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo "fi" >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5  && \
    chmod 755 /opt/mlc-python-2.7.11/bin/mlc_pyuic5

# Add PyQt5 Charts
RUN git clone git://code.qt.io/qt/qtcharts.git && \
    cd qtcharts && \
    git checkout release-2.1.0 && \
    qmake && make && make install

RUN wget https://sourceforge.net/projects/pyqt/files/PyQtChart/PyQtChart-5.7/PyQtChart_gpl-5.7.tar.gz && \
    tar xzvf PyQtChart_gpl-5.7.tar.gz && \
    cd PyQtChart_gpl-5.7 && \
    /opt/mlc-python-2.7.11/bin/mlc_python configure.py --qtchart-version=2.1.0 --sip /opt/mlc-python-2.7.11/bin/sip && \
    make && make install

# Install fpm and create .deb package
RUN gem install fpm && fpm -s dir -t deb -v 0.4 -n mlc-python /opt/mlc-python-2.7.11
