#!/bin/bash

# This script runs grid-hammer loadtest and benchmark at different parameters.
set -e

source conf.sh

folder=$(date +"%F_%T")
mkdir -p $run_dir/hammer-runspace/$folder

trap "if [ $run_dir ] && [ $folder ]; then rm -rf $run_dir/hammer-runspace/$folder; fi;" EXIT

url=$xrootd_url/hammer-runspace/$folder

mkdir -p $logs_dir/hammer-wrapper/$folder
logs=$logs_dir/hammer-wrapper/$folder

for num_of_files in "${num_of_files[@]}";
do
    mkdir -p $logs/nfiles_$num_of_files
    
    hammer-runner.py --initialization --constantnfiles --url $url/ --protocols xroot --strict-exit-code 1 --threads $threads --operations $operations \
        --runs $num_of_runs --nfiles $num_of_files --data-repo $logs/nfiles_$num_of_files/ \
        | sed -e 's/\x1b\[[0-9;]*m//g' > $logs/nfiles_$num_of_files/hammer-runner_ouput.log # sed clears the color codes from the output

    test ${PIPESTATUS[0]} -eq 0 # exit code 1 if hammer-runner.py fails
    
    if [ "$plot_graphs" = true ]; then
        printf "\nPlotting graphs...\n"
        mkdir -p $logs/graphs/nfiles_$num_of_files
        hammer-visualizer.py --path $logs/nfiles_$num_of_files/*/ad-hoc-$num_of_files-files/eoshpmload.cern.ch/ --output-dir $logs/graphs/nfiles_$num_of_files/
    fi
done
