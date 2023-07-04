#!/bin/bash

# This script runs grid-hammer loadtest and benchmark at different parameters.
set -e

source conf.sh

folder=$(date +"%F_%T")
mkdir -p $run_dir/$folder
url=$xrootd_url/hammer-runspace/$folder

mkdir -p $logs_dir/hammer-wrapper/$folder
logs=$logs_dir/hammer-wrapper/$folder

for num_of_files in "${num_of_files[@]}";
do
    printf "\nTesting on $num_of_files files"
    mkdir -p $logs/nfiles_$num_of_files
    hammer-runner.py --url $url/ --protocols xroot --strict-exit-code 1 --threads $threads --operations $operations --runs $num_of_runs --nfiles $num_of_files --data-repo $logs/nfiles_$num_of_files/ | tee -a $logs/nfiles_$num_of_files/hammer-runner_ouput.log
done

rmdir $run_dir/$folder
