from benchmarks.bench_flattening import stacked_diamonds
from src.gradual.definitions import Edge, Environment, Signature, Specification
from src.gradual.evidence.definitions import (
    Evidence,
    EvidenceInterval,
    EvidenceSignature,
    EvidenceSpecification,
)
from src.gradual.evidence.flattening import (
    e_bot_table,
    e_top_table,
    edge_table,
    evidence_below,
    flatten_dp,
    flatten_unfiltered,
    max_filter,
    min_filter,
    topological_order,
)
from src.gradual.pair_validation import pair_valid
from src.gradual.types import Unknown
from src.static.types import ClassName


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
        assert flatten_dp(environment, sigma) is True
        assert pair_valid(environment, sigma) is True


def test_incompatible_edge_rejected_and_agree():
    environment, sigma = incompatible_edge()
    assert flatten_dp(environment, sigma) is False
    assert pair_valid(environment, sigma) is False


def test_crossing_diamond_pair_valid_but_rejected():
    environment, sigma = crossing_diamond()
    assert pair_valid(environment, sigma) is True
    assert flatten_dp(environment, sigma) is False


def test_unfiltered_flattening_agrees_with_flattening():
    for k in range(1, 5):
        environment, sigma = stacked_diamonds(k)
        assert flatten_unfiltered(environment, sigma) is True
    environment, sigma = incompatible_edge()
    assert flatten_unfiltered(environment, sigma) is False
    environment, sigma = crossing_diamond()
    assert flatten_unfiltered(environment, sigma) is False


def test_filtered_tables_are_inside_the_unfiltered_ones():
    for instance in (stacked_diamonds(3), crossing_diamond()):
        environment, sigma = instance
        order = topological_order(environment)
        edges = edge_table(environment, sigma)
        top = e_top_table(environment, sigma, order, edges, filtered=False)
        top_max = e_top_table(environment, sigma, order, edges)
        bot = e_bot_table(environment, sigma, order, edges, filtered=False)
        bot_min = e_bot_table(environment, sigma, order, edges)
        for node in environment.Ns:
            assert top_max[node.name] <= top[node.name]
            assert bot_min[node.name] <= bot[node.name]
            assert bool(top_max[node.name]) == bool(top[node.name])
            assert bool(bot_min[node.name]) == bool(bot[node.name])


def test_filters_drop_exactly_the_strictly_dominated():
    p, d = ClassName("P"), ClassName("D")
    nodes = [p, d]
    edges = [Edge(d, p)]
    empty = Specification(set())
    sigma = {"P": empty, "D": empty}
    environment = Environment(nodes, edges, sigma)

    def evidence(lower, upper):
        interval = EvidenceInterval(lower, upper)
        spec = EvidenceSpecification({EvidenceSignature("x", interval)})
        return Evidence(spec, spec)

    low = evidence(d, d)
    high = evidence(d, p)
    assert evidence_below(environment, low, high)
    assert not evidence_below(environment, high, low)
    assert max_filter(environment, {low, high}) == {high}
    assert min_filter(environment, {low, high}) == {low}
    assert max_filter(environment, {low}) == {low}
    assert min_filter(environment, {high}) == {high}
