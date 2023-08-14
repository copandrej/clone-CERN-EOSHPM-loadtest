#!/bin/bash

set -e

source conf.sh

folder=$(date +"%F-%H-%M-%S")
mkdir -p $logs_dir/fio/$folder
mkdir -p $fuse_mountpoint/fio/$folder

trap "if [ $logs_dir ] && [ $folder ]; then rm -rf $fuse_mountpoint/fio/$folder; fi;" EXIT

for njobs in "${num_of_jobs[@]}";
do
    for size in "${size_of_file[@]}";
    do
        fio --name=load_test --time_based=1 --runtime=60s --output-format=json --verify_state_save=0 --ioengine=sync --rw=rw --numjobs=$njobs --group_reporting --direct=1 --size=$size\M --verify=md5 --verify_fatal=1 --directory=$fuse_mountpoint/fio/$folder/ --output $logs_dir/fio/$folder/fio_njobs_$njobs\_size_$size.log > /dev/null
    done
done
