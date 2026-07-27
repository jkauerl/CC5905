from src.gradual.definitions import Edge, Environment, Signature, Specification
from src.gradual.evidence.flattening import flatten_dp, flatten_naive
from src.gradual.types import Unknown
from src.static.types import ClassName

from benchmarks.bench_flattening import stacked_diamonds


def crossing_diamond():
    """The crossing-diamond example: C1{y:D}, C2{y:E} -> N{y:?} -> A1{y:P}, A2{y:Q},
    over the field-type universe D, E <: P, Q (non-unique meets: P meet Q = {D, E})."""
    p, q, d, e = (ClassName(n) for n in ["P", "Q", "D", "E"])
    a1, a2, n, c1, c2 = (ClassName(x) for x in ["A1", "A2", "N", "C1", "C2"])

    nodes = [p, q, d, e, a1, a2, n, c1, c2]
    edges = [
        Edge(d, p),
        Edge(d, q),
        Edge(e, p),
        Edge(e, q),
        Edge(n, a1),
        Edge(n, a2),
        Edge(c1, n),
        Edge(c2, n),
    ]
    empty = Specification(set())
    sigma = {
        "P": empty,
        "Q": empty,
        "D": empty,
        "E": empty,
        "A1": Specification({Signature("y", p)}),
        "A2": Specification({Signature("y", q)}),
        "N": Specification({Signature("y", Unknown())}),
        "C1": Specification({Signature("y", d)}),
        "C2": Specification({Signature("y", e)}),
    }
    return Environment(nodes, edges, sigma), sigma


def incompatible_edge():
    """Two unrelated field types on one edge: the edge evidence is empty."""
    p, q, a, b = (ClassName(n) for n in ["P", "Q", "A", "B"])
    nodes = [p, q, a, b]
    edges = [Edge(b, a)]
    empty = Specification(set())
    sigma = {
        "P": empty,
        "Q": empty,
        "A": Specification({Signature("x", p)}),
        "B": Specification({Signature("x", q)}),
    }
    return Environment(nodes, edges, sigma), sigma


def test_stacked_diamonds_accepted_and_agree():
    for k in range(1, 5):
        environment, sigma = stacked_diamonds(k)
        naive = flatten_naive(environment, sigma)
        dp = flatten_dp(environment, sigma)
        assert naive is True
        assert dp is True


def test_incompatible_edge_rejected_and_agree():
    environment, sigma = incompatible_edge()
    naive = flatten_naive(environment, sigma)
    dp = flatten_dp(environment, sigma)
    assert naive is False
    assert dp is False


def test_crossing_diamond_agree():
    environment, sigma = crossing_diamond()
    naive = flatten_naive(environment, sigma)
    dp = flatten_dp(environment, sigma)
    assert naive == dp
