#!/bin/bash
export ROOTPATH="$(dirname "$(readlink -f "$0")")/.."

OS=""
PACKAGE_SYSTEM=""
UNAME=`uname`
DATE_STRING=`date +"%Y-%m-%d_%H%M%S"`
LOG_FILE="$ROOTPATH/tools/MATLAB_Engine_install_log_$DATE_STRING.log"
FILE_LOG_LEVEL=7
CONSOLE_LOG_LEVEL=5
MLC_PYTHON_DIR="$ROOTPATH/mlc_python"
UNINSTALL=0
INSTALLED=0
PACKAGE_PATH=""
MATLAB_DIR=""
PYTHON_ENG_DIR="extern/engines/python"


function usage() {
    log_message 5 "MLC Installer. Available options:"
    log_message 5 "  -h: Show this help"
    log_message 5 "  -d <dir>: Absolute path where MATLAB is installed in the system. Mandatory!"
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

    if [ x"$MATLAB_DIR" = "x" ]; then
        log_message 1 "MATLAB dir must be supplied."
        usage
        exit 1
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


function install_matlab_engine() {
    # Move to Python engine directory to install the Engine module. It doesn't work in another way
    cd "$MATLAB_DIR/$PYTHON_ENG_DIR"

    #Remove the build directory if it exists
    rm -rf "$MATLAB_DIR/$PYTHON_ENG_DIR/build"
    $MLC_PYTHON_DIR/bin/mlc_python "$MATLAB_DIR/$PYTHON_ENG_DIR/setup.py" build > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        log_message 1 "An error ocurred while building MATLAB Python Package. Aborting installation"
        exit 1
    fi


    $MLC_PYTHON_DIR/bin/mlc_python "$MATLAB_DIR/$PYTHON_ENG_DIR/setup.py" install > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        log_message 1 "An error ocurred while installing MATLAB Python Package. Aborting installation"
        exit 1
    fi

    log_message 5 "MATLAB Engine was succesfully installed"
}


function main() {
    log_message 4 "#################################"
    log_message 4 "#     MATLAB Engine Installer   #"
    log_message 4 "#################################"
    log_message 4 "Saving log to $LOG_FILE"

    if [ $# -ne 1 -o "$1" != "-h"  ]; then
       check_run_as_root
    fi
    parse_args $*
    install_matlab_engine
}


main $*