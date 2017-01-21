#/bin/bash

files=$(ls | grep "ui$")

for i in $files; do
   output=$(echo $i | sed "s/\(.*\)\.ui/\1\.py/")
#   rm $output
   echo "Generating $i --> $output"
   /opt/mlc-python-2.7.11/bin/mlc_python -m PyQt5.uic.pyuic $i -o $output
done;

