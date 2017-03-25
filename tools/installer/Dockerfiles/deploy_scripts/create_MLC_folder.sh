#!/bin/bash
RELEASE=$1
MLC_PATH="/tmp/MLC-$RELEASE"

# Create the containing folder
mkdir -p $MLC_PATH/tools

# Download the MLC code from Github
wget "https://github.com/Ezetowers/MLC/archive/v$RELEASE.tar.gz"
tar xzvf v$RELEASE.tar.gz -C $MLC_PATH
rm -rf /tmp/v$RELEASE.tar.gz

# Add the mlc_python
mv /opt/mlc-python-2.7.11 $MLC_PATH/mlc_python

# Add project scripts
cp -r /tmp/deploy_scripts/mlc.sh.in $MLC_PATH/mlc.sh
sed -i "s/^\([^@]*\)@\([^@]*\)@$/\1$RELEASE/" $MLC_PATH/mlc.sh
cp -r /tmp/deploy_scripts/install_matlab_engine.sh $MLC_PATH/tools

# Create symbolic links to mlc_python and mlc_ipython
cd $MLC_PATH
ln -s mlc_python/bin/mlc_python mlc_python.sh
ln -s mlc_python/bin/mlc_ipython mlc_ipython.sh
