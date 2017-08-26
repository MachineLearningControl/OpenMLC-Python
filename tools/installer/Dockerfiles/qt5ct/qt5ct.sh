#!/bin/bash
export ROOTPATH="$(dirname "$(readlink -f "$0")")/.."

# Execute the qt5ct
unset QT_STYLE_OVERRIDE
export QT_QPA_PLATFORMTHEME=qt5ct
export LD_LIBRARY_PATH=$ROOTPATH/mlc_python/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$ROOTPATH/mlc_python/custom_libs:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$ROOTPATH/mlc_python/Qt-5.9.1/lib:$LD_LIBRARY_PATH
export QT_LOGGING_RULES="qt5ct.debug=false"
$ROOTPATH/mlc_python/bin/qt5ct
