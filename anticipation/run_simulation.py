import contextlib
import csv
import json
import os
import time
import traceback

import esds
import numpy as np
from execo_engine import ParamSweeper, sweep


def run_expe(current_param):
    ons_tasks = [
        [(f"run{n_num}_{p_num}", 10, (f"run{n_num+1}_{p_num}",)) for p_num in range(current_param["nb_place"])]
        for n_num in range(current_param["chains_length"] - 1)
    ]
    ons_tasks.append([(f"run{current_param['chains_length']-1}_{p_num}", 10, ()) for p_num in range(current_param["nb_place"])])

    # Setup simulator
    BANDWIDTH = 50_000
    IDLE_CONSO = 1.339
    STRESS_CONSO = 2.697
    n_nodes = len(ons_tasks)
    B = np.full((n_nodes, n_nodes), BANDWIDTH)
    L = np.full((n_nodes, n_nodes), 0)
    smltr = esds.Simulator({"eth0": {"bandwidth": B, "latency": L, "is_wired": False}})
    termination_list = [False]*n_nodes
    with open(f"/home/aomond/leverages/uptimes_schedules/{current_param['id_run']}-60.json") as f:
        uptimes_schedules = json.load(f)
    for _ in range(n_nodes):
        smltr.create_node("on", interfaces=["eth0"], args={
            "termination_list": termination_list,
            "ons_tasks": ons_tasks,
            "uptimes_schedules": uptimes_schedules,
            "type_comms": current_param["type_comms"]
        })

    # Run simulation
    results_log_path = f"/tmp/{time.time_ns()}.txt"
    # results_log_path = f"/tmp/1707566152275199436.txt"
    with open(results_log_path, "w") as f:
        with contextlib.redirect_stdout(f):
            smltr.run(interferences=False)

    # Scrap metrics from logs
    metrics_per_nodes = {"node_cons": {}, "comms_cons": {}, "upt_count": {}, "sleep_time": {}, "upt_time": {}, "stress_time": {}, "nb_msg_sent": {}, "nb_msg_rcv": {}, "time": {}}
    with open(results_log_path) as f:
        for line in f.readlines():
            l_split = line.split()
            if l_split[1][:-1] in metrics_per_nodes.keys():
                node_num = int(l_split[0].split(",")[1].replace("src=n", ""))
                metrics_per_nodes.setdefault(l_split[1][:-1], {})[node_num] = float(l_split[2])

    # Process metrics
    metrics_per_nodes["node_cons"]["total"] = sum(metrics_per_nodes["node_cons"].values())
    metrics_per_nodes["comms_cons"]["total"] = sum(metrics_per_nodes["comms_cons"].values())
    metrics_per_nodes["upt_count"]["total"] = max(metrics_per_nodes["upt_count"].values())
    metrics_per_nodes["sleep_time"]["total"] = sum(metrics_per_nodes["sleep_time"].values())
    metrics_per_nodes["upt_time"]["total"] = sum(metrics_per_nodes["upt_time"].values())
    metrics_per_nodes["stress_time"]["total"] = sum(metrics_per_nodes["stress_time"].values())
    metrics_per_nodes["nb_msg_sent"]["total"] = sum(metrics_per_nodes["nb_msg_sent"].values())
    metrics_per_nodes["nb_msg_rcv"]["total"] = sum(metrics_per_nodes["nb_msg_rcv"].values())
    metrics_per_nodes["time"]["total"] = max(metrics_per_nodes["time"].values())
    metrics_per_nodes["static"] = metrics_per_nodes["upt_time"]["total"]*IDLE_CONSO
    metrics_per_nodes["dynamic"] = metrics_per_nodes["stress_time"]["total"]*STRESS_CONSO + metrics_per_nodes["comms_cons"]["total"]
    metrics_per_nodes["duration"] = metrics_per_nodes["time"]["total"]

    # Print metrics
    # for k, m in metrics_per_nodes.items():
    #     print(k, m)

    # Save into csv
    filename = "results.csv"
    with open(filename, "a") as f:
        csvwriter = csv.writer(f, delimiter=",")
        if os.stat(filename).st_size == 0:
            csvwriter.writerow(["static", "dynamic", "duration", *current_param.keys()])
        csvwriter.writerow([
            round(metrics_per_nodes["static"], 2),
            round(metrics_per_nodes["dynamic"], 2),
            round(metrics_per_nodes["duration"], 2),
            *current_param.values()
        ])


def main():
    # Setup parameters
    parameters = {
        "type_comms": ["push", "pull"],
        "nb_place": [2, 3, 4, 5],
        "deps_pos": ["place"],  # comp, place, trans
        "chains_length": [2, 3, 4, 5],
        "nb_chains": [1],
        "topology": ["clique"],
        "id_run": [*range(10)]
    }
    sweeper = ParamSweeper(persistence_dir="sweeper", sweeps=sweep(parameters), save_sweeps=True)
    print(str(sweeper))
    current_param = sweeper.get_next()
    while current_param is not None:
        try:
            s = time.perf_counter()
            run_expe(current_param)
            sweeper.done(current_param)
            print(f"{current_param} done in: {(time.perf_counter() - s):.2f}")
        except Exception as e:
            traceback.print_exc()
            sweeper.skip(current_param)
        finally:
            current_param = sweeper.get_next()


if __name__ == "__main__":
    main()
