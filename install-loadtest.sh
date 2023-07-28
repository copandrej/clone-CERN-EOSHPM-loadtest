#!/bin/bash

# Install script for grid-hammer, filebench, fio...

set -e

yum -y install wget tar bison byacc gcc make flex python3 which

repo="
[local]
name=grid-hammer
baseurl=https://storage-ci.web.cern.ch/storage-ci/grid-hammer/master/el7/x86_64/
gpgcheck=0
enabled=1
protect=1
priority=20
"

if [ -d /etc/yum-puppet.repos.d ]; then
    echo "$repo" > /etc/yum-puppet.repos.d/grid-hammer.repo # puppet
else
    echo "$repo" >> /etc/yum.repos.d/grid-hammer.repo
fi 

yum install -y grid-hammer

# Filebench

tempdir=$(mktemp -d)
cd $tempdir

wget https://github.com/filebench/filebench/releases/download/1.5-alpha3/filebench-1.5-alpha3.tar.gz 
tar -xzf filebench-1.5-alpha3.tar.gz

cd filebench-1.5-alpha3

./configure
make
make install

cd
rm -rf $tempdir


# fio

yum install -y fio
