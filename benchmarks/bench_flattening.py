import os
import sys
import time
from typing import List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gradual.definitions import (  # noqa: E402
    Edge,
    Environment,
    Signature,
    Specification,
)
from src.gradual.evidence.flattening import Sigma  # noqa: E402
from src.gradual.types import Unknown  # noqa: E402
from src.static.types import ClassName  # noqa: E402

""" Stacked-diamond family and the timing helper shared by the benchmarks. """


def stacked_diamonds(k: int) -> Tuple[Environment, Sigma]:
    """A stack of k diamonds: A_i on top, B_i / C_i in the middle, A_{i+1} at
    the bottom (also the top of the next diamond).  3k + 1 nodes, 4k edges.
    Uniform specs; wrap with bench_shapes.alternate for the benchmark."""
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
