#!/bin/bash

set -e

source conf.sh

dat=$(date +"%F-%H-%M-%S")

mkdir -p $logs_dir/filebench/
mkdir -p $fuse_mountpoint/filebench/$dat

# Replace the dir in the config file
temp_config_file=$(mktemp)
sed "/^set \$dir/c\set \$dir=$fuse_mountpoint/filebench/$dat/" $config_file > $temp_config_file

filebench -f $temp_config_file > $logs_dir/filebench/$dat.log

rm -f $temp_config_file
if [ $fuse_mountpoint ] && [ $dat ]; then
    rm -rf $fuse_mountpoint/filebench/$dat
else
    printf "WARNING: deleting runspace faild, delete it manually: $fuse_mountpoint/filebench/$dat\n"
fi
