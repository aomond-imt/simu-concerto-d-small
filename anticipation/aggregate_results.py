import csv

import numpy as np

vals_to_aggregate = {}
with open("results.csv") as f:
    reader = csv.DictReader(f)
    for r in reader:
        key = (r["type_comms"], r["nb_deps_seq"], r["deps_pos"], r["chains_length"], r["nb_chains"], r["topology"])
        vals_to_aggregate.setdefault(key, {"static": [], "dynamic": [], "duration": []})["static"].append(float(r["static"]))
        vals_to_aggregate[key]["dynamic"].append(float(r["dynamic"]))
        vals_to_aggregate[key]["duration"].append(float(r["duration"]))

    with open("aggregated_results.csv", "w") as f:
        csvwriter = csv.writer(f, delimiter=",")
        csvwriter.writerow([
            "static_mean", "static_std", "dynamic_mean", "dynamic_std", "duration_mean", "duration_std",
            "type_comms", "nb_deps_seq", "deps_pos", "chains_length", "nb_chains", "topology"
        ])
        for key in vals_to_aggregate.keys():
            csvwriter.writerow([
                round(np.asarray(vals_to_aggregate[key]["static"]).mean(), 2), round(np.asarray(vals_to_aggregate[key]["static"]).std(), 2),
                round(np.asarray(vals_to_aggregate[key]["dynamic"]).mean(), 2), round(np.asarray(vals_to_aggregate[key]["dynamic"]).std(), 2),
                round(np.asarray(vals_to_aggregate[key]["duration"]).mean(), 2), round(np.asarray(vals_to_aggregate[key]["duration"]).std(), 2),
                *key
            ])
print("done")
