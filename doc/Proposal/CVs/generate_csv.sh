#!/bin/bash

function usage() {
    echo "./generate_csv [subject_file_path] [output_file_path]"
}

if [ $# -ne 2 ]; then
    echo "Invalid amount of parameters"
    usage
    exit -1
fi

cat $1 | grep -v hline | grep -v "textbf" | grep \& | sed 's@^[ ]*@@' | sed 's@\\\\@@' | awk -F'&' '{print $1,",",$2,",",$3,",",$4,",",$5,",",$6}' > $2
exit 0
