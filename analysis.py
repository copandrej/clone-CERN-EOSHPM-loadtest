#!/bin/python3
import json, shutil, logging, traceback, csv, os, glob
# import pandas as pd
"""
*** NOT COMPLETED ***

Analysis of the outputs of all loadtesting tools.
Gathers important metrics, pretty prints them, generates plots, 
saves to .csv for multiple run comparisons and ploting.
"""

class Results:
    def __init__(self, name: str, metrics: dict, configs: dict = {}):

        self.name: str = name
        self.metrics: dict = metrics
        self.configs = configs

    def print_configs(self) -> None:

        for k, v in self.configs.items():
            print(f"{k: <30} {v}")

        print()

    def print_metrics(self) -> None:

        for k, v in self.metrics.items():
            print(f"{k: <30} {v}")

        print()

    def save_to_csv(self):
        """
        Saves the metrics to a .csv file by timestamp and configurations.
        timestamp,name_of_test,configuration(threads-nfiles-bs),metrics*
        """

        raise NotImplementedError("TODO")


# Parsing functions
def parse_fio(filename: str):
    """
    gets important metrics from fio logs and returns them in a dictionary.

    :param filename: path to the fio Results
    :return: dictionary with the metrics
    """

    with open(filename, "r") as f:
        data = json.load(f)

    metrics: dict = {}
    configs: dict = {}

    # KiB/s to MiB/s
    metrics["Write bandwidth [MiB/s]"] = round(data["jobs"][0]["write"]["bw"] / 1024, 2)
    metrics["Write io/s"] = round(data["jobs"][0]["write"]["iops"])

    metrics["Read bandwidth [MiB/s]"] = round(data["jobs"][0]["read"]["bw"] / 1024, 2)
    metrics["Read io/s"] = round(data["jobs"][0]["read"]["iops"])

    metrics["Read mean latency [ms]"] = round(data["jobs"][0]['read']['lat_ns']['mean'] / 1_000_000, 5)  # ns to ms
    metrics["Read stdev latency [ms]"] = round(data["jobs"][0]['read']['lat_ns']['stddev'] / 1_000_000, 5)

    metrics["Write mean latency [ms]"] = round(data["jobs"][0]['write']['lat_ns']['mean'] / 1_000_000, 5)
    metrics["Write stdev latency [ms]"] = round(data["jobs"][0]['write']['lat_ns']['stddev'] / 1_000_000, 5)

    configs["Number of files"] = data["jobs"][0]["job options"]["numjobs"]
    configs["Size of files [MB]"] = data["jobs"][0]["job options"]["size"]

    return metrics, configs


def parse_filebench(filename: str):
    """
    parses filbench output and returns in a dict.

    :param filename: path to the filebench Results
    :return: dictionary with the metrics
    """

    with open(filename, "r") as f:
        lines = f.readlines()

    metrics: dict = {}
    other_operations_rate = []
    for line in lines:
        
        # starts with read or write
        if line.startswith("re"):
            line = line.split()
            metrics["Read io/s"] = float(line[2].replace("ops/s", ""))
            metrics["Read bandwidth [mb/s]"] = float(line[3].replace("mb/s", ""))
            metrics["Read min latency [ms]"] = float(line[5].replace("[", "").replace("ms", ""))
            metrics["Read max latency [ms]"] = float(line[7].replace("ms]", ""))

        elif line.startswith("wr"):
            line = line.split()
            metrics["Write io/s"] = float(line[2].replace("ops/s", ""))
            metrics["Write bandwidth [mb/s]"] = float(line[3].replace("mb/s", ""))
            metrics["Write min latency [ms]"] = float(line[5].replace("[", "").replace("ms", ""))
            metrics["Write max latency [ms]"] = float(line[7].replace("ms]", ""))
            
        # if it doesnt start with a number or Filebench than parse as well
        elif not line[0].isdigit() and not line.startswith("Filebench"):
            line = line.split()
            other_operations_rate.append(float(line[2].replace("ops/s", "")))

    metrics["Other operations rate avg"] = sum(other_operations_rate)/len(other_operations_rate)
    return metrics


def parse_grid_hammer(filename: str):
    """
    *** NOT WORKING CORRECTLY ***
    parses grid hammer output and returns in a dict.

    :param filename: path to the grid hammer Results
    :return: dictionary with the metrics
    """

    with open(filename, "r") as f:
        lines = f.readlines()

    grid_hammer_results = []
    metrics: dict = {}
    configs: dict = {}

    for ix, line in enumerate(lines):
        line = line.split()

        if "files" in line:
            if metrics:
                grid_hammer_results.append(Results("GRID HAMMER", metrics, configs))
                metrics = {}
                configs = {}

            configs["Number of files"] = int(line[0])
            configs["Number of threads"] = int(line[3])

        elif "Rate:" in line:
            operation = lines[ix-1].split()[3]
            metrics[operation + " rate [files/s]"] = float(line[1])

        elif "Latency" in line:
            operation = lines[ix-2].split()[3]
            # s to ms
            metrics[operation + " min latency [ms]"] = float(line[3]) * 1000
            metrics[operation + " max latency [ms]"] = float(line[5]) * 1000

    grid_hammer_results.append(Results("GRID HAMMER", metrics, configs))

    return grid_hammer_results


# Helper functions
def read_bash_vars(filename: str) -> dict:
    """
    Opens conf.sh and reads lodatest bash variables from it.
    """

    with open(filename, "r") as f:
        lines = f.readlines()

    vars = dict(map(lambda x: x.split("="), filter(lambda x: "=" in x, lines)))
    vars = dict(map(lambda x: (x[0], x[1].replace(
        "\n", "").split("#")[0].strip()), vars.items()))

    return vars


def print_header(name: str) -> None:
    """
    Pretty prints benchmark name in a terminal.
    """
    terminal_width, _ = shutil.get_terminal_size()
    separator_width = terminal_width - len(name) - 8
    left_separator_width = separator_width // 2
    right_separator_width = separator_width - left_separator_width
    separator = "=" * left_separator_width + "=== " + \
        name + " ===" + "=" * right_separator_width
    print("\n" + separator + "\n")


def print_separator() -> None:
    """
    Prints a full width separator in a terminal.
    """
    terminal_width, _ = shutil.get_terminal_size()
    print("-" * terminal_width, "\n")


def regenerate_plots(csv_path: str):
    raise NotImplementedError("TODO")


def get_newest_file_name(path: str) -> str:
    list_of_files = glob.glob(path + "/*")
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def main() -> int:
    conf: dict = read_bash_vars("eoshpm-loadtest/conf.sh")
    logs_dir: str = conf["logs_dir"] + "/"
    # logs_dir: str = "analysis/"
    status: int = 0

    try:
        print_header("GRID HAMMER")
        newest_log_dir = get_newest_file_name(logs_dir + "/hammer-wrapper")
        for folder in os.listdir(newest_log_dir):
            grid_hammer_results = parse_grid_hammer(newest_log_dir + "/" + folder + "/hammer-runner_ouput.log")

            for result in grid_hammer_results:
                result.print_configs()
                result.print_metrics()
                print_separator()

    except Exception as error:
        print(f"\nParsing Grid Hammer Results failed. Please check the verbose logs in logs directory: {logs_dir}\n")
        logging.error(error)
        traceback.print_exc()
        status = 1

    try:
        print_header("FILEBENCH loadtest")
        print(f"Filebench config file location: {conf['config_file']}\n")

        file_name = get_newest_file_name(logs_dir + "/filebench")
        filebench_results = Results("FILEBENCH loadtest", parse_filebench(file_name))
        filebench_results.print_metrics()

    except Exception as error:
        print(f"\nParsing Filebench Results failed. Please check the tool output logs in: {logs_dir}\n")
        logging.error(error)
        traceback.print_exc()
        status = 1

    try:
        print_header("FIO BENCHMARK")
        newest_log_dir = get_newest_file_name(logs_dir + "fio")
        for file in os.listdir(newest_log_dir):
            fio_results = []
            
            if file.startswith("fio"):
                metrics, configs = parse_fio(newest_log_dir + "/" + file)
                fio_result = Results("FIO BENCHMARK", metrics, configs)
                fio_result.print_configs()
                fio_result.print_metrics()
                print_separator()
                fio_results.append(fio_result)

    except Exception as error:
        print(f"\nParsing FIO Results failed. Please check the tool output logs in: {logs_dir}\n")
        logging.error(error)
        traceback.print_exc()
        status = 1

    print(f"\nFor more verbose logs please check the logs directory: {logs_dir}")
    return status


if __name__ == "__main__":
    exit(main())
