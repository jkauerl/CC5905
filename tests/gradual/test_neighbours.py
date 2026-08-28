from benchmarks.bench_flattening import stacked_diamonds
from benchmarks.bench_shapes import random_dag
from src.gradual.neighbours import ancestors, children, descendants, parents
from src.gradual.pair_validation import ancestor_pairs, strict_ancestor_pairs
from src.static.subtyping import is_direct_subtype, is_subtype
from tests.gradual.test_flattening import crossing_diamond


def _graphs():
    yield crossing_diamond()[0]
    yield stacked_diamonds(3)[0]
    yield random_dag(40, 3, seed=11)[0]


def test_neighbours_match_their_definitions():
    for environment in _graphs():
        for n in environment.Ns:
            assert parents(environment, n.name) == {
                p.name for p in environment.Ns if is_direct_subtype(environment, n, p)
            }
            assert children(environment, n.name) == {
                c.name for c in environment.Ns if is_direct_subtype(environment, c, n)
            }
            assert ancestors(environment, n.name) == {
                a.name for a in environment.Ns if is_subtype(environment, n, a)
            }
            assert descendants(environment, n.name) == {
                c.name for c in environment.Ns if is_subtype(environment, c, n)
            }


def test_ancestors_and_descendants_are_reflexive_and_dual():
    for environment in _graphs():
        for n in environment.Ns:
            assert n.name in ancestors(environment, n.name)
            assert n.name in descendants(environment, n.name)
            for a in ancestors(environment, n.name):
                assert n.name in descendants(environment, a)


def test_ancestor_pairs_count():
    for environment in _graphs():
        pairs = ancestor_pairs(environment)
        strict = strict_ancestor_pairs(environment)
        assert len(pairs) == len(strict) + len(environment.Ns)
        assert all(n != a for n, a in strict)
