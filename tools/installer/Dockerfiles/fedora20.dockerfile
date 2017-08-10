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

WORKDIR /tmp

RUN mkdir -p /opt/mlc-python-2.7.11/bin

# Update the current system
RUN yum update -y
# RUN yum --enablerepo=extras install epel-release -y

RUN yum --enablerepo=updates-testing update -y
RUN yum --enablerepo=updates-testing install openssl-devel -y

# Install packages
RUN yum install tk-devel lapack-devel cmake tcl tcl-devel expect tkinter openssh-server gcc gcc-c++ wget xz make vim openssh-clients rpm-build ruby-devel libpng libpng-devel sqlite-devel libxkbcommon freeglut-devel libxcb libxcb-devel xcb-util xcb-util-devel git -y

# Compile Openssl from scratch. There are dependency problems with this packet in Fedora 20
# RUN wget https://www.openssl.org/source/openssl-1.1.0c.tar.gz && \
#     tar xzvf openssl-1.1.0c.tar.gz && \
#     cd openssl-1.1.0c && ./config && make && make install

# Download python 2.7.11
# For more information about the compilation of the Python: http://www.mathworks.com/help/matlab/matlab_external/system-requirements-for-matlab-engine-for-python.html?requestedDomain=www.mathworks.com
RUN wget -q https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tar.xz && \
    tar xJvf Python-2.7.11.tar.xz && \
    cd Python-2.7.11 && ./configure --enable-shared --enable-unicode=ucs4 --prefix=/opt/mlc-python-2.7.11 && make && make install && \
    rm -rf /tmp/Python-2.7.11*

# Install Qt5.7
RUN git clone git://code.qt.io/qt/qtbase.git && \
    cd qtbase && \
    git checkout 5.7 && \
    ./configure --prefix=/opt/mlc-python-2.7.11/Qt-5.7.1 -xkb-config-root /usr/share/X11/xkb -no-gtk -nomake tests -nomake examples -qt-xcb --opensource --confirm-license && make -j4 && make install && \
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

RUN git clone https://github.com/Ezetowers/qt5ct.git && \
    cd qt5ct && \
    /opt/mlc-python-2.7.11/Qt-5.7.1/bin/qmake PREFIX=/opt/mlc-python-2.7.11/qt5ct && make -j4 && make install && \
    rm -rf /tmp/qt5ct

RUN git clone git://code.qt.io/qt/qtstyleplugins.git && \
    cd qtstyleplugins && \
    /opt/mlc-python-2.7.11/Qt-5.7.1/bin/qmake && make && \
    mkdir -p /opt/mlc-python-2.7.11/Qt-5.7.1/plugins/styles && \
    cp -r ./plugins/styles/* /opt/mlc-python-2.7.11/Qt-5.7.1/plugins/styles && \
    rm -rf /tmp/qtstyleplugins

# Add Python scripts
ADD mlc_python_scripts/* /opt/mlc-python-2.7.11/bin/

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

RUN /opt/mlc-python-2.7.11/bin/mlc_pip install --upgrade pip

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

RUN wget http://www.graphviz.org/pub/graphviz/stable/SOURCES/graphviz-2.40.1.tar.gz && \
    tar xzvf graphviz-2.40.1.tar.gz && \
    cd graphviz-2.40.1 && \
    ./configure --prefix=/tmp/graphviz-2.40.1 && \
    make -j4 && make install

# Install mlc dependencies
# Create .sh who will load the desired enviroment to run nosetests within it
RUN export CFLAGS="-I/tmp/graphviz-2.40.1/include" \
    export LD_LIBRARY_PATH=/opt/mlc-python-2.7.11/custom_libs:$LD_LIBRARY_PATH && \
    export LD_LIBRARY_PATH=/opt/mlc-python-2.7.11/Qt-5.7.1/lib:$LD_LIBRARY_PATH && \
    export LD_LIBRARY_PATH=/tmp/graphviz-2.40.1/lib:$LD_LIBRARY_PATH && \
    export PKG_CONFIG_PATH=/tmp/graphviz-2.40.1/lib/pkgconfig:$PKG_CONFIG_PATH && \
    export PATH=/opt/mlc-python-2.7.11/Qt-5.7.1/bin:$PATH && \
    export PATH=/opt/mlc-python-2.7.11/custom_bins:$PATH && \
    export PATH=/tmp/graphviz-2.40.1/bin:$PATH && \
    /opt/mlc-python-2.7.11/bin/mlc_pip install networkx pydotplus pygraphviz 'ipython<6.0.0' numpy flask requests pyserial nose pyyaml coverage matplotlib scipy pyusb

RUN mkdir -p /opt/mlc-python-2.7.11/custom_libs /opt/mlc-python-2.7.11/custom_bins && \
    cp -r /tmp/graphviz-2.40.1/lib/*.so* /tmp/graphviz-2.40.1/lib/graphviz /opt/mlc-python-2.7.11/custom_libs && \
    cp -r /tmp/graphviz-2.40.1/bin/* /opt/mlc-python-2.7.11/custom_bins && \
    rm -rf /tmp/graphviz-2.40.1*

RUN gem install fpm

ARG RELEASE
ENV RELEASE ${RELEASE}
ENV OS_VERSION fedora-20
ENV PACKAGE_TYPE rpm
ADD deploy_scripts/* /tmp/deploy_scripts/
ADD qt5ct /tmp/qt5ct/
ENTRYPOINT ["/tmp/deploy_scripts/create_MLC_folder.sh"]
