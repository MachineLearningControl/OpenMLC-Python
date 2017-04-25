#!/bin/bash
RELEASE=0.0.4

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
    docker build -f ubuntu1404.dockerfile -t mlc_ubuntu:14.04 --build-arg RELEASE=$RELEASE .
    docker build -f ubuntu1604.dockerfile -t mlc_ubuntu:16.04 --build-arg RELEASE=$RELEASE .
    docker build -f ubuntu1610.dockerfile -t mlc_ubuntu:16.10 --build-arg RELEASE=$RELEASE .
    docker build -f debian8.dockerfile -t mlc_debian:8 --build-arg RELEASE=$RELEASE .
    docker build -f centos7.dockerfile -t mlc_centos:7 --build-arg RELEASE=$RELEASE .
    docker build -f fedora20.dockerfile -t mlc_fedora:20 --build-arg RELEASE=$RELEASE .
}

main $*

