from run_simulation import run_expe
import inspect


class T():
    def test_pull(self):
        parameters = {
            "type_comms": "pull",
            "nb_deps_seq": 2,
            "deps_pos": "place",
            "chains_length": 2,
            "nb_chains": 1,
            "topology": "clique",
            "id_run": 0
        }
        metrics_per_node = run_expe(parameters)
        assert metrics_per_node["upt_count"]["total"] == 25, metrics_per_node["upt_count"]["total"]
        print("passed")


if __name__ == "__main__":
    for k, v in inspect.getmembers(T(), predicate=inspect.ismethod):
        print(k)
        v()
