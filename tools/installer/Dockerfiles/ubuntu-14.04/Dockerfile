# Set the base image
FROM ubuntu:14.04

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
                    git \
                    freeglut3 \
                    freeglut3-dev \
                    binutils-gold \
                    libglew-dev \
                    mesa-common-dev \
                    build-essential \
                    '^libxcb.*-dev' \
                    libx11-xcb-dev \
                    libglu1-mesa-dev \
                    libxrender-dev \
                    libxi-dev \
                    libxkbcommon-dev \
                    -y

# Download python 2.7.11
WORKDIR /tmp
# For more information about the compilation of the Python: http://www.mathworks.com/help/matlab/matlab_external/system-requirements-for-matlab-engine-for-python.html?requestedDomain=www.mathworks.com
RUN wget -q https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tar.xz && \
    tar xJvf Python-2.7.11.tar.xz && \
    cd Python-2.7.11 && ./configure --enable-shared --enable-unicode=ucs4 --prefix=/opt/mlc-python-2.7.11 && make && make install && \
    rm -rf /tmp/Python-2.7.11

# Create .sh who will load the desired enviroment to run python within it
RUN echo '#!/bin/bash' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
    echo 'export ROOTPATH="$(dirname "$(readlink -f "$0")")/.."' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
    echo "" >> /opt/mlc-python-2.7.11/bin/mlc_python && \
    echo "# Add the correct path to the LD_LIBRARY_PATH enviroment variable" >> /opt/mlc-python-2.7.11/bin/mlc_python && \
    echo 'export LD_LIBRARY_PATH=$ROOTPATH/lib:$LD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
    echo 'export LD_LIBRARY_PATH=$ROOTPATH/custom_libs:$LD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
    echo 'export LD_LIBRARY_PATH=$ROOTPATH/Qt-5.7.1/lib:$LD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
    echo 'PYTHON="$ROOTPATH/bin/python2.7"' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
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
    cd setuptools-20.1.1 && /opt/mlc-python-2.7.11/bin/mlc_python setup.py build && /opt/mlc-python-2.7.11/bin/mlc_python setup.py install && \
    rm -rf /tmp/setuptools-20.1.1*


# Idem with pip
RUN wget -q https://pypi.python.org/packages/source/p/pip/pip-8.0.2.tar.gz#md5=3a73c4188f8dbad6a1e6f6d44d117eeb && \
    tar xzvf pip-8.0.2.tar.gz && \
    cd pip-8.0.2 && /opt/mlc-python-2.7.11/bin/mlc_python setup.py build && /opt/mlc-python-2.7.11/bin/mlc_python setup.py install && \
    rm -rf /tmp/pip-8.0.2*

# Create .sh who will load the desired enviroment to run pip within it
RUN echo '#!/bin/bash' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo 'export ROOTPATH="$(dirname "$(readlink -f "$0")")/.."' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo "" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo "# Add the correct path to the LD_LIBRARY_PATH enviroment variable" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo 'export LD_LIBRARY_PATH=$ROOTPATH/lib:$LD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo 'export LD_LIBRARY_PATH=$ROOTPATH/custom_libs:$LD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo 'export LD_LIBRARY_PATH=$ROOTPATH/Qt-5.7.1/lib:$LD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo 'PIP="$ROOTPATH/bin/pip2.7"' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo "" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo "# Run the dynamically compiled pip" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo 'if [ "$#" -ne 0 ]; then' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo '        $PIP $@' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo "else" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo '        $PIP' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo "fi" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    chmod 755  /opt/mlc-python-2.7.11/bin/mlc_pip

# Install Qt5.7
RUN git clone git://code.qt.io/qt/qtbase.git && \
    cd qtbase && \
    git checkout 5.7 && \
    ./configure --prefix=/opt/mlc-python-2.7.11/Qt-5.7.1 -xkb-config-root /usr/share/X11/xkb -no-gtk -nomake tests -nomake examples -qt-xcb --opensource --confirm-license && \
    make -j4 && make install && \
    rm -rf /tmp/qtbase

RUN git clone git://code.qt.io/qt/qttools.git && \
    cd qttools && \
    git checkout 5.7 && \
    /opt/mlc-python-2.7.11/Qt-5.7.1/bin/qmake CONFIG+=release && make -j4 && make install && \
    rm -rf /tmp/qttools

RUN git clone git://code.qt.io/qt/qtcharts.git && \
    cd qtcharts && \
    git checkout 5.7 && \
    /opt/mlc-python-2.7.11/Qt-5.7.1/bin/qmake CONFIG+=release && make -j4 && make install && \
    rm -rf /tmp/qtcharts

RUN git clone git://code.qt.io/qt/qtdatavis3d.git && \
    cd qtdatavis3d && \
    git checkout 5.7 && \
    /opt/mlc-python-2.7.11/Qt-5.7.1/bin/qmake CONFIG+=release && make -j4 && make install && \
    rm -rf /tmp/qtdatavis3d

RUN git clone git://code.qt.io/qt/qtdeclarative.git && \
    cd qtdeclarative && \
    git checkout 5.7 && \
    /opt/mlc-python-2.7.11/Qt-5.7.1/bin/qmake CONFIG+=release && make -j4 && make install && \
    rm -rf /tmp/qtdeclarative

RUN git clone git://code.qt.io/qt/qtx11extras.git && \
    cd qtx11extras && \
    git checkout 5.7 && \
    /opt/mlc-python-2.7.11/Qt-5.7.1/bin/qmake CONFIG+=release && make -j4 && make install && \
    rm -rf /tmp/qtx11extras

RUN git clone https://github.com/mati75/qt5ct.git && \
    cd qt5ct && \
    /opt/mlc-python-2.7.11/Qt-5.7.1/bin/qmake PREFIX=/opt/mlc-python-2.7.11/qt5ct && make -j4 && make install && \
    rm -rf /tmp/qt5ct

RUN git clone git://code.qt.io/qt/qtstyleplugins.git && \
    cd qtstyleplugins && \
    /opt/mlc-python-2.7.11/Qt-5.7.1/bin/qmake && make && \
    mkdir -p /opt/mlc-python-2.7.11/Qt-5.7.1/plugins/styles && \
    cp -r ./plugins/styles/* /opt/mlc-python-2.7.11/Qt-5.7.1/plugins/styles && \
    rm -rf /tmp/qtstyleplugins

# Add PyQt5 Support
RUN wget https://sourceforge.net/projects/pyqt/files/sip/sip-4.19/sip-4.19.tar.gz && \
    tar xzvf sip-4.19.tar.gz && \
    cd sip-4.19 && \
    /opt/mlc-python-2.7.11/bin/mlc_python configure.py && \
    make -j4 && make install && \
    rm -rf /tmp/sip-4.19*

RUN wget https://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.7.1/PyQt5_gpl-5.7.1.tar.gz && \
    tar xzvf PyQt5_gpl-5.7.1.tar.gz && \
    cd PyQt5_gpl-5.7.1 && \
    /opt/mlc-python-2.7.11/bin/mlc_python configure.py --qmake /opt/mlc-python-2.7.11/Qt-5.7.1/bin/qmake --confirm-license --sip /opt/mlc-python-2.7.11/bin/sip && \
    make -j4 && make install && \
    rm -rf /tmp/PyQt5_gpl-5.7.1*

# Add PyQt5 Charts
RUN wget https://sourceforge.net/projects/pyqt/files/PyQtChart/PyQtChart-5.7.1/PyQtChart_gpl-5.7.1.tar.gz && \
    tar xzvf PyQtChart_gpl-5.7.1.tar.gz && \
    cd PyQtChart_gpl-5.7.1 && \
    /opt/mlc-python-2.7.11/bin/mlc_python configure.py --qmake /opt/mlc-python-2.7.11/Qt-5.7.1/bin/qmake --sip /opt/mlc-python-2.7.11/bin/sip && \
    make -j4 && make install && \
    rm -rf /tmp/PyQtChart_gpl-5.7.1*

RUN wget https://sourceforge.net/projects/pyqt/files/PyQtDataVisualization/PyQtDataVisualization-5.7.1/PyQtDataVisualization_gpl-5.7.1.tar.gz/download -O PyQtDataVisualization_gpl-5.7.1.tar.gz && \
    tar xzvf PyQtDataVisualization_gpl-5.7.1.tar.gz && \
    cd PyQtDataVisualization_gpl-5.7.1 && \
    /opt/mlc-python-2.7.11/bin/mlc_python configure.py --qmake /opt/mlc-python-2.7.11/Qt-5.7.1/bin/qmake --sip /opt/mlc-python-2.7.11/bin/sip && \
    make -j4 && make install && \
    rm -rf /tmp/PyQtDataVisualization_gpl-5.7.1*

# Create .sh who will load the desired enviroment to run pip within it
RUN echo '#!/bin/bash' >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo 'export ROOTPATH="$(dirname "$(readlink -f "$0")")/.."' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo "" >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo "# Add the correct path to the LD_LIBRARY_PATH enviroment variable" >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo 'export LD_LIBRARY_PATH=$ROOTPATH/lib:$LD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo 'export LD_LIBRARY_PATH=$ROOTPATH/custom_libs:$LD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo 'export LD_LIBRARY_PATH=$ROOTPATH/Qt-5.7.1/lib:$LD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo 'PYUIC="$ROOTPATH/bin/pyuic5"' >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo "" >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo "# Run the dynamically compiled pip" >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo 'if [ "$#" -ne 0 ]; then' >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo '        $PYUIC $@' >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo "else" >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo '        $PYUIC' >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5 && \
    echo "fi" >> /opt/mlc-python-2.7.11/bin/mlc_pyuic5  && \
    chmod 755 /opt/mlc-python-2.7.11/bin/mlc_pyuic5

# Install mlc dependencies
# Create .sh who will load the desired enviroment to run nosetests within it
RUN export LD_LIBRARY_PATH=/usr/local/Qt-5.7.1/lib:$LD_LIBRARY_PATH && \
    export PATH=/usr/local/Qt-5.7.1/bin:$PATH && \
    /opt/mlc-python-2.7.11/bin/mlc_pip install cython numpy flask requests pyserial nose pyyaml coverage matplotlib scipy

RUN echo '#!/bin/bash' > /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo 'export ROOTPATH="$(dirname "$(readlink -f "$0")")/.."' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
    echo "" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo "# Add the correct path to the LD_LIBRARY_PATH enviroment variable" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo 'export LD_LIBRARY_PATH=$ROOTPATH/lib:$LD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo 'export LD_LIBRARY_PATH=$ROOTPATH/custom_libs:$LD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo 'export LD_LIBRARY_PATH=$ROOTPATH/Qt-5.7.1/lib:$LD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo 'NOSETESTS="$ROOTPATH/bin/nosetests"' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo "" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo "# Run the dynamically compiled nosetests" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo 'if [ "$#" -ne 0 ]; then' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo '        $NOSETESTS $@' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo "else" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo '        $NOSETESTS' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo "fi" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    chmod 755 /opt/mlc-python-2.7.11/bin/mlc_nosetests

RUN echo '[Paths]' > /opt/mlc-python-2.7.11/bin/qt.conf && \
    echo "Prefix=../Qt-5.7.1" >> /opt/mlc-python-2.7.11/bin/qt.conf

# Install fpm and create .deb package
RUN gem install fpm && fpm -s dir -t deb -v 0.6 -n mlc-python-ubuntu-14.04 /opt/mlc-python-2.7.11
