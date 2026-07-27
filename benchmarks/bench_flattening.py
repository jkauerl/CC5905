import csv
import os
import sys
import time
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gradual.definitions import Edge, Environment, Signature, Specification  # noqa: E402
from src.gradual.evidence.flattening import (  # noqa: E402
    Sigma,
    flatten_dp,
    flatten_naive,
)
from src.gradual.types import Unknown  # noqa: E402
from src.static.types import ClassName  # noqa: E402

""" Benchmark: naive vs table-driven (DP) evaluation of the flattening on
stacked-diamond hierarchies.

A stack of k diamonds has 3k + 1 nodes and 4k edges, and 2^k distinct
inheritance paths from the bottom node to the root: the naive evaluation
re-derives the evidence of shared ancestors once per path, the table-driven
one computes each node exactly once.
"""


def stacked_diamonds(k: int) -> Tuple[Environment, Sigma]:
    """Build a stack of k diamonds: A_i on top, B_i / C_i in the middle,
    A_{i+1} at the bottom (also the top of the next diamond).

    Every node declares the same two fields (one class-typed, one unknown),
    so every meet taken along the way is trivial and the measured difference
    between the two evaluations is purely the traversal strategy.

    :param k: The number of stacked diamonds.
    :return: The environment and the complete specification assignment.
    """
    nodes: List[ClassName] = []
    edges: List[Edge] = []

    def a(i: int) -> ClassName:
        return ClassName(f"A{i}")

    def b(i: int) -> ClassName:
        return ClassName(f"B{i}")

    def c(i: int) -> ClassName:
        return ClassName(f"C{i}")

    nodes.append(a(0))
    for i in range(k):
        nodes.extend([b(i), c(i), a(i + 1)])
        edges.append(Edge(b(i), a(i)))
        edges.append(Edge(c(i), a(i)))
        edges.append(Edge(a(i + 1), b(i)))
        edges.append(Edge(a(i + 1), c(i)))

    spec = Specification(
        {Signature("x", ClassName("A0")), Signature("y", Unknown())}
    )
    sigma: Sigma = {node.name: spec for node in nodes}
    environment = Environment(nodes, edges, sigma)
    return environment, sigma


def measure(fn, repeats: int = 5) -> Tuple[float, float]:
    """Mean and standard deviation of the wall-clock time of a nullary
    callable over `repeats` timed runs, after one untimed warm-up run."""
    fn()
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        times.append(time.perf_counter() - start)
    mean = sum(times) / len(times)
    variance = sum((t - mean) ** 2 for t in times) / (len(times) - 1)
    return mean, variance**0.5


def main() -> None:
    naive_cap_seconds = 3.0
    dp_ks = [1, 2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128]
    rows = []

    print(f"{'variant':<8} {'k':>4} {'nodes':>6} {'edges':>6} {'mean_s':>12} {'std_s':>12}")

    k = 1
    while True:
        environment, sigma = stacked_diamonds(k)
        mean, std = measure(lambda: flatten_naive(environment, sigma))
        rows.append(("naive", k, len(environment.Ns), len(environment.Es), mean, std))
        print(f"{'naive':<8} {k:>4} {len(environment.Ns):>6} {len(environment.Es):>6} {mean:>12.6f} {std:>12.6f}")
        if mean > naive_cap_seconds or k >= 24:
            break
        k += 1

    for k in dp_ks:
        environment, sigma = stacked_diamonds(k)
        mean, std = measure(lambda: flatten_dp(environment, sigma))
        rows.append(("dp", k, len(environment.Ns), len(environment.Es), mean, std))
        print(f"{'dp':<8} {k:>4} {len(environment.Ns):>6} {len(environment.Es):>6} {mean:>12.6f} {std:>12.6f}")

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flattening_times.csv")
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["variant", "k", "nodes", "edges", "seconds", "std"])
        writer.writerows(rows)
    print(f"\nwritten: {out_path}")


if __name__ == "__main__":
    main()
