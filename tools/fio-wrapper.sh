#!/bin/bash

set -e

source conf.sh

folder=$(date +"%F-%H-%M-%S")
mkdir -p $logs_dir/fio/$folder
mkdir -p $fuse_mountpoint/fio/$folder

for njobs in "${num_of_jobs[@]}";
do
    for size in "${size_of_file[@]}";
    do
        fio --name=load_test --output-format=json --verify_state_save=0 --ioengine=sync --rw=rw --numjobs=$njobs --group_reporting --direct=1 --size=$size\M --verify=md5 --verify_fatal=1 --directory=$fuse_mountpoint/fio/$folder/ --output $logs_dir/fio/$folder/fio_njobs_$njobs\_size_$size.log > /dev/null
    done
done

if [ $fuse_mountpoint ] && [ $folder ]; then
    rm -rf $fuse_mountpoint/fio/$folder
else
    printf "WARNING: deleting runspace faild, delete it manually: $fuse_mountpoint/fio/$folder\n"
fi
