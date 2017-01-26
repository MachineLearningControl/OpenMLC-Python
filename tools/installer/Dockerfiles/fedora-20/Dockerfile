# Set the base image
FROM fedora:20
MAINTAINER "Ezequiel Torres Feyuk" <ezequiel.torresfeyuk@gmail.com>
ENV container docker
RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == systemd-tmpfiles-setup.service ] || rm -f $i; done); \
rm -f /lib/systemd/system/multi-user.target.wants/*;\
rm -f /etc/systemd/system/*.wants/*;\
rm -f /lib/systemd/system/local-fs.target.wants/*; \
rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
rm -f /lib/systemd/system/basic.target.wants/*;\
rm -f /lib/systemd/system/anaconda.target.wants/*;
VOLUME [ "/sys/fs/cgroup" ]
CMD ["/usr/sbin/init"]

# Update the current system
RUN yum update -y
# RUN yum --enablerepo=extras install epel-release -y

RUN yum --enablerepo=updates-testing update -y
RUN yum --enablerepo=updates-testing install openssl-devel -y

# Install packages
RUN yum install tk-devel lapack-devel cmake tcl tcl-devel expect tkinter openssh-server gcc gcc-c++ wget xz make vim openssh-clients rpm-build ruby-devel libpng libpng-devel sqlite-devel qt5-qtbase qt5-qtbase-devel qt5-qtdeclarative qt5-qtdeclarative-devel -y

WORKDIR /tmp
# Compile Openssl from scratch. There are dependency problems with this packet in Fedora 20
# RUN wget https://www.openssl.org/source/openssl-1.1.0c.tar.gz && \
#     tar xzvf openssl-1.1.0c.tar.gz && \
#     cd openssl-1.1.0c && ./config && make && make install

# Download python 2.7.11
# For more information about the compilation of the Python: http://www.mathworks.com/help/matlab/matlab_external/system-requirements-for-matlab-engine-for-python.html?requestedDomain=www.mathworks.com
RUN wget -q https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tar.xz && \
    tar xJvf Python-2.7.11.tar.xz && \
    cd Python-2.7.11 && ./configure --enable-shared --enable-unicode=ucs4 --prefix=/opt/mlc-python-2.7.11 && \
    make && make install

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
    cd setuptools-20.1.1 && /opt/mlc-python-2.7.11/bin/mlc_python setup.py build && /opt/mlc-python-2.7.11/bin/mlc_python setup.py install


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
    chmod 755 /opt/mlc-python-2.7.11/bin/mlc_pip


# Install PyQt5 Environment
RUN wget https://sourceforge.net/projects/pyqt/files/sip/sip-4.19/sip-4.19.tar.gz && \
    tar xzvf sip-4.19.tar.gz && \
    cd sip-4.19 && \
    /opt/mlc-python-2.7.11/bin/mlc_python configure.py && \
    make && make install

RUN wget https://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.7.1/PyQt5_gpl-5.7.1.tar.gz && \
    tar xzvf PyQt5_gpl-5.7.1.tar.gz && \
    cd PyQt5_gpl-5.7.1 && \
    /opt/mlc-python-2.7.11/bin/mlc_python configure.py --qmake /usr/bin/qmake-qt5 --confirm-license --sip /opt/mlc-python-2.7.11/bin/sip && \
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
RUN yum update -y && yum install git -y
RUN git clone git://code.qt.io/qt/qtcharts.git && \
    cd qtcharts && \
    git checkout release-2.1.0 && \
    /usr/bin/qmake-qt5 && make && make install

RUN wget https://sourceforge.net/projects/pyqt/files/PyQtChart/PyQtChart-5.7.1/PyQtChart_gpl-5.7.1.tar.gz && \
    tar xzvf PyQtChart_gpl-5.7.1.tar.gz && \
    cd PyQtChart_gpl-5.7.1 && \
    /opt/mlc-python-2.7.11/bin/mlc_python configure.py --qmake /usr/bin/qmake-qt5 --qtchart-version=2.1.0 --sip /opt/mlc-python-2.7.11/bin/sip && \
    make && make install

RUN git clone git://code.qt.io/qt/qtdatavis3d.git && \
    cd qtdatavis3d && \
    git checkout 5.7 && \
    /usr/bin/qmake-qt5 && make && make install

RUN wget https://sourceforge.net/projects/pyqt/files/PyQtDataVisualization/PyQtDataVisualization-5.7.1/PyQtDataVisualization_gpl-5.7.1.tar.gz/download -O PyQtDataVisualization_gpl-5.7.1.tar.gz && \
    tar xzvf PyQtDataVisualization_gpl-5.7.1.tar.gz && \
    cd PyQtDataVisualization_gpl-5.7.1 && \
    /opt/mlc-python-2.7.11/bin/mlc_python configure.py --qmake /usr/bin/qmake-qt5 --sip /opt/mlc-python-2.7.11/bin/sip && \
    make && make install


# Install mlc dependencies
RUN /opt/mlc-python-2.7.11/bin/mlc_pip install pyserial numpy nose matplotlib scipy pyyaml flask requests

# Create .sh who will load the desired enviroment to run nosetests within it
RUN echo '#!/bin/bash' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
    echo "" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests \
    echo "# Add the correct path to the LD_LIBRARY_PATH enviroment variable" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests \
    echo 'export LD_LIBRARY_PATH=/opt/mlc-python-2.7.11/lib:$LD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests \
    echo 'NOSETESTS="/opt/mlc-python-2.7.11/bin/nosetests"' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests \
    echo "" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests \
    echo "# Run the dynamically compiled nosetests" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests \
    echo 'if [ "$#" -ne 0 ]; then' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests \
    echo '        $NOSETESTS $@' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests \
    echo "else" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests \
    echo '        $NOSETESTS' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests \
    echo "fi" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests \
    chmod 755 /opt/mlc-python-2.7.11/bin/mlc_nosetests

# Install fpm and create .deb package
RUN gem install fpm && fpm -s dir -t rpm -v 0.5 -n mlc-python-fedora20 /opt/mlc-python-2.7.11
