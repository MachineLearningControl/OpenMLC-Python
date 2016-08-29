#!/bin/bash

OS=""
PACKAGE_SYSTEM=""
UNAME=`uname`
DATE_STRING=`date +"%Y-%m-%d_%H%M%S"`
LOG_FILE="/tmp/MLC_install_log_$DATE_STRING.log"
FILE_LOG_LEVEL=7
CONSOLE_LOG_LEVEL=5
MLC_PYTHON_DIR=/opt/mlc-python-2.7.11
UNINSTALL=0
INSTALLED=0
PACKAGE_PATH=""
MATLAB_DIR=""
PYTHON_ENG_DIR="extern/engines/python"

function usage() {
    log_message 5 "MLC Installer. Available options:"
    log_message 5 "  -h: Show this help"
    log_message 5 "  -u: uninstall MLC"
    log_message 5 "  -p <file>: MLC's [deb|RPM] file. Mandatory!"
    log_message 5 "  -d <dir>: Absolute path where MATLAB is installed in the system. Mandatory!"
}


# Check if the OS where this script is running is a Linux like flavor
function check_os() {
    if [ x"$UNAME" = "xLinux" ]; then
        return 0
    fi

   log_message 1 "ERROR: The present OS is not a Linux like system. Aborting installation."
   exit 1
}


function get_linux_flavor() {
    # grep return 0 if any line was selected
    if egrep -q -i "centos|rhel|fedora" /etc/os-release; then
        PACKAGE_SYSTEM="RPM"
    elif egrep -q -i "ubuntu|debian" /etc/os-release; then
        # TODO: Find out how to identify another RPM OSs like Debian or Mint
        PACKAGE_SYSTEM="DEB"
    fi

    if [ x"$PACKAGE_SYSTEM" = "x" ]; then
        log_message 1 "Could not identify Linux package system. Aborting instalation."
        exit 1
    else
        log_message 5 "$PACKAGE_SYSTEM Package System detected."
    fi
}


# LOG LEVELS:
# 0: EMERGENCY
# 1: CRITICAL
# 2: ERROR
# 3: WARNING
# 4: NOTICE
# 5: INFO
# 6: DEBUG
# 7: TRACE
function log_message() {
    LOG_LEVEL=$1
    LOG_MESSAGE=$2

    if [ $LOG_LEVEL -le $FILE_LOG_LEVEL ]; then
        echo -e "$LOG_MESSAGE" >> $LOG_FILE
    fi

    if [ $LOG_LEVEL -le $CONSOLE_LOG_LEVEL ]; then
        echo -e "$LOG_MESSAGE"
    fi
}


function check_run_as_root() {
    case `id` in
        uid=0*) ;;

        *)
        log_message 1 "ERROR: Must be root to run script (use -h for help). Aborting installation"
        exit 1
        ;;
    esac
}


function parse_args() {
    log_message 7 "Checking command line arguments"
    # Needed to make getopts work
    local OPTIND opt
    OPTSPEC=":hup:d:"

    while getopts $OPTSPEC opt; do
        case "${opt}" in
            h)
                usage
                exit 0
                ;;
            u)
                UNINSTALL=1
                ;;
            p)
                if [ -z "$OPTARG" ]; then
                   log_message 1 "option '-p' requires an argument"
                   usage
                   exit 1
                fi

                PACKAGE_PATH=$OPTARG
                ;;
            d)
                if [ -z "$OPTARG" ]; then
                   log_message 1 "option '-d' requires an argument"
                   usage
                   exit 1
                fi
                MATLAB_DIR=$OPTARG
                ;;
            \?)
                log_message 1 "ERROR: Invalid option received"
                usage
                exit 1
                ;;
        esac
    done

    if [ $UNINSTALL -eq 1 ]; then
	    return
    fi

    if [ x"$PACKAGE_PATH" = "x" ]; then
	    log_message  1 "Package path must be supplied."
	    usage
	    exit 1
    fi

    if [ x"$MATLAB_DIR" = "x" ]; then
	    log_message 1 "MATLAB dir must be supplied."
	    usage
	    exit 1
    fi
}


function check_previous_installation() {
    log_message 5 "Searching for previous version of MLC"
    if [ -d $MLC_PYTHON_DIR ]; then
        log_message 5 "Previous installation of MLC detected"
        INSTALLED=1
    fi
}


# For the moment, there will be always only a version of mlc.
# This version always will be installed in /opt/mlc-python-2.7.11
function uninstall() {
    log_message 5 "Preparing for uninstall"
    if [ $PACKAGE_SYSTEM = "DEB" ]; then
        MLC_PYTHON=`dpkg -l | grep mlc-python | awk '{print $2}'`
        MLC_VERSION=`dpkg -l | grep mlc-python | awk '{print $3}'`
    elif [ $PACKAGE_SYSTEM = "RPM" ]; then
        MLC_PYTHON="mlc-python"
        RPM_PACKAGE=`rpm -qa | grep $MLC_PYTHON`
        MLC_VERSION=`yum info $RPM_PACKAGE | grep -i "version" | awk -F ':' '{print $2}' | sed 's/ //g'`
    fi

    if [ x"$MLC_PYTHON" != "x" ]; then
	    log_message 5 "Version $MLC_VERSION of MLC found. Proceed to uninstall."
        # Redirect stderr to stdout and the output to /dev/null to avoid annoying warnings
        if [ $PACKAGE_SYSTEM = "DEB" ]; then
            dpkg -r $MLC_PYTHON > /dev/null 2>&1
        elif [ $PACKAGE_SYSTEM = "RPM" ]; then
            rpm -e "$MLC_PYTHON"
        fi
    else
        log_message 3 "No version of MLC was found on the database. Aborting uninstalling."
        exit 1
    fi

    if [ -d $MLC_PYTHON_DIR ]; then
        log_message 5 "MLC python root dir wasn't removed after the package removal. Do you want to remove it? y[n]"
        DEFAULT="y"
        while true; do
            read -p "" RESPONSE
            RESPONSE=${RESPONSE:=$DEFAULT}
            case $RESPONSE in
                [yn]*) break;;
                *) log_message 4 "Please answer y or n";;
            esac
        done

        if [ $RESPONSE = y ]; then
            log_message 5 "Proceed to remove MLC python root dir"
           rm -rf $MLC_PYTHON_DIR
        fi
    fi

    log_message 5 "MLC Python was succesfully uninstalled."
}


function install_mlc() {
    # Check if the package exists
    if [ ! -f $PACKAGE_PATH ]; then
        log_message 1 "Package path doesn't exists. Aborting installation."
        exit 1
    fi

    # Check if MATLAB dir exists
    if [ ! -d $MATLAB_DIR ]; then
        log_message 1 "MATLAB dir doesn't exists. Aborting installation."
    fi

    # Check that the python engine is installed
    if [ ! -d "$MATLAB_DIR/$PYTHON_ENG_DIR" ]; then
        log_message 1 "MATLAB version isn't shipped with Python Engine module. Check that your MATLAB version is superior to version 2014a"
    fi

    log_message 5 "Proceed to install MLC Python."
    if [ $PACKAGE_SYSTEM = "DEB" ]; then
        dpkg -i $PACKAGE_PATH
    elif [ $PACKAGE_SYSTEM = "RPM" ]; then
        rpm -ivh $PACKAGE_PATH
    fi

    if [ $? -ne 0 ]; then
        log_message 1 "An error ocurred while installing MLC Package. Aborting installation"
        exit 1
    fi

    # Move to Python engine directory to install the Engine module. It doesn't work in another way
    cd "$MATLAB_DIR/$PYTHON_ENG_DIR"

    #Remove the build directory if it exists
    rm -rf "$MATLAB_DIR/$PYTHON_ENG_DIR/build"
    $MLC_PYTHON_DIR/bin/mlc_python "$MATLAB_DIR/$PYTHON_ENG_DIR/setup.py" build > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        log_message 1 "An error ocurred while building MATLAB Python Package. Aborting installation"
        UNINSTALL=1
        uninstall
        exit 1
    fi


    $MLC_PYTHON_DIR/bin/mlc_python "$MATLAB_DIR/$PYTHON_ENG_DIR/setup.py" install > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        log_message 1 "An error ocurred while installing MATLAB Python Package. Aborting installation"
        UNINSTALL=1
        uninstall
        exit 1
    fi

    log_message 5 "MLC Python succesfully installed"
}


function main() {
    log_message 4 "############################"
    log_message 4 "#     MLC Installer        #"
    log_message 4 "############################"
    log_message 4 "Saving log to $LOG_FILE"

    check_os
    get_linux_flavor
    if [ $# -ne 1 -o "$1" != "-h"  ]; then
       check_run_as_root
    fi
    parse_args $*
    check_previous_installation

    if [ $UNINSTALL -eq 1 ]; then
        uninstall
    else
        install_mlc
    fi
}


main $*
