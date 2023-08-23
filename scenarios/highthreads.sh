#!/bin/bash

# Variables for loadtests and benchmarks, adjust this before running loadtest

# -------------------------
# General variables
# -------------------------

fuse_mountpoint=/eos/homedev/loadtest
xrootd_url=eoshomedev.cern.ch//eos/homedev/loadtest
logs_dir=/eos/homedev/loadtest/logs

# -------------------------
# grid-hammer - xrootd
# -------------------------

run_dir=/eos/homedev/loadtest       # should be the same folder as xrootd_url
num_of_files=(10000)
num_of_runs=10
threads="10 20 50 100"
operations="write read delete"
plot_graphs=false

# -------------------------
# filebench - FUSE
# -------------------------

config_file=tools/filebench-configs/highthreads.f

# -------------------------
# fio - FUSE
# -------------------------

num_of_jobs=(10 20 50 100)
size_of_file=(1M)
block_size=1M
