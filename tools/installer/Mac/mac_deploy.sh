#!/bin/bash

# Install xcode in some way...

# Install brew
# xcode-select --install
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# Install dependencies
brew install openssl wget freetype libpng pkg-config qt5 cmake gcc

# Add include and libs paths to SSL to compile Python with Openssl support
export LDFLAGS="-L/usr/local/opt/openssl/lib"
export CPPFLAGS="-I/usr/local/opt/openssl/include"
export CFLAGS="-I/usr/local/opt/openssl/include"

WORKDIR=`pwd`

# Download and compile Python 2.7.11
wget -q https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tar.xz && \
tar xJvf Python-2.7.11.tar.xz && \
cd Python-2.7.11 && ./configure --enable-shared --enable-unicode=ucs4 --prefix=/opt/mlc-python-2.7.11 && make && make install
cd $WORKDIR

# Create mlc_python script
echo '#!/bin/bash' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo "" >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo "# Add the correct path to the DYLD_LIBRARY_PATH enviroment variable" >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo 'export DYLD_LIBRARY_PATH=/opt/mlc-python-2.7.11/lib:$DYLD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo 'PYTHON="/opt/mlc-python-2.7.11/bin/python2.7"' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo "" >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo "# Run the dynamically compiled python for matlab" >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo 'if [ "$#" -ne 0 ]; then' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo '        $PYTHON $@' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo "else" >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo '        $PYTHON' >> /opt/mlc-python-2.7.11/bin/mlc_python && \
echo "fi" >> /opt/mlc-python-2.7.11/bin/mlc_python && \
chmod 755 /opt/mlc-python-2.7.11/bin/mlc_python

# Install setuptools
wget -q https://pypi.python.org/packages/source/s/setuptools/setuptools-20.1.1.tar.gz#md5=10a0f4feb9f2ea99acf634c8d7136d6d && \
tar xzvf setuptools-20.1.1.tar.gz && \
cd setuptools-20.1.1 && /opt/mlc-python-2.7.11/bin/mlc_python setup.py build && /opt/mlc-python-2.7.11/bin/mlc_python setup.py install
cd $WORKDIR

# Install pip
wget -q https://pypi.python.org/packages/source/p/pip/pip-8.0.2.tar.gz#md5=3a73c4188f8dbad6a1e6f6d44d117eeb && \
tar xzvf pip-8.0.2.tar.gz && \
cd pip-8.0.2 && /opt/mlc-python-2.7.11/bin/mlc_python setup.py build && /opt/mlc-python-2.7.11/bin/mlc_python setup.py install
cd $WORKDIR

echo '#!/bin/bash' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
echo "" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
echo "# Add the correct path to the DYLD_LIBRARY_PATH enviroment variable" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
echo 'export DYLD_LIBRARY_PATH=/opt/mlc-python-2.7.11/lib:$DYLD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
echo 'PIP="/opt/mlc-python-2.7.11/bin/pip2.7"' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
echo "" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
echo "# Run the dynamically compiled pip" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
echo 'if [ "$#" -ne 0 ]; then' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
echo '        $PIP $@' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
echo "else" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
echo '        $PIP' >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
echo "fi" >> /opt/mlc-python-2.7.11/bin/mlc_pip && \
chmod 755  /opt/mlc-python-2.7.11/bin/mlc_pip

# Add PyQt5 Support
wget https://sourceforge.net/projects/pyqt/files/sip/sip-4.18.1/sip-4.18.1.tar.gz && \
tar xzvf sip-4.18.1.tar.gz && \
cd sip-4.18.1 && \
/opt/mlc-python-2.7.11/bin/mlc_python configure.py && \
make && make install
cd $WORKDIR

wget https://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.7/PyQt5_gpl-5.7.tar.gz && \
tar xzvf PyQt5_gpl-5.7.tar.gz && \
cd PyQt5_gpl-5.7 && \
/opt/mlc-python-2.7.11/bin/mlc_python configure.py --confirm-license --sip /opt/mlc-python-2.7.11/bin/sip --qmake /usr/local/opt/qt5/bin/qmake && \
make && make install
cd $WORKDIR

wget https://sourceforge.net/projects/pyqt/files/PyQtChart/PyQtChart-5.7/PyQtChart_gpl-5.7.tar.gz && \
tar xzvf PyQtChart_gpl-5.7.tar.gz && \
cd PyQtChart_gpl-5.7 && \
/opt/mlc-python-2.7.11/bin/mlc_python configure.py --sip /opt/mlc-python-2.7.11/bin/sip && \
make && make install
cd $WORKDIR

/opt/mlc-python-2.7.11/bin/mlc_pip install flask requests pyserial nose matplotlib numpy scipy pyyaml

echo '#!/bin/bash' > /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
echo "" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
echo "# Add the correct path to the DYLD_LIBRARY_PATH enviroment variable" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
echo 'export DYLD_LIBRARY_PATH=/opt/mlc-python-2.7.11/lib:$DYLD_LIBRARY_PATH' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
echo 'NOSETESTS="/opt/mlc-python-2.7.11/bin/nosetests"' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
echo "" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
echo "# Run the dynamically compiled nosetests" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
echo 'if [ "$#" -ne 0 ]; then' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
echo '        $NOSETESTS $@' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
echo "else" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
echo '        $NOSETESTS' >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
echo "fi" >> /opt/mlc-python-2.7.11/bin/mlc_nosetests && \
chmod 755 /opt/mlc-python-2.7.11/bin/mlc_nosetests
