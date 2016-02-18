#!/bin/bash

OS=""
UNAME=`uname`
DATE_STRING=`date +"%Y-%m-%d_%H%M%S"`
LOG_FILE="MLC_install_log_$DATE_STRING.log"
FILE_LOG_LEVEL=7
CONSOLE_LOG_LEVEL=5
MLC_ROOT_DIR=/opt/mlc-python-2.7.11
UNINSTALL=0
INSTALLED=0

function usage() {
    log_message 5 "MLC Installer. Available options:"
    log_message 5 "  -h: Show this help"
    log_message 5 "  -u: uninstall TFTP"
    log_message 5 "  -p <file>: MLC's deb file. Mandatory!"
    log_message 5 "  -m <dir>: Absolute path where MATLAB is installed in the system"
}


# Check if the OS where this script is running is a Linux like flavor
function check_os() {
    if [ x"$UNAME" = "xLinux" ] ; then
        return 0
    fi

   log_message 1 "ERROR: The present OS is not a Linux like system. Aborting installation." 
   exit 1
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
        log_message 1 "ERROR: Must be root to run script. Aborting installation"
        exit 1
        ;;
    esac
}


function parse_args() {
    log_message 7 "Checking command line arguments"
    optspec="hup:d:"
   
    while getopts "$optspec" opt; do
        case $opt in
            h)
                show_usage
                exit 0
                ;;
            u)
                UNINSTALL=1
                ;;
            p)
                if [ -z "$OPTARG" ]; then
                   log_message 1 "option '-p' requires an argument" 
                   show_usage
                   exit 1
                fi

                PACKAGE_PATH=$OPTARG
                ;;
            d)
                if [ -z "$OPTARG" ]; then
                   log_message 1 "option '-d' requires an argument" 
                   show_usage
                   exit 1
                fi
                MATLAB_DIR=$OPTARG
                ;;
            *)
                log_message 1 "ERROR: Invalid option received"
                show_usage
                exit 1
                ;;
        esac
    done
}


function check_previous_installation() {
    log_message 5 "Searching for previous version of MLC"
    if [ -d $MLC_ROOT_DIR ]; then
        log_message 5 "Previous installation of MLC detected"
        INSTALLED=1
    fi
}


function uninstall() {
    log_message 5 "Preparing for uninstall"
    
}


function install_mlc() {
}


function main() {
    log_message 4 "############################"
    log_message 4 "#     MLC Installer        #"
    log_message 4 "############################"
    log_message 4 "Saving log to $LOG_FILE"

    check_os
    check_run_as_root
    parse_args $* 
    check_previous_installation

    if [ $UNINSTALL -eq 1 ]; then
        uninstall
    else
        install_mlc
    fi
}


main

