import contextlib
import time

import esds
import numpy as np

# Setup simulator
BANDWIDTH = 50_000
IDLE_CONSO = 1.339
STRESS_CONSO = 2.697
n_nodes = 4
B = np.full((n_nodes, n_nodes), BANDWIDTH)
L = np.full((n_nodes, n_nodes), 0)
smltr = esds.Simulator({"eth0": {"bandwidth": B, "latency": L, "is_wired": False}})
termination_list = [False]*n_nodes
for _ in range(n_nodes):
    smltr.create_node("on", interfaces=["eth0"], args=termination_list)

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
for k, m in metrics_per_nodes.items():
    print(k, m)
