import csv
import os
import random
import sys
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.bench_flattening import measure, stacked_diamonds  # noqa: E402
from src.gradual.definitions import Edge, Environment, Signature, Specification  # noqa: E402
from src.gradual.evidence.flattening import Sigma, flatten_dp, flatten_naive  # noqa: E402
from src.gradual.types import Unknown  # noqa: E402
from src.static.types import ClassName  # noqa: E402

""" Benchmark across hierarchy shapes.

The driver of the naive/table-driven separation is the number of inheritance
paths, not the number of nodes: chains and trees (single inheritance) have
few paths and both evaluations are fast, random multiple-inheritance DAGs
sit in between, and stacked diamonds are the extreme.  Every family uses
the same uniform two-field specs ({x : name, y : ?}) so all meets are
trivial and the measured differences are purely traversal.

The naive evaluation is skipped (reported as blank) when the path count
exceeds NAIVE_PATH_CAP.
"""

NAIVE_PATH_CAP = 200_000


def uniform_specs(nodes: List[ClassName]) -> Sigma:
    spec = Specification({Signature("x", ClassName("1")), Signature("y", Unknown())})
    return {node.name: spec for node in nodes}


def chain(n: int) -> Tuple[Environment, Sigma]:
    nodes = [ClassName(str(i)) for i in range(1, n + 1)]
    edges = [Edge(ClassName(str(i + 1)), ClassName(str(i))) for i in range(1, n)]
    sigma = uniform_specs(nodes)
    return Environment(nodes, edges, sigma), sigma


def binary_tree(depth: int) -> Tuple[Environment, Sigma]:
    n = 2**depth - 1
    nodes = [ClassName(str(i)) for i in range(1, n + 1)]
    edges = [Edge(ClassName(str(i)), ClassName(str(i // 2))) for i in range(2, n + 1)]
    sigma = uniform_specs(nodes)
    return Environment(nodes, edges, sigma), sigma


def random_dag(n: int, max_parents: int, seed: int) -> Tuple[Environment, Sigma]:
    rng = random.Random(seed)
    nodes = [ClassName(str(i)) for i in range(1, n + 1)]
    edges = []
    for child in range(2, n + 1):
        k = rng.randint(1, min(max_parents, child - 1))
        for p in rng.sample(range(1, child), k):
            edges.append(Edge(ClassName(str(child)), ClassName(str(p))))
    sigma = uniform_specs(nodes)
    return Environment(nodes, edges, sigma), sigma


def dense_mi_dag(n: int, seed: int) -> Tuple[Environment, Sigma]:
    """Dense multiple inheritance: every node (past the second) has 2 or 3
    parents, the shape the validator exists for."""
    rng = random.Random(seed)
    nodes = [ClassName(str(i)) for i in range(1, n + 1)]
    edges = [Edge(ClassName("2"), ClassName("1"))]
    for child in range(3, n + 1):
        k = min(rng.choice([2, 2, 3]), child - 1)
        for p in rng.sample(range(1, child), k):
            edges.append(Edge(ClassName(str(child)), ClassName(str(p))))
    sigma = uniform_specs(nodes)
    return Environment(nodes, edges, sigma), sigma


def path_count(environment: Environment) -> int:
    """Total number of distinct non-empty directed paths in the DAG."""
    parents: Dict[str, List[str]] = {n.name: [] for n in environment.Ns}
    for e in environment.Es:
        parents[e.source.name].append(e.target.name)

    memo: Dict[str, int] = {}

    def f(name: str) -> int:
        if name not in memo:
            memo[name] = sum(1 + f(p) for p in parents[name])
        return memo[name]

    return sum(f(n.name) for n in environment.Ns)


def main() -> None:
    cases = [
        ("chain (control)", chain(121)),
        ("binary tree (control)", binary_tree(7)),
        ("sparse mi dag", random_dag(34, 2, seed=7)),
        ("sparse mi dag", random_dag(121, 2, seed=7)),
        ("dense mi dag", dense_mi_dag(34, seed=7)),
        ("dense mi dag", dense_mi_dag(121, seed=7)),
        ("diamond stack", stacked_diamonds(11)),
        ("diamond stack", stacked_diamonds(40)),
    ]

    rows = []
    print(f"{'family':<14} {'nodes':>6} {'edges':>6} {'paths':>12} {'naive_s':>10} {'dp_s':>10}")
    for family, (environment, sigma) in cases:
        n, e = len(environment.Ns), len(environment.Es)
        paths = path_count(environment)
        assert flatten_dp(environment, sigma) is True
        dp_mean, _ = measure(lambda: flatten_dp(environment, sigma))
        if paths <= NAIVE_PATH_CAP:
            assert flatten_naive(environment, sigma) is True
            naive_mean, _ = measure(lambda: flatten_naive(environment, sigma))
            naive_str = f"{naive_mean:.6f}"
        else:
            naive_mean = None
            naive_str = "-"
        rows.append((family, n, e, paths, naive_str, f"{dp_mean:.6f}"))
        print(f"{family:<14} {n:>6} {e:>6} {paths:>12} {naive_str:>10} {dp_mean:>10.6f}")

    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "flattening_shapes.csv"
    )
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["family", "nodes", "edges", "paths", "naive_s", "dp_s"])
        writer.writerows(rows)
    print(f"\nwritten: {out_path}")


def sweep() -> None:
    """Size sweep per family, for the per-family panels."""
    families = [
        ("dense mi", [dense_mi_dag(n, seed=7) for n in (8, 16, 32, 64, 121)]),
        ("sparse mi", [random_dag(n, 2, seed=7) for n in (8, 16, 32, 64, 121)]),
        ("chain", [chain(n) for n in (8, 16, 32, 64, 121)]),
        ("binary tree", [binary_tree(d) for d in (3, 4, 5, 6, 7)]),
    ]
    rows = []
    print(f"{'family':<12} {'nodes':>6} {'paths':>8} {'naive_s':>10} {'dp_s':>10}")
    for family, instances in families:
        for environment, sigma in instances:
            n = len(environment.Ns)
            paths = path_count(environment)
            assert flatten_dp(environment, sigma) is True
            dp_mean, _ = measure(lambda: flatten_dp(environment, sigma))
            if paths <= NAIVE_PATH_CAP:
                naive_mean, _ = measure(lambda: flatten_naive(environment, sigma))
                naive_str = f"{naive_mean:.6f}"
            else:
                naive_str = "-"
            rows.append((family, n, paths, naive_str, f"{dp_mean:.6f}"))
            print(f"{family:<12} {n:>6} {paths:>8} {naive_str:>10} {dp_mean:>10.6f}")

    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "flattening_shapes_sweep.csv"
    )
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["family", "nodes", "paths", "naive_s", "dp_s"])
        writer.writerows(rows)
    print(f"\nwritten: {out_path}")


if __name__ == "__main__":
    if "--sweep" in sys.argv:
        sweep()
    else:
        main()
