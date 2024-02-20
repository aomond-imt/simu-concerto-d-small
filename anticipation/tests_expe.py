from concurrent.futures import ProcessPoolExecutor

from run_simulation import run_expe
import inspect


class Pull:
    def test_pull_nb_deps_seq_1(self):
        parameters = {
            "type_comms": "pull",
            "nb_deps_seq": 1,
            "chains_length": 2,
            "is_pipeline": True,
            "nb_chains": 1,
            "topology": "clique",
            "id_run": 0
        }
        metrics_per_node = run_expe(parameters)
        assert metrics_per_node["upt_count"]["total"] == 25, metrics_per_node["upt_count"]["total"]
        print("passed")

    def test_pull_nb_deps_seq_2(self):
        parameters = {
            "type_comms": "pull",
            "nb_deps_seq": 2,
            "chains_length": 2,
            "is_pipeline": True,
            "nb_chains": 1,
            "topology": "clique",
            "id_run": 0
        }
        metrics_per_node = run_expe(parameters)
        assert metrics_per_node["upt_count"]["total"] == 53, metrics_per_node["upt_count"]["total"]
        print("passed")

    def test_pull_nb_deps_seq_3(self):
        # exit()
        parameters = {
            "type_comms": "pull",
            "nb_deps_seq": 3,
            "chains_length": 2,
            "is_pipeline": True,
            "nb_chains": 1,
            "topology": "clique",
            "id_run": 0
        }
        metrics_per_node = run_expe(parameters)
        assert metrics_per_node["upt_count"]["total"] == 105, metrics_per_node["upt_count"]["total"]
        print("passed")

    def test_pull_chains_length_5(self):
        parameters = {
            "type_comms": "pull",
            "nb_deps_seq": 1,
            "chains_length": 5,
            "is_pipeline": True,
            "nb_chains": 1,
            "topology": "clique",
            "id_run": 0
        }
        metrics_per_node = run_expe(parameters)
        assert metrics_per_node["upt_count"]["total"] == 25, metrics_per_node["upt_count"]["total"]
        print("passed")


class Push:
    def test_push_nb_deps_seq_1(self):
        parameters = {
            "type_comms": "push",
            "nb_deps_seq": 1,
            "chains_length": 2,
            "is_pipeline": True,
            "nb_chains": 1,
            "topology": "clique",
            "id_run": 0
        }
        metrics_per_node = run_expe(parameters)
        assert metrics_per_node["upt_count"]["total"] == 25, metrics_per_node["upt_count"]["total"]
        print("passed")

    def test_push_nb_deps_seq_5(self):
        parameters = {
            "type_comms": "push",
            "nb_deps_seq": 5,
            "chains_length": 2,
            "is_pipeline": True,
            "nb_chains": 1,
            "topology": "clique",
            "id_run": 0
        }
        metrics_per_node = run_expe(parameters)
        assert metrics_per_node["upt_count"]["total"] == 25, metrics_per_node["upt_count"]["total"]
        print("passed")

    def test_push_chains_length_5(self):
        parameters = {
            "type_comms": "push",
            "nb_deps_seq": 1,
            "chains_length": 5,
            "is_pipeline": True,
            "nb_chains": 1,
            "topology": "clique",
            "id_run": 0
        }
        metrics_per_node = run_expe(parameters)
        assert metrics_per_node["upt_count"]["total"] == 25, metrics_per_node["upt_count"]["total"]
        print("passed")


class PullAnticipation:
    def test_pull_anticipation_nb_deps_seq_1(self):
        parameters = {
            "type_comms": "pull_anticipation",
            "nb_deps_seq": 1,
            "chains_length": 2,
            "is_pipeline": True,
            "nb_chains": 1,
            "topology": "clique",
            "id_run": 0
        }
        metrics_per_node = run_expe(parameters)
        assert metrics_per_node["upt_count"]["total"] == 25, metrics_per_node["upt_count"]["total"]
        print("passed")

    def test_pull_anticipation_nb_deps_seq_5(self):
        parameters = {
            "type_comms": "pull_anticipation",
            "nb_deps_seq": 5,
            "chains_length": 2,
            "is_pipeline": True,
            "nb_chains": 1,
            "topology": "clique",
            "id_run": 0
        }
        metrics_per_node = run_expe(parameters)
        assert metrics_per_node["upt_count"]["total"] == 25, metrics_per_node["upt_count"]["total"]
        print("passed")

    def test_pull_anticipation_chains_length_5(self):
        parameters = {
            "type_comms": "pull_anticipation",
            "nb_deps_seq": 3,
            "chains_length": 5,
            "is_pipeline": True,
            "nb_chains": 1,
            "topology": "clique",
            "id_run": 0
        }
        metrics_per_node = run_expe(parameters)
        assert metrics_per_node["upt_count"]["total"] == 25, metrics_per_node["upt_count"]["total"]
        print("passed")


if __name__ == "__main__":
    results = []
    with ProcessPoolExecutor(max_workers=3) as executor:
        for k, v in inspect.getmembers(Pull(), predicate=inspect.ismethod):
            print(k)
            results.append(executor.submit(v))
        for k, v in inspect.getmembers(Push(), predicate=inspect.ismethod):
            print(k)
            results.append(executor.submit(v))
        for k, v in inspect.getmembers(PullAnticipation(), predicate=inspect.ismethod):
            print(k)
            results.append(executor.submit(v))

    for r in results:
        print(r.result())
