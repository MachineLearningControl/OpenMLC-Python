#!/bin/bash

# Execute the MLC_GUI
unset QT_STYLE_OVERRIDE
export QT_QPA_PLATFORMTHEME=qt5ct
/opt/mlc-python-3.4.7/bin/mlc_python mlc_gui.py
