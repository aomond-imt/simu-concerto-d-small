import contextlib
import csv
import json
import os
import time
import traceback

import esds
import numpy as np
from execo_engine import ParamSweeper, sweep


def compute_ons_tasks(nb_nodes, nb_deps_seq, tt):
    return [
        [(f"run0_{p_num}", tt, tuple(f"run{n_num}_{p_num}" for n_num in range(1, nb_nodes))) for p_num in range(nb_deps_seq)],
        *[[(f"run{n_num}_{p_num}", tt, ()) for p_num in range(nb_deps_seq)] for n_num in range(1, nb_nodes)],
    ]


def compute_topology(name, nb_nodes, bw):
    if name == "clique":
        return np.full((nb_nodes, nb_nodes), bw)
    if name == "star":
        B = [
            [bw]*nb_nodes,
            *[[bw, *[0]*(nb_nodes-1)] for _ in range(1, nb_nodes)]
        ]
        for i in range(nb_nodes):
            B[i][i] = bw
        return np.asarray(B)
    if name == "chain":
        B = []
        for n_num in range(nb_nodes):
            a = [0]*nb_nodes
            if n_num > 0:
                a[n_num - 1] = bw
            a[n_num] = bw
            if n_num < nb_nodes-1:
                a[n_num + 1] = bw
            B.append(a)
        return np.asarray(B)


def run_expe(current_param):
    tt = 5
    ons_tasks = compute_ons_tasks(current_param["nb_nodes"], current_param["nb_deps_seq"], tt)

    # Setup simulator
    BANDWIDTH = 50_000
    IDLE_CONSO = 1.339
    STRESS_CONSO = 2.697
    n_nodes = len(ons_tasks)
    B = compute_topology(current_param["topology"], current_param["nb_nodes"], BANDWIDTH)
    L = np.full((n_nodes, n_nodes), 0)
    smltr = esds.Simulator({"eth0": {"bandwidth": B, "latency": L, "is_wired": False}})
    termination_list = [False]*n_nodes
    with open(f"{os.environ['HOME']}/leverages/uptimes_schedules/{current_param['id_run']}-60.json") as f:
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
    total_metrics = {
        "node_cons": sum(metrics_per_nodes["node_cons"].values()),
        "comms_cons": sum(metrics_per_nodes["comms_cons"].values()),
        "upt_count": max(metrics_per_nodes["upt_count"].values()),
        "sleep_time": sum(metrics_per_nodes["sleep_time"].values()),
        "upt_time": sum(metrics_per_nodes["upt_time"].values()),
        "stress_time": sum(metrics_per_nodes["stress_time"].values()),
        "nb_msg_sent": sum(metrics_per_nodes["nb_msg_sent"].values()),
        "nb_msg_rcv": sum(metrics_per_nodes["nb_msg_rcv"].values()),
        "time": max(metrics_per_nodes["time"].values()),
    }
    total_metrics["static"] = round(total_metrics["upt_time"] * IDLE_CONSO, 2)
    total_metrics["dynamic"] = round(total_metrics["stress_time"] * STRESS_CONSO + total_metrics["comms_cons"], 2)
    total_metrics["duration"] = round(total_metrics["time"], 2)

    return total_metrics


def main():
    # Setup parameters
    parameters = {
        "type_comms": ["push", "pull_anticipation"],
        "nb_deps_seq": [5],
        "nb_nodes": [5],
        "topology": ["clique", "star", "chain"],
        "routing": [False],
        "id_run": [*range(10)]
    }
    sweeper = ParamSweeper(persistence_dir="sweeper", sweeps=sweep(parameters), save_sweeps=True)
    print(str(sweeper))
    current_param = sweeper.get_next()
    while current_param is not None:
        try:
            s = time.perf_counter()
            metrics_per_nodes = run_expe(current_param)
            simu_time = time.perf_counter() - s
            print(f"{current_param} done in: {simu_time:.2f}")
            sweeper.done(current_param)

            # Save into csv
            filename = "results_clique_star_chain.csv"
            with open(filename, "a") as f:
                csvwriter = csv.writer(f, delimiter=",")
                if os.stat(filename).st_size == 0:
                    csvwriter.writerow([*metrics_per_nodes.keys(), *current_param.keys(), "simu_time"])
                csvwriter.writerow([
                    *metrics_per_nodes.values(),
                    *current_param.values(),
                    simu_time
                ])

        except Exception as e:
            traceback.print_exc()
            sweeper.skip(current_param)
        finally:
            current_param = sweeper.get_next()


if __name__ == "__main__":
    main()
