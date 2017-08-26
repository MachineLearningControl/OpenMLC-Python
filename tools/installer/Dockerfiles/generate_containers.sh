#!/bin/bash
RELEASE=0.1.0-alpha
PYTHON_VERSION=3.4.7

function check_run_as_root() {
    case `id` in
        uid=0*) ;;

        *)
        echo"ERROR: Must be root to run script (use -h for help)."
        exit 1
        ;;
    esac
}


function main() {
    check_run_as_root
    dockerfile_array=("ubuntu1604" 
                      "ubuntu1404" 
                      "ubuntu1610" 
                      "debian8"
                      "fedora20"
                      "centos7")

    containers_array=("mlc_ubuntu:16.04" 
                      "mlc_ubuntu:14.04" 
                      "mlc_ubuntu:16.10"
                      "mlc_debian:8"  
                      "mlc_fedora:20"
                      "mlc_centos:7")

    # (Loop until we find an empty string.)
    #
    count=0
    while [ "x${dockerfile_array[count]}" != "x" ]
    do
        docker build -f "${dockerfile_array[count]}.dockerfile" -t ${containers_array[count]} --build-arg RELEASE=$RELEASE --build-arg PYTHON_VERSION=$PYTHON_VERSION .
        # docker run --rm -v $(pwd)/release:/tmp/release -it ${containers_array[count]} bash
        count=$(( $count + 1 ))
    done    
}

main $*
