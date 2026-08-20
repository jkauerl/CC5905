import random

from benchmarks.bench_flattening import stacked_diamonds
from benchmarks.bench_shapes import alternate, dense_mi_dag, random_dag
from src.gradual.definitions import Edge, Environment, Signature, Specification
from src.gradual.evidence.flattening import flatten_dp
from src.gradual.non_degenerate import degenerate_nodes, non_degenerate
from src.gradual.pair_validation import pair_valid
from src.gradual.types import Unknown
from src.static.types import ClassName
from tests.gradual.test_flattening import crossing_diamond, incompatible_edge


def crossing_diamond_with_middle():
    """The crossing diamond with a type M strictly between the two layers
    (D, E <: M <: P, Q): the witness t^N(y) = M exists."""
    environment, sigma = crossing_diamond()
    m = ClassName("M")
    p, q, d, e = (ClassName(n) for n in ["P", "Q", "D", "E"])
    nodes = list(environment.Ns) + [m]
    edges = [
        edge for edge in environment.Es
        if not (edge.source in (d, e) and edge.target in (p, q))
    ] + [Edge(d, m), Edge(e, m), Edge(m, p), Edge(m, q)]
    sigma = dict(sigma)
    sigma["M"] = Specification(set())
    return Environment(nodes, edges, sigma), sigma


def test_stacked_diamonds_non_degenerate():
    for k in range(1, 5):
        environment, sigma = stacked_diamonds(k)
        assert non_degenerate(environment, sigma) is True


def test_incompatible_edge_degenerate():
    environment, sigma = incompatible_edge()
    assert non_degenerate(environment, sigma) is False
    assert degenerate_nodes(environment, sigma) == [("A", "x"), ("B", "x")]


def test_crossing_diamond_separates_pair_valid():
    environment, sigma = crossing_diamond()
    assert pair_valid(environment, sigma) is True
    assert non_degenerate(environment, sigma) is False
    assert degenerate_nodes(environment, sigma) == [("N", "y")]
    assert flatten_dp(environment, sigma) is False


def test_crossing_diamond_with_middle_accepted():
    environment, sigma = crossing_diamond_with_middle()
    assert non_degenerate(environment, sigma) is True
    assert flatten_dp(environment, sigma) is True


def test_missing_ancestor_field_degenerate():
    a, b = ClassName("A"), ClassName("B")
    p = ClassName("P")
    sigma = {
        "P": Specification(set()),
        "A": Specification({Signature("x", p), Signature("y", p)}),
        "B": Specification({Signature("x", p)}),
    }
    environment = Environment([p, a, b], [Edge(b, a)], sigma)
    assert non_degenerate(environment, sigma) is False
    assert degenerate_nodes(environment, sigma) == [("A", None), ("B", None)]


def test_flattening_agrees_on_alternating_families():
    for k in (1, 2, 4, 8):
        environment, sigma = alternate(stacked_diamonds(k)[0])
        assert non_degenerate(environment, sigma) is True
        assert flatten_dp(environment, sigma) is True
    for n in (8, 16, 32):
        environment, sigma = alternate(dense_mi_dag(n, seed=7)[0])
        assert non_degenerate(environment, sigma) == flatten_dp(environment, sigma)
        environment, sigma = alternate(random_dag(n, 2, seed=7)[0])
        assert non_degenerate(environment, sigma) == flatten_dp(environment, sigma)


def test_flattening_agrees_on_random_perturbations():
    """Random first-order specs over a small type lattice, valid or not:
    the flattening's verdict is exactly non-degeneracy."""
    rng = random.Random(3)
    p0, p1, p2 = (ClassName(n) for n in ["P0", "P1", "P2"])
    type_nodes = [p0, p1, p2]
    type_edges = [Edge(p1, p0), Edge(p2, p1)]
    pool = [p0, p1, p2, Unknown()]
    for trial in range(40):
        base, _ = random_dag(6, 2, seed=trial)
        nodes = list(base.Ns) + type_nodes
        edges = list(base.Es) + type_edges
        sigma = {t.name: Specification(set()) for t in type_nodes}
        for node in base.Ns:
            sigma[node.name] = Specification({Signature("x", rng.choice(pool))})
        environment = Environment(nodes, edges, sigma)
        assert non_degenerate(environment, sigma) == flatten_dp(environment, sigma)
