#!/bin/bash

# This script runs the load test at different parameters.
# Specify the number of runs per configuration and the directories.

num_of_runs=1
logdir=/eos/homedev/loadtest/logs/
rundir=eoshomedev.cern.ch//eos/homedev/loadtest/runspace/

kinit -kt /etc/krb5.keytab.eostest eostest # for premissions

for num_of_files in 10 1000 2000
do
    printf "\nTesting on $num_of_files files\n"
    mkdir -p $logdir/nfiles_$num_of_files
    hammer-runner.py --url $rundir --protocols xroot --threads 10 50 100 200 --operations write read delete --runs $num_of_runs --nfiles $num_of_files --data-repo $logdir/nfiles_$num_of_files/
done
