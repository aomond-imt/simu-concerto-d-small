import inspect

import numpy as np

from anticipation.run_simulation import compute_ons_tasks, compute_topology


class T:
    def test_compute_ons_tasks1(self):
        nb_nodes, nb_deps_seq, tt = 2, 2, 5
        expected = [
            [("run0_0", 5, ("run1_0",)), ("run0_1", 5, ("run1_1",))],
            [("run1_0", 5, ()), ("run1_1", 5, ())],
        ]
        ons_tasks = compute_ons_tasks(nb_nodes, nb_deps_seq, tt)
        assert ons_tasks == expected, f"expected {expected} got {ons_tasks}"

    def test_compute_ons_tasks2(self):
        nb_nodes, nb_deps_seq, tt = 3, 1, 5
        expected = [
            [("run0_0", 5, ("run1_0", "run2_0"))],
            [("run1_0", 5, ())],
            [("run2_0", 5, ())],
        ]
        ons_tasks = compute_ons_tasks(nb_nodes, nb_deps_seq, tt)
        assert ons_tasks == expected, f"expected {expected} got {ons_tasks}"

    def test_compute_topology_clique(self):
        name, nb_nodes, bw = "clique", 4, 50
        expected = np.full((nb_nodes, nb_nodes), bw)
        tply = compute_topology(name, nb_nodes, bw)
        assert all((all(x == y for x,y in zip(a, b)) for a,b in zip(tply, expected)))

    def test_compute_topology_star_4(self):
        name, nb_nodes, bw = "star", 4, 50
        expected = [
            [50, 50, 50, 50],
            [50, 50, 0, 0],
            [50, 0, 50, 0],
            [50, 0, 0, 50],
        ]
        tply = compute_topology(name, nb_nodes, bw)
        assert all((all(x == y for x,y in zip(a, b)) for a,b in zip(tply, expected)))

    def test_compute_topology_star_6(self):
        name, nb_nodes, bw = "star", 6, 500
        expected = [
            [500, 500, 500, 500, 500, 500],
            [500, 500, 0, 0, 0, 0],
            [500, 0, 500, 0, 0, 0],
            [500, 0, 0, 500, 0, 0],
            [500, 0, 0, 0, 500, 0],
            [500, 0, 0, 0, 0, 500],
        ]
        tply = compute_topology(name, nb_nodes, bw)
        assert all((all(x == y for x,y in zip(a, b)) for a,b in zip(tply, expected)))

    def test_compute_topology_chain_4(self):
        name, nb_nodes, bw = "chain", 4, 50
        expected = [
            [50, 50, 0, 0],
            [50, 50, 50, 0],
            [0, 50, 50, 50],
            [0, 0, 50, 50],
        ]
        tply = compute_topology(name, nb_nodes, bw)
        assert all((all(x == y for x,y in zip(a, b)) for a,b in zip(tply, expected)))

    def test_compute_topology_chain_6(self):
        name, nb_nodes, bw = "chain", 6, 50
        expected = [
            [50, 50, 0, 0, 0, 0],
            [50, 50, 50, 0, 0, 0],
            [0, 50, 50, 50, 0, 0],
            [0, 0, 50, 50, 50, 0],
            [0, 0, 0, 50, 50, 50],
            [0, 0, 0, 0, 50, 50],
        ]
        tply = compute_topology(name, nb_nodes, bw)
        assert all((all(x == y for x,y in zip(a, b)) for a,b in zip(tply, expected)))


if __name__ == '__main__':
    for k, v in inspect.getmembers(T(), predicate=inspect.ismethod):
        print(k)
        v()
