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
num_of_files=(10 1000 2000)
num_of_runs=1
threads="10 50 100 200"
operations="write read delete"

# -------------------------
# filebench - FUSE
# -------------------------

config_file=tools/filebench-configs/fileserver.f

# -------------------------
# fio - FUSE
# -------------------------

num_of_jobs=(10 50)
size_of_file=(50 100)               # in MB
