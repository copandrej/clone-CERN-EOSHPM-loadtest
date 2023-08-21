#!/bin/python3
import json, shutil, logging, traceback, os, glob, sys

"""
Analysis of the outputs of all loadtesting tools.
Gathers important metrics, pretty prints them.
Optionally does analysis of older results by running
the script with --old <num> argument.

Usage:

python3 analysis.py
python3 analysis.py --old <num>

To run the full loadtest with analysis:
./loadtest.sh
./loadtest.sh --compare

More info in README.md
"""

class Results:
    """
    Stores results of a single run.
    Methods for printing configs and metrics.
    """
    
    def __init__(self, name: str, metrics: dict, configs: dict = {}):

        self.name: str = name
        self.metrics: dict = metrics
        self.configs: dict = configs

    def print_configs(self) -> None:

        for k, v in self.configs.items():
            print(f"{k: <30} {v}")

        print()

    def print_metrics(self) -> None:

        for k, v in self.metrics.items():
            print(f"{k: <30} {v}")

        print()



# Parsing functions
def parse_fio(filename: str) -> tuple:
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
    metrics["Write throughput [MiB/s]"] = round(data["jobs"][0]["write"]["bw"] / 1024, 2)
    metrics["Write io/s"] = round(data["jobs"][0]["write"]["iops"])

    metrics["Read throughput [MiB/s]"] = round(data["jobs"][0]["read"]["bw"] / 1024, 2)
    metrics["Read io/s"] = round(data["jobs"][0]["read"]["iops"])

    metrics["Read mean latency [ms]"] = round(data["jobs"][0]['read']['lat_ns']['mean'] / 1_000_000, 5)  # ns to ms
    metrics["Read stdev latency [ms]"] = round(data["jobs"][0]['read']['lat_ns']['stddev'] / 1_000_000, 5)

    metrics["Write mean latency [ms]"] = round(data["jobs"][0]['write']['lat_ns']['mean'] / 1_000_000, 5)
    metrics["Write stdev latency [ms]"] = round(data["jobs"][0]['write']['lat_ns']['stddev'] / 1_000_000, 5)

    configs["Number of threads"] = data["jobs"][0]["job options"]["numjobs"]
    configs["Size of files"] = data["jobs"][0]["job options"]["size"]
    configs["Block size"] = data["jobs"][0]["job options"]["bs"]

    return metrics, configs


def parse_filebench(filename: str) -> dict:
    """
    parses filbench output and returns in a dict.

    :param filename: path to the filebench Results
    :return: dictionary with the metrics
    """

    with open(filename, "r") as f:
        lines = f.readlines()

    metrics: dict = {}
    for line in lines:
        
        # starts with read or write
        if line.startswith("re"):
            line = line.split()
            
            metrics["Read throughput [mb/s]"] = float(line[3].replace("mb/s", ""))
            metrics["Read mean latency [ms/o]"] = float(line[4].replace("ms/op", ""))
            metrics["Read min latency [ms]"] = float(line[5].replace("[", "").replace("ms", ""))
            metrics["Read max latency [ms]"] = float(line[7].replace("ms]", ""))

        elif line.startswith("wr"):
            line = line.split()
            
            metrics["Write throughput [mb/s]"] = float(line[3].replace("mb/s", ""))
            metrics["Write mean latency [ms/o]"] = float(line[4].replace("ms/op", ""))
            metrics["Write min latency [ms]"] = float(line[5].replace("[", "").replace("ms", ""))
            metrics["Write max latency [ms]"] = float(line[7].replace("ms]", ""))
            
    return metrics

def parse_grid_hammer(filename: str) -> list:

    """
    parses grid hammer output and returns in a dict.

    :param filename: path to the grid hammer Results
    :return: dictionary with the metrics
    """

    with open(filename, "r") as f:
        lines = f.readlines()

    grid_hammer_results: list = []
    metrics: dict = {}
    configs: dict = {}
    status: int = 0

    for ix, line in enumerate(lines):
        line = line.split()

        # if failure print the number of failures
        if "FAIL" in line:
            metrics["WARNING: " + line[3] + " errors"] = int(lines[ix+2].split()[0])
            status = 1
            
        if "files" in line:
            if metrics:
                grid_hammer_results.append(Results("GRID HAMMER", metrics, configs))
                metrics = {}
                configs = {}

            status = 0

            configs["Number of files"] = int(line[0])
            configs["Number of threads"] = int(line[3])

        if status == 1:
            continue
        
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
    vars = dict(map(lambda x: (x[0], x[1].replace("\n", "").split("#")[0].strip()), vars.items()))

    return vars


def print_header(name: str) -> None:
    """
    Pretty prints benchmark name in a terminal.
    """
    terminal_width, _ = shutil.get_terminal_size()
    separator_width = terminal_width - len(name) - 8
    left_separator_width = separator_width // 2
    right_separator_width = separator_width - left_separator_width
    separator = "=" * (left_separator_width//2) + "=== " + name + " ===" + "=" * (right_separator_width//2)
    print("\n" + separator + "\n")


def print_separator() -> None:
    """
    Prints a full width separator in a terminal.
    """
    terminal_width, _ = shutil.get_terminal_size()
    print("-" * (terminal_width//2), "\n")


def get_newest_file_name(path: str, num: int = 1) -> str:
    """
    Orders by creation time, depending on num returns the latest or older file name.
    """
    list_of_files = glob.glob(path + "/*")
    list_of_files.sort(key=os.path.getctime)
    
    try :
        return list_of_files[-num]
    except IndexError:
        raise Exception(f"\nERROR: Correct logs were not found! Check the --old or --custom arguments or change log path")


def print_filebench_configs(filename: str) -> None:
    """
    Prints filebench variables from the config file, skips $dir.
    """
    with open(filename, "r") as f:
        lines = f.readlines()
        
    for line in lines:
        if line.startswith("set"):
            if "dir" in line:
                continue
            print(line.replace("set $", "").replace("=", ": ").replace("\n", ""))
            
    print()


def main() -> int:
    conf: dict = read_bash_vars("conf.sh")
    logs_dir: str = conf["logs_dir"] + "/"
    status: int = 0
    
    if "--old" in sys.argv:
        num: int = int(sys.argv[sys.argv.index("--old") + 1])
    else:
        num: int = 1
    
    hammer_logs = get_newest_file_name(logs_dir + "/hammer-wrapper", num)
    filebench_logs = get_newest_file_name(logs_dir + "/filebench", num)
    fio_logs = get_newest_file_name(logs_dir + "fio", num)
    
    time_of_run = hammer_logs.split("/")[-1]
    print("\nApproximate loadtest time: ", time_of_run)
    
    export_data = {
        "hammer": [],
        "filebench": [],
        "fio": []
    }
    
    try:
        print_header("GRID HAMMER")
        for folder in os.listdir(hammer_logs):
            grid_hammer_results = parse_grid_hammer(hammer_logs + "/" + folder + "/hammer-runner_ouput.log")

            num_results = 1
            avg_results = Results("GRID HAMMER", {}, {})
            
            for ix, result in enumerate(grid_hammer_results):
                if ix + 1 < len(grid_hammer_results) and result.configs == grid_hammer_results[ix+1].configs:
                    num_results += 1
                    if num_results == 2:
                        avg_results.configs = result.configs
                        avg_results.metrics = result.metrics
                        
                    for k, v in grid_hammer_results[ix+1].metrics.items():
                        avg_results.metrics[k] += v
                    continue
                    
                elif num_results > 1:
                    for k, v in avg_results.metrics.items():
                        avg_results.metrics[k] = round(v / num_results, 2)
                        
                    print(f"Average over {num_results} runs:")
                    avg_results.print_configs()
                    avg_results.print_metrics()
                    print_separator()
                    
                    export_data["hammer"].append({ "result" : avg_results.metrics, "configs" : avg_results.configs, "time" : time_of_run  })
                    avg_results = Results("GRID HAMMER", {}, {})
                    num_results = 1
                
                else:
                    result.print_configs()
                    result.print_metrics()
                    print_separator()
                    export_data["hammer"].append({ "result" : result.metrics, "configs" : result.configs, "time" : time_of_run  })


    except Exception as error:
        print(f"\nParsing Grid Hammer Results failed. Please check the verbose logs in logs directory: {logs_dir}\n")
        logging.error(error)
        traceback.print_exc()
        status = 1

    try:
        print_header("FILEBENCH loadtest")
        print(f"Filebench config file location: {conf['config_file']}\n")
        print_filebench_configs(conf['config_file'])
        filebench_results = Results("FILEBENCH loadtest", parse_filebench(filebench_logs))
        filebench_results.print_metrics()
        export_data["filebench"].append({ "result" : filebench_results.metrics, "configs" : filebench_results.configs, "time" : time_of_run  })

    except Exception as error:
        print(f"\nParsing Filebench Results failed. Please check the tool output logs in: {logs_dir}\n")
        logging.error(error)
        traceback.print_exc()
        status = 1

    try:
        print_header("FIO BENCHMARK")
        for file in os.listdir(fio_logs):
            
            if file.startswith("fio"):
                metrics, configs = parse_fio(fio_logs + "/" + file)
                fio_result = Results("FIO BENCHMARK", metrics, configs)
                fio_result.print_configs()
                fio_result.print_metrics()
                print_separator()
                export_data["fio"].append({ "result" : fio_result.metrics, "configs" : fio_result.configs, "time" : time_of_run  })

    except Exception as error:
        print(f"\nParsing FIO Results failed. Please check the tool output logs in: {logs_dir}\n")
        logging.error(error)
        traceback.print_exc()
        status = 1

    print(f"\nFor more verbose logs please check the logs directory: {logs_dir}")
    
    # save export_data to file
    if not os.path.exists("analysis-out"):
        os.makedirs("analysis-out")
    
    if not os.path.exists("analysis-out/export_data_" + time_of_run + ".json"):
        with open("analysis-out/export_data_" + time_of_run + ".json", "w") as f:
            json.dump(export_data, f)

    return status


if __name__ == "__main__":
    exit(main())
