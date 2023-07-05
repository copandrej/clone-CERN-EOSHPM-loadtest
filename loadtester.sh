#!/bin/bash

# Loadtesting script for EOS
# Runs different tools for loadtesting in /tools
# To install programs and dependencies on a new machine, run install-loadtest.sh
# Adjust variables in conf.sh before running

exit_code=0
# Load configuration

source conf.sh
if [ ! $? -eq 0 ]; then
    echo "Error: loading configuratoin failed" >&2
    exit 1
fi

# Run Grid Hammer

./tools/hammer-wrapper.sh
if [ ! $? -eq 0 ]; then
    echo "\nError: grid-hammer loadtest was not successful, check logs in $logs_dir\n" >&2
    exit_code=1
fi


# Run Filebench

# mkdir -p $logs_dir/filebench
# filebench -f $config_file | tee $logs_dir/filebench/$(date +"%F_%T").log


# Run fio

./tools/fio-wrapper.sh
if [ ! $? -eq 0 ]; then
    echo "\nError: fio loadtest was not successful, check logs in $logs_dir\n" >&2
    exit_code=1
fi


exit $exit_code
