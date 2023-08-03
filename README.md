# EOSHPM loadtest

The purpose of this tool is to automate load testing and benchmarking of the EOS storage system, assess its performance, and compare results while changing configurations of hardware or software on EOS machines. 

It is a modular wrapper around existing load testing and benchmarking tools (grid-hammer, filebench, fio). It permutates over tools parameters and collects logs in an organized directory structure. 

The analysis script parses output logs of tools and prints/compares the results of completed runs. 

The tool is containerized with Docker, thus allowing it to run on any VM with access to EOS.

### Components and scripts
- `conf.sh` - configuration file for setting all important variables and parameters for the loadtester
- `install-loadtest.sh` - installs dependencies and benchmarking tools on a clean machine
- `loadtest.sh` - main script, runs the tools, visualizer and data analysis
- `tools/` - directory with wrapper scripts for benchmarking tools, can be run individually
- `analysis.py` - Python script for parsing and comparing results of benchmarking tools
- `Dockerfile` - Dockerfile for building the image, similar to `install-loadtest.sh`


## Installation and requirements

The tool can be used as a docker image. In case one wants to install it directly on a machine, the following requirements should be met:

- `yum`, `git`, `python2`
- OPTIONAL: python2 module: `matplotlib` (for hammer visualizer)

Everything else will be installed by the `install-loadtest.sh` script.

> ⚠️ NOTE:
>
> If installing the software without the install script, log parsing is not guaranteed to work on all software versions. The developed tool was tested with the following versions:
>
> - grid-hammer-0.0.1.115.c3c1158-1.el7.cern.x86_64
> - filebench-1.5-alpha3
> - fio-3.7

### Install

```bash
git clone https://gitlab.cern.ch/AIGROUP-eos-admins/eoshpm-loadtest.git
cd eoshpm-loadtest
./install-loadtest.sh
```


## Usage 

> ⚠️ Important:
>
> Before using the tool user should check system limits on the testing VM: `ulimit -n`, if the limit for `open files` is set to default `1024` grid hammer will fail at high thread count. Limit should be increased as `ulimit -n 1048576`. Note that by running `./install-loadtest.sh` or using docker image this will be fixed automatically.

Open configuration file `conf.sh`. At minimum, change the variables for mountpoints, directories and urls.

Run the tool as:

```bash
./loadtest.sh
```

Or run individual tools from `tools/` directory:
```bash
./tools/hammer-wrapper.sh
./tools/fio-wrapper.sh
./tools/filebench-wrapper.sh
```
Additionaly `--compare` flag can be used with `loadtest.sh` to compare results of two latest runs.
Without running the test, user can use `analysis.py` script to check the results of previous runs. Or compare them with older runs by using `--old` flags and some bash commands:
```bash
# Pretty prints the results of the latest run
./analysis.py

# Prints the results of any run with --old <num> flag, where 1 is the latest run
./analysis.py --old 2

# Compares the results of two latest runs
paste <(./analysis.py) <(./analysis.py --old 2) | column -s $'\t' -t
``````

Note that filebench has its own config file in `tools/filbench-config/filserver.f`, where flow of operations and parameters can be adjusted.

## Docker

Latest image location from master:

[gitlab-registry.cern.ch/aigroup-eos-admins/eoshpm-loadtest:latest](gitlab-registry.cern.ch/aigroup-eos-admins/eoshpm-loadtest:latest)

Container should be ran as:
```bash
docker run -it --net=host --entrypoint /bin/bash -v <eos-mountpoint>:/eos/homedev/loadtest -v /etc/<krb5.keytab.* file>:/host-etc/<krb5.keytab.* file> eoshpm-loadtest
```
Change `<eos-mountpoint>` to where EOS is mounted on the host machine.

Second volume (`<krb5.keytab.* file>`) should point to Kerberos keytab file, which is needed for writing to EOS. Only one keytab file should be mounted or the tool will fail.

To directly run the tool through container use entrypoint: `--entrypoint /eoshpm-loadtest/loadtester.sh`.

## Further development
The tool is designed to be modular, so adding new tools should be straightforward, with the exception of the analysis script, which requires complex parsing of the output logs of each tool.

To add a new tool, a developer should create a wrapper script in the `tools/` directory named similar to `<tool>-wrapper.sh`. The wrapper script should run the tool in the appropriate runspace and collect the output logs in a structured directory in a similar way to other tools.

All important configurations and bash variables need to be set in the `conf.sh` file.

Requirements and installation of the tool can be added to the `install-loadtest.sh` script as well as Dockerfile.

Optionally, calling of the wrapper script can be added to `loadtest.sh`, and functions for passing output can be added to `analysis.py`.

Documentation and the structure of the code are clear from comments inside the source code.

After commiting changes to the repository and merging with master, gitlab CI/CD will automatically build a new docker image and push it to the registry.

## Authors and acknowledgment
Project by CERN Openlab summer student [Andrej Čop](mailto:andrej7.cop@gmail.com), supervisor Emmanouil Bagakis and with help of the EOSHPM team. The project is part of CERN IT-SD-GSS section.

Project would not be possible without existing tools:
- [grid-hammer](https://gitlab.cern.ch/lcgdm/grid-hammer/-/tree/master)

- [filebench](https://github.com/filebench/filebench)

- [fio](https://fio.readthedocs.io/en/latest/fio_doc.html)
