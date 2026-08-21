import os
import random
import sys
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gradual.definitions import (  # noqa: E402
    Edge,
    Environment,
    Signature,
    Specification,
)
from src.gradual.evidence.flattening import (  # noqa: E402
    Sigma,
    adjacency,
    topological_order,
)
from src.gradual.types import Unknown  # noqa: E402
from src.static.types import ClassName  # noqa: E402

""" Hierarchy families (chain, binary tree, sparse / dense multiple
inheritance) and the alternating-spec wrapper the benchmark applies to every
family.  The builders return uniform specs; `alternate` replaces them. """


def uniform_specs(nodes: List[ClassName]) -> Sigma:
    spec = Specification({Signature("x", ClassName("1")), Signature("y", Unknown())})
    return {node.name: spec for node in nodes}


def alternate(environment: Environment) -> Tuple[Environment, Sigma]:
    """Alternating specs: classes at even depth declare {x : P_(d//2)} over a
    fresh chain-shaped type lattice P0 > P1 > ..., classes at odd depth
    declare {x : ?}.  Valid by construction, and every ?-class sits between
    two differing concrete declarations, so consistent subtyping is genuinely
    non-transitive.  The lattice nodes are added to the environment."""
    parents, _ = adjacency(environment)
    order = topological_order(environment)
    depth: Dict[str, int] = {}
    for node in order:
        ps = parents[node.name]
        depth[node.name] = 0 if not ps else 1 + max(depth[p.name] for p in ps)
    max_level = max(depth.values()) // 2 + 1
    type_nodes = [ClassName(f"P{i}") for i in range(max_level + 1)]
    type_edges = [Edge(type_nodes[i + 1], type_nodes[i]) for i in range(max_level)]
    empty = Specification(set())
    sigma: Sigma = {t.name: empty for t in type_nodes}
    for node in environment.Ns:
        d = depth[node.name]
        if d % 2 == 1:
            sigma[node.name] = Specification({Signature("x", Unknown())})
        else:
            sigma[node.name] = Specification({Signature("x", type_nodes[d // 2])})
    nodes = list(environment.Ns) + type_nodes
    edges = list(environment.Es) + type_edges
    env2 = Environment(nodes, edges, sigma)
    return env2, sigma


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
    """Sparse multiple inheritance: 1..max_parents random earlier parents."""
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
    """Dense multiple inheritance: every node past the second has 2 or 3
    random earlier parents."""
    rng = random.Random(seed)
    nodes = [ClassName(str(i)) for i in range(1, n + 1)]
    edges = [Edge(ClassName("2"), ClassName("1"))]
    for child in range(3, n + 1):
        k = min(rng.choice([2, 2, 3]), child - 1)
        for p in rng.sample(range(1, child), k):
            edges.append(Edge(ClassName(str(child)), ClassName(str(p))))
    sigma = uniform_specs(nodes)
    return Environment(nodes, edges, sigma), sigma


def complete_binary_tree(n: int) -> Tuple[Environment, Sigma]:
    """Complete binary tree on exactly n nodes (node i's parent is i // 2)."""
    nodes = [ClassName(str(i)) for i in range(1, n + 1)]
    edges = [Edge(ClassName(str(i)), ClassName(str(i // 2))) for i in range(2, n + 1)]
    sigma = uniform_specs(nodes)
    return Environment(nodes, edges, sigma), sigma
