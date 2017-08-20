#!/bin/bash

# Execute the MLC_GUI
unset QT_STYLE_OVERRIDE
export QT_QPA_PLATFORMTHEME=qt5ct
/opt/mlc-python-3.6.2/bin/mlc_python mlc_gui.py
