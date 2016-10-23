# Set the base image
FROM centos:7
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

# Install packages
# RUN apt-get install ssh gcc wget xz-utils make vim libssl-dev -y
RUN yum install tk-devel lapack-devel cmake tcl tcl-devel expect tkinter qt-devel openssh-server gcc gcc-c++ wget xz make vim openssl-devel openssh-clients rpm-build ruby-devel libpng libpng-devel sqlite-devel -y

# Download python 2.7.11
WORKDIR /tmp
RUN wget -q https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tar.xz
RUN tar xJvf Python-2.7.11.tar.xz
# For more information about the compilation of the Python: http://www.mathworks.com/help/matlab/matlab_external/system-requirements-for-matlab-engine-for-python.html?requestedDomain=www.mathworks.com
RUN cd Python-2.7.11 && ./configure --enable-shared --enable-unicode=ucs4 --prefix=/opt/mlc-python-2.7.11 
RUN cd Python-2.7.11 && make && make install

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
RUN wget -q https://pypi.python.org/packages/source/s/setuptools/setuptools-20.1.1.tar.gz#md5=10a0f4feb9f2ea99acf634c8d7136d6d
RUN tar xzvf setuptools-20.1.1.tar.gz
RUN cd setuptools-20.1.1 && /opt/mlc-python-2.7.11/bin/mlc_python setup.py build && /opt/mlc-python-2.7.11/bin/mlc_python setup.py install 


# Idem with pip
RUN wget -q https://pypi.python.org/packages/source/p/pip/pip-8.0.2.tar.gz#md5=3a73c4188f8dbad6a1e6f6d44d117eeb
RUN tar xzvf pip-8.0.2.tar.gz
RUN cd pip-8.0.2 && /opt/mlc-python-2.7.11/bin/mlc_python setup.py build && /opt/mlc-python-2.7.11/bin/mlc_python setup.py install 

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


# Install mlc dependencies
RUN /opt/mlc-python-2.7.11/bin/mlc_pip install pyserial numpy nose matplotlib scipy pyyaml

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

# Install fpm
RUN gem install fpm

# Create .rpm package
RUN fpm -s dir -t rpm -v 0.2 -n mlc-python /opt/mlc-python-2.7.11
