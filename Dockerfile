FROM gitlab-registry.cern.ch/linuxsupport/cc7-base

# Dependencies
RUN yum -y install wget tar bison byacc gcc make flex python3 nano which

# Grid hammer
RUN echo -e "[grid-hammer]\nname=grid-hammer continuous builds for master\nbaseurl=http://storage-ci.web.cern.ch/storage-ci/grid-hammer/xrootd5/master/el7/x86_64/\ngpgcheck=0\nenabled=1\nprotect=1\npriority=20\n" > /etc/yum.repos.d/grid-hammer.repo
RUN yum install -y grid-hammer-0.0.1.118.5e76778-1.el7.cern.x86_64

# Fio
RUN yum install -y fio-3.7

# Filebench
RUN tempdir=$(mktemp -d) && cd $tempdir \
        && wget https://github.com/filebench/filebench/releases/download/1.5-alpha3/filebench-1.5-alpha3.tar.gz \
        && tar -xzf filebench-1.5-alpha3.tar.gz \
        && cd filebench-1.5-alpha3 \
        && ./configure \
        && make \
        && make install \
        && cd \
        && rm -rf $tempdir

# Copy loadtest
COPY ./ /eoshpm-loadtest

ENTRYPOINT /bin/bash
