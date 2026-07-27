import os
import sys
import time
from typing import Dict, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import src.gradual.evidence.flattening as flat  # noqa: E402
from benchmarks.bench_flattening import measure, stacked_diamonds  # noqa: E402

""" Audit of the flattening benchmark.

1. Deep agreement: on the benchmark family, the naive and the table-driven
   evaluations produce the SAME per-node complete evidences (set equality),
   not merely the same boolean verdict.
2. Operation counts: instrument the evidence operations and compare the
   counts against an independent structural prediction --- a cheap recursion
   over the bare graph that mirrors the traversal without doing evidence
   work.  Naive counts must satisfy the path recurrence (doubling), DP
   counts must be exactly linear in the graph.
3. Fresh timings: re-measure a few sizes and report the drift against the
   recorded CSV.
"""


class Counters:
    def __init__(self):
        self.edge = 0
        self.trans = 0
        self.meet = 0

    def reset(self):
        self.edge = 0
        self.trans = 0
        self.meet = 0


COUNTERS = Counters()

_orig_edge = flat.edge_evidence
_orig_trans = flat.transitivity_complete_evidences
_orig_meet = flat.meet_complete_evidences


def _counted_edge(*args, **kwargs):
    COUNTERS.edge += 1
    return _orig_edge(*args, **kwargs)


def _counted_trans(*args, **kwargs):
    COUNTERS.trans += 1
    return _orig_trans(*args, **kwargs)


def _counted_meet(*args, **kwargs):
    COUNTERS.meet += 1
    return _orig_meet(*args, **kwargs)


def instrument():
    flat.edge_evidence = _counted_edge
    flat.transitivity_complete_evidences = _counted_trans
    flat.meet_complete_evidences = _counted_meet


def deinstrument():
    flat.edge_evidence = _orig_edge
    flat.transitivity_complete_evidences = _orig_trans
    flat.meet_complete_evidences = _orig_meet


def predict_naive(environment) -> Tuple[int, int, int]:
    """Structural prediction of (edge, trans, meet) call counts of
    flatten_naive, by mirroring the recursion over the bare graph."""
    parents, children = flat.adjacency(environment)

    def count_top(name: str) -> Tuple[int, int, int]:
        ps = parents[name]
        if not ps:
            return (0, 0, 0)
        e = t = 0
        m = len(ps) - 1
        for p in ps:
            pe, pt, pm = count_top(p.name)
            e += 1 + pe
            t += 1 + pt
            m += pm
        return (e, t, m)

    def count_bot(name: str) -> Tuple[int, int, int]:
        cs = children[name]
        if not cs:
            return (0, 0, 0)
        e = t = 0
        m = len(cs) - 1
        for c in cs:
            ce, ct, cm = count_bot(c.name)
            e += 1 + ce
            t += 1 + ct
            m += cm
        return (e, t, m)

    total = [0, 0, 0]
    for node in environment.Ns:
        for part in (count_top(node.name), count_bot(node.name)):
            total[0] += part[0]
            total[1] += part[1]
            total[2] += part[2]
    return tuple(total)


def predict_dp(environment) -> Tuple[int, int, int]:
    """Structural prediction of (edge, trans, meet) call counts of
    flatten_dp: one composition per edge per pass, one meet-fold per node."""
    parents, children = flat.adjacency(environment)
    edges = len(environment.Es)
    e = 2 * edges
    t = 2 * edges
    m = sum(max(0, len(parents[n.name]) - 1) for n in environment.Ns) + sum(
        max(0, len(children[n.name]) - 1) for n in environment.Ns
    )
    return (e, t, m)


def audit_deep_agreement(k: int) -> bool:
    environment, sigma = stacked_diamonds(k)
    order = flat.topological_order(environment)
    top_table = flat.e_top_table(environment, sigma, order)
    bot_table = flat.e_bot_table(environment, sigma, order)
    ok = True
    for node in environment.Ns:
        if flat.e_top_naive(environment, sigma, node) != top_table[node.name]:
            print(f"  MISMATCH e_top at {node.name} (k={k})")
            ok = False
        if flat.e_bot_naive(environment, sigma, node) != bot_table[node.name]:
            print(f"  MISMATCH e_bot at {node.name} (k={k})")
            ok = False
    return ok


def audit_counts(k: int) -> bool:
    environment, sigma = stacked_diamonds(k)
    ok = True

    instrument()
    COUNTERS.reset()
    assert flat.flatten_naive(environment, sigma) is True
    got_naive = (COUNTERS.edge, COUNTERS.trans, COUNTERS.meet)
    COUNTERS.reset()
    assert flat.flatten_dp(environment, sigma) is True
    got_dp = (COUNTERS.edge, COUNTERS.trans, COUNTERS.meet)
    deinstrument()

    want_naive = predict_naive(environment)
    want_dp = predict_dp(environment)

    print(
        f"  k={k:>2}  naive (edge,trans,meet): measured {got_naive} "
        f"predicted {want_naive}  {'OK' if got_naive == want_naive else 'FAIL'}"
    )
    print(
        f"        dp    (edge,trans,meet): measured {got_dp} "
        f"predicted {want_dp}  {'OK' if got_dp == want_dp else 'FAIL'}"
    )
    return got_naive == want_naive and got_dp == want_dp


def audit_timing_drift(csv_path: str) -> None:
    import csv as csv_mod

    recorded: Dict[Tuple[str, int], float] = {}
    with open(csv_path) as f:
        for row in csv_mod.DictReader(f):
            recorded[(row["variant"], int(row["k"]))] = float(row["seconds"])

    checks = [("naive", 6), ("naive", 9), ("naive", 11), ("dp", 16), ("dp", 64), ("dp", 128)]
    print(f"  {'variant':<8} {'k':>4} {'recorded':>12} {'fresh':>12} {'drift':>8}")
    for variant, k in checks:
        if (variant, k) not in recorded:
            continue
        environment, sigma = stacked_diamonds(k)
        fn = flat.flatten_naive if variant == "naive" else flat.flatten_dp
        fresh, _ = measure(lambda: fn(environment, sigma))
        old = recorded[(variant, k)]
        drift = (fresh - old) / old * 100.0
        print(f"  {variant:<8} {k:>4} {old:>12.6f} {fresh:>12.6f} {drift:>+7.1f}%")


def main() -> None:
    print("[1] deep per-node agreement naive == dp (set equality of evidences)")
    ok_deep = all(audit_deep_agreement(k) for k in (2, 3, 4))
    print(f"  {'OK' if ok_deep else 'FAIL'} for k in (2, 3, 4)")

    print("[2] operation counts: instrumented vs structurally predicted")
    ok_counts = all(audit_counts(k) for k in (2, 4, 6, 8, 10))
    print(f"  counts {'OK' if ok_counts else 'FAIL'}")

    print("[3] doubling / linearity of the trans counts")
    prev = None
    for k in range(2, 11):
        environment, _ = stacked_diamonds(k)
        _, t_naive, _ = predict_naive(environment)
        _, t_dp, _ = predict_dp(environment)
        ratio = (t_naive / prev) if prev else float("nan")
        print(f"  k={k:>2}  naive trans={t_naive:>8} (x{ratio:5.3f})  dp trans={t_dp:>5} (=8k: {t_dp == 8 * k})")
        prev = t_naive

    print("[4] timing drift vs recorded CSV")
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flattening_times.csv")
    audit_timing_drift(csv_path)

    start = time.perf_counter()
    print(f"\naudit wall time: {time.perf_counter() - start:.1f}s (timing section dominates)")


if __name__ == "__main__":
    main()
