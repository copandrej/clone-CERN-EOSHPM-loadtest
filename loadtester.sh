#!/bin/bash

# Loadtesting script for EOS
# Runs different tools for loadtesting in /tools
# To install programs and dependencies on a new machine, run install-loadtest.sh
# Adjust variables in conf.sh before running

set -e

source conf.sh

./tools/hammer-wrapper.sh

# mkdir -p $logs_dir/filebench
# filebench -f $config_file | tee $logs_dir/filebench/$(date +"%F_%T").log
