import os
import sys
from typing import Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import src.gradual.evidence.flattening as flat  # noqa: E402
from benchmarks.bench_flattening import measure, stacked_diamonds  # noqa: E402
from benchmarks.bench_shapes import alternate  # noqa: E402
from src.gradual.non_degenerate import non_degenerate  # noqa: E402
from src.gradual.pair_validation import pair_valid, strict_ancestor_pairs  # noqa: E402

""" Audit of the benchmark, on alternating-spec stacked diamonds.

1. The three validators (per-pair, flattening, non-degeneracy) agree.
2. The flattening's operation counts match the structural prediction: one
   edge evidence per edge, one composition per edge per pass, one meet per
   extra parent, one join per extra child, one combination per node.
3. Unit costs: seconds per evidence operation vs seconds per pair check; the
   ratio is the pairs-per-edge threshold at which the flattening overtakes.
"""


class Counters:
    def __init__(self):
        self.trans = 0
        self.meet = 0
        self.join = 0
        self.comb = 0

    def reset(self):
        self.trans = self.meet = self.join = self.comb = 0


COUNTERS = Counters()

_ORIGINALS = {
    "trans": ("trans_evidences", flat.trans_evidences),
    "meet": ("meet_evidence_sets", flat.meet_evidence_sets),
    "join": ("join_evidence_sets", flat.join_evidence_sets),
    "comb": ("combine_evidences", flat.combine_evidences),
}


def instrument():
    for key, (name, fn) in _ORIGINALS.items():
        def counted(*args, _key=key, _fn=fn, **kwargs):
            setattr(COUNTERS, _key, getattr(COUNTERS, _key) + 1)
            return _fn(*args, **kwargs)

        setattr(flat, name, counted)


def deinstrument():
    for _, (name, fn) in _ORIGINALS.items():
        setattr(flat, name, fn)


def predict(environment) -> Tuple[int, int, int, int, int]:
    """(edge, trans, meet, join, comb) call counts predicted from the graph."""
    parents, children = flat.adjacency(environment)
    edges = len(environment.Es)
    meets = sum(max(0, len(parents[n.name]) - 1) for n in environment.Ns)
    joins = sum(max(0, len(children[n.name]) - 1) for n in environment.Ns)
    return (edges, 2 * edges, meets, joins, len(environment.Ns))


def counted_run(environment, sigma) -> Tuple[int, int, int, int, int]:
    instrument()
    COUNTERS.reset()
    assert flat.flatten_dp(environment, sigma) is True
    edges = len(flat.edge_table(environment, sigma))
    got = (edges, COUNTERS.trans, COUNTERS.meet, COUNTERS.join, COUNTERS.comb)
    deinstrument()
    return got


def main() -> None:
    print("[1] verdict agreement: pair_valid == flatten_dp == non_degenerate")
    ok = True
    for k in (1, 2, 3, 4, 8, 16, 32):
        environment, sigma = alternate(stacked_diamonds(k)[0])
        v = pair_valid(environment, sigma)
        if not (v == flat.flatten_dp(environment, sigma)
                == non_degenerate(environment, sigma)):
            print(f"  MISMATCH at k={k}")
            ok = False
    print(f"  {'OK' if ok else 'FAIL'}")

    print("\n[2] operation counts: instrumented vs predicted (edge, trans, meet, join, comb)")
    ok = True
    for k in (2, 4, 8, 16, 32, 64):
        environment, sigma = alternate(stacked_diamonds(k)[0])
        got, want = counted_run(environment, sigma), predict(environment)
        ok = ok and got == want
        print(f"  k={k:>3}  measured {got}  predicted {want}  "
              f"{'OK' if got == want else 'FAIL'}")
    print(f"  {'OK' if ok else 'FAIL'}")

    print("\n[3] unit costs")
    print(f"  {'k':>4} {'nodes':>6} {'ops':>6} {'pairs':>7} "
          f"{'us/op':>8} {'us/pair':>8} {'op/pair':>8}")
    for k in (8, 32, 128):
        environment, sigma = alternate(stacked_diamonds(k)[0])
        ops = sum(counted_run(environment, sigma))
        pairs = len(strict_ancestor_pairs(environment))
        flat_mean, _ = measure(lambda: flat.flatten_dp(environment, sigma))
        pair_mean, _ = measure(lambda: pair_valid(environment, sigma))
        us_op = flat_mean / ops * 1e6
        us_pair = pair_mean / pairs * 1e6
        print(f"  {k:>4} {len(environment.Ns):>6} {ops:>6} {pairs:>7} "
              f"{us_op:>8.2f} {us_pair:>8.2f} {us_op / us_pair:>7.1f}x")


if __name__ == "__main__":
    main()
