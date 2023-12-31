#!/bin/bash

# Loadtesting script for EOS
# Runs different tools for loadtesting in /tools
# To install programs and dependencies on a new machine, run install-loadtest.sh
# Adjust variables in conf.sh before running

# if inside docker then /etc-host exists (container volume) run kinit from there

ulimit -n 1048576 # Open files limit fix

WORKING_DIRECTORY=$(pwd)
cd "$(dirname "$0")"

exit_code=0

# Load configuration

echo -e "\nLoading configuration from conf.sh\n"
source conf.sh
if [ ! $? -eq 0 ]; then
    echo -e "ERROR: loading configuratoin failed\n" >&2
    exit 1
fi

#Authenticate with Kerberos for container, check if already authenticated and check if keytab is mounted

klist -s
if [ ! $? -eq 0 ]; then
    if [ -d /host-etc ]; then
        if (( $(ls /host-etc | wc -l) != 1)); then 
            echo "WARNING: Kerberos keytab file is not properly mounted in /host-etc/, container might not have access to EOS" >&2; 
        else
            echo "Authenticating with Kerberos..."
            keytab_file=$(ls /host-etc)
            kinit -kt /host-etc/$keytab_file ${keytab_file#*keytab.}
        fi
    fi
fi

# Run Grid Hammer

echo -e "Running grid-hammer loadtest...\n"
./tools/hammer-wrapper.sh
if [ ! $? -eq 0 ]; then
    echo -e "ERROR: grid-hammer loadtest was not successful, check logs in $logs_dir\n" >&2
    exit_code=1
fi


# Run Filebench

echo -e "Running filebench loadtest...\n"
./tools/filebench-wrapper.sh
if [ ! $? -eq 0 ]; then
    echo -e "ERROR: filebench loadtest was not successful, check logs in $logs_dir\n" >&2
    exit_code=1
fi


# Run fio

echo -e "Running fio loadtest...\n"
./tools/fio-wrapper.sh
if [ ! $? -eq 0 ]; then
    echo -e "ERROR: fio loadtest was not successful, check logs in $logs_dir\n" >&2
    exit_code=1
fi


if [[ "$*" == *"compare"* ]]
then
    paste <(./analysis.py --old 2) <(./analysis.py) | column -s $'\t' -t &&
    ./summary.py
else
    ./analysis.py
fi

cd $WORKING_DIRECTORY
exit $exit_code
