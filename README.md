# EOSHPM loadtest

The purpose of this tool is to automate workflow and load generator as well as run benchmarking tools for testing the EOS storage system. It is a modular wrapper around existing loadtesting and benchmarking tools (grid-hammer, filebench, fio), it permutates over tools parameters and colects logs in organized directory structure.

### Components and scripts
- `conf.sh` - configuration file for setting all important variables and parameters for the loadtester
- `install-loadtest.sh` - installs dependencies and benchmarking tools on a clean machine
- `loadtest.sh` - main script, runs the tools, visualizer and data analysis
- `tools/` - directory with wrapper scripts for benchmarking tools, can be run individually


## Installation and requirements

Prior to installation, make sure the following packages are installed:
- `git`, `python2`, `python3`, `wget`, `tar`
- python modules: `matplotlib`

### Install

```bash
git clone https://gitlab.cern.ch/AIGROUP-eos-admins/eoshpm-loadtest.git
cd eoshpm-loadtest
./install-loadtest.sh
```

## Usage
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

Note that filebench has its own config file in `tools/filbench-config/filserver.f`, where flow of operations and parameters can be adjusted.

## Authors and acknowledgment
Project by CERN summer student [Andrej Čop](mailto:andrej7.cop@gmail.com), supervisor Emmanouil Bagakis and with help of the EOSHPM team. The project is part of CERN IT-SD-GSS section.

Project would not be possible without existing tools:
- [grid-hammer](https://gitlab.cern.ch/lcgdm/grid-hammer/-/tree/master)

- [filebench](https://github.com/filebench/filebench)

- [fio](https://fio.readthedocs.io/en/latest/fio_doc.html)

## License
For open source projects, say how it is licensed.
