#!/bin/bash
MLC_PATH="/tmp/MLC-$RELEASE"
# Create the containing folder
mkdir -p $MLC_PATH/tools

# Download the MLC code from Github
wget "https://github.com/Ezetowers/MLC/archive/v$RELEASE.tar.gz"
tar xzvf v$RELEASE.tar.gz -C $MLC_PATH
mv $MLC_PATH/OpenMLC-Python-$RELEASE $MLC_PATH/MLC-$RELEASE
rm -rf /tmp/v$RELEASE.tar.gz

# Add libs and binaries used by Python before creating the .deb
mkdir -p /opt/mlc-python-$PYTHON_VERSION/custom_bins
mkdir -p /opt/mlc-python-$PYTHON_VERSION/custom_libs
cp -r /usr/bin/dot /opt/mlc-python-$PYTHON_VERSION/custom_bins

# Add the mlc_python
cp -r /opt/mlc-python-$PYTHON_VERSION $MLC_PATH/mlc_python
chmod a+x $MLC_PATH/mlc_python/bin/*

# Add project scripts
cp -r /tmp/deploy_scripts/mlc.sh.in $MLC_PATH/mlc.sh
sed -i "s/^\([^@]*\)@\([^@]*\)@$/\1$RELEASE/" $MLC_PATH/mlc.sh

cd $MLC_PATH
ln -s mlc_python/bin/mlc_python mlc_python.sh
ln -s mlc_python/bin/mlc_ipython mlc_ipython.sh
ln -s mlc_python/bin/mlc_pip mlc_pip.sh

# Move qt5ct binary, add license and remove another directories
mv $MLC_PATH/mlc_python/qt5ct/bin/qt5ct $MLC_PATH/mlc_python/bin
cp -r /tmp/qt5ct/qt5ct.COPYING $MLC_PATH/mlc_python/bin
cp -r /tmp/qt5ct/.config $MLC_PATH/mlc_python/bin
rm -rf $MLC_PATH/mlc_python/qt5ct

# Add tools scripts
cp -r /tmp/deploy_scripts/install_matlab_engine.sh $MLC_PATH/tools
cp -r /tmp/qt5ct/qt5ct.sh $MLC_PATH/tools
chmod a+x $MLC_PATH/tools/*

# Clean unnecesary files in the MLC package
find $MLC_PATH/mlc_python -name "*.pyc" | xargs rm -rf
find $MLC_PATH/mlc_python -name "*.pyo" | xargs rm -rf
find $MLC_PATH/mlc_python -name "*.pyd" | xargs rm -rf
find $MLC_PATH/mlc_python -name "test" | xargs rm -rf
rm -rf $MLC_PATH/MLC-$RELEASE/tools/Kicad_Projects
rm -rf $MLC_PATH/MLC-$RELEASE/tools/installer
rm -rf $MLC_PATH/MLC-$RELEASE/tests
rm -rf $MLC_PATH/MLC-$RELEASE/doc
rm -rf $MLC_PATH/MLC-$RELEASE/bugs
rm -rf $MLC_PATH/MLC-$RELEASE/matlab_code
rm -rf $MLC_PATH/Qt-5.7.1/docs
rm -rf $MLC_PATH/Qt-5.7.1/include
rm -rf $MLC_PATH/Qt-5.7.1/mkspecs

# Create the MLC Package
tar cJvpf /tmp/MLC-$RELEASE-$OS_VERSION.tar.xz -C /tmp MLC-$RELEASE
fpm -s dir -t $PACKAGE_TYPE -v $RELEASE -n mlc-python-$OS_VERSION /opt/mlc-python-$PYTHON_VERSION
mv /tmp/MLC-$RELEASE/*.deb /tmp/release
mv /tmp/*.tar.xz /tmp/release