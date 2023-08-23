#!/bin/python3
import json, sys
from analysis import get_newest_file_name, print_header, print_separator

"""
Summary of relative changes between two test analysis. It outputs percentage changes for important metrics.
Average changes over different parameters for each test and operation.
Should be ran after analysis.py and after running tests with same configs.
Normaly it is called by loadtester.sh it is not meant as a standalone script.

Usage: python3 summary.py [--custom] [newer] [older]

argument is the number of the .json output sorted from newest to oldest (1 = newest)

More info in README.md
"""

def fio_changes(test: dict, data: dict) -> tuple:
    """
    Calculates percentage changes between two fio tests with same configs. Positive values mean that metrics are better.
    """
    
    for test_new in data["fio"]:
        if test_new["configs"] == test["configs"]:
            
            read_change = 100 * (test_new["result"]["Read throughput [MiB/s]"] - test["result"]
                                ["Read throughput [MiB/s]"])/test["result"]["Read throughput [MiB/s]"]
            
            write_change = 100 * (test_new["result"]["Write throughput [MiB/s]"] - test["result"]
                                ["Write throughput [MiB/s]"])/test["result"]["Write throughput [MiB/s]"]
            
            read_mean_latency_change = 100 * (test["result"]["Read mean latency [ms]"] - test_new["result"]
                                                ["Read mean latency [ms]"])/test["result"]["Read mean latency [ms]"]
            
            write_mean_latency_change = 100 * (test["result"]["Write mean latency [ms]"] - test_new["result"]
                                                ["Write mean latency [ms]"])/test["result"]["Write mean latency [ms]"]
            
            return read_change, write_change, read_mean_latency_change, write_mean_latency_change
    
    raise Exception("ERROR: Fio tests that are being compared don't have the same configs!")

def hammer_changes(test: dict, data: dict) -> tuple:
    """
    Calculates percentage changes between two grid hammer tests with same configs.
    """
    
    for test_new in data["hammer"]:
        if test_new["configs"] == test["configs"]:
            
            read_change = 100 * (test_new["result"]["read rate [files/s]"] - test["result"]
                                ["read rate [files/s]"])/test["result"]["read rate [files/s]"]
            
            write_change = 100 * (test_new["result"]["write rate [files/s]"] - test["result"]
                                ["write rate [files/s]"])/test["result"]["write rate [files/s]"]
            
            return read_change, write_change
        
    raise Exception("ERROR: Hammer tests that are being compared don't have the same configs!")
    

def main() -> None:

    # parse arguments
    if "--custom" in sys.argv:
        newer: int = int(sys.argv[sys.argv.index("--custom") + 1])
        older: int = int(sys.argv[sys.argv.index("--custom") + 2])
    else:
        newer: int = 1
        older: int = 2
        
    # read json exported output from analysis.py
    analysis_out_path: str = "analysis-out/"
    
    with open(get_newest_file_name(analysis_out_path, older), "r") as f:
        data: dict = json.load(f)

    with open(get_newest_file_name(analysis_out_path, newer), "r") as f:
        data_new: dict = json.load(f)

    # print summary
    print_header("Summary")
    print("Filebench changes:\n")

    print("Read throughput: {:.2f}%".format(100*(data_new["filebench"][0]["result"]["Read throughput [mb/s]"] -
          data["filebench"][0]["result"]["Read throughput [mb/s]"])/data["filebench"][0]["result"]["Read throughput [mb/s]"]))

    print("Write throughput: {:.2f}%".format(100*(data_new["filebench"][0]["result"]["Write throughput [mb/s]"] -
          data["filebench"][0]["result"]["Write throughput [mb/s]"])/data["filebench"][0]["result"]["Write throughput [mb/s]"]))

    print("Read latency: {:.2f}%".format(100*(data["filebench"][0]["result"]["Read mean latency [ms/o]"] - data_new["filebench"]
          [0]["result"]["Read mean latency [ms/o]"])/data["filebench"][0]["result"]["Read mean latency [ms/o]"]))

    print("Write latency: {:.2f}%".format(100*(data["filebench"][0]["result"]["Write mean latency [ms/o]"] - data_new["filebench"]
          [0]["result"]["Write mean latency [ms/o]"])/data["filebench"][0]["result"]["Write mean latency [ms/o]"]))

    print("\nFio average changes:\n")
    read_change, write_change, read_mean_latency_change, write_mean_latency_change = 0, 0, 0, 0
    
    for test in data["fio"]:
        tpl = fio_changes(test, data_new)
        read_change += tpl[0]
        write_change += tpl[1]
        read_mean_latency_change += tpl[2]
        write_mean_latency_change += tpl[3]

    print("Read throughput: {:.2f}%".format(read_change/len(data["fio"])))
    print("Write throughput: {:.2f}%".format(write_change/len(data["fio"])))
    print("Read latency: {:.2f}%".format(read_mean_latency_change/len(data["fio"])))
    print("Write latency: {:.2f}%".format(write_mean_latency_change/len(data["fio"])))
    
    print("\nHammer average changes:\n")
    read_change, write_change = 0, 0
    
    for test in data["hammer"]:
        tpl = hammer_changes(test, data_new)
        read_change += tpl[0]
        write_change += tpl[1]
        
    print("Read rate: {:.2f}%".format(read_change/len(data["hammer"])))
    print("Write rate: {:.2f}%".format(write_change/len(data["hammer"])))
    
    print_separator()
    
    print("Note that negative values mean that metrics are worse.")
    print("Small changes should be taken with a grain of salt.")
    print("Please check side by side comparison and raw logs before making any conclusions.\n")
    

if __name__ == "__main__":
    main()
