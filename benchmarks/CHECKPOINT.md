# Checkpoint — 2026-08-21 — validator benchmark (per-pair vs the ⋎-fold flattening vs the naive ND check)

State of the benchmark side of the thesis (the mechanization's checkpoint is
`thesis/rocq/CHECKPOINT.md`).  Supersedes the 2026-08-16 file, which described
the ANCHORED flattening.  On 2026-08-20 the Python was synced to the shipped
validator: the bottom pass folds children with the evidence JOIN ⋎ (R16), the
anchor is DELETED, and the specification the flattening decides is
**NonDegenerate** (R18), not PairValid.

## WHAT IS COMPARED

- **PairValid** (`src/gradual/pair_validation.py`, `pair_valid`) — consistent
  subtyping at every reachable pair.  With `?` the relation is not transitive,
  so a per-edge check is unsound.  PairValid is now the BASELINE, not an
  equivalent decider: it is strictly weaker than NonDegenerate (the crossing
  diamond is PairValid yet rejected — `tests/gradual/test_non_degenerate.py`).
- **the flattening** (`src/gradual/evidence/flattening.py`, `flatten_dp`) —
  two passes over a topological order: the top pass MEETS across parents
  (`_meet_fold`), the bottom pass JOINS across children (`_join_fold` /
  `join_evidence_sets`, mirroring `E_spec_join`/`E_evidence_join`), combine
  per node.  No anchor anywhere (`anchor_floor`/`anchor_views`/
  `flatten_anchored` deleted).  The mechanized theorem
  (`flatten_graph_NonDegenerate_equiv`, axiom-free): acceptance ⟺
  NonDegenerate.
- **the naive ND check** (`src/gradual/non_degenerate.py`, `non_degenerate` /
  `degenerate_nodes`) — a direct first-order decision procedure of the Rocq
  definition: per node a witness from γ(Σ(N)(x)) above every concrete
  descendant declaration and below every concrete ancestor one.  It is the
  correctness ORACLE, not a contender: for a `?` field it enumerates every
  name of the environment, cost ≈ |N̄|² + 2·pairs (model verified: ≈ 1–1.3 µs
  per elementary subtyping test across all families).  Function-typed fields
  raise.

Every benchmarked family carries ALTERNATING specs (`bench_shapes.alternate`),
so consistent subtyping is genuinely non-transitive and every instance is
valid (hence ND) by construction; `bench_pairvalid_tex.py` asserts all three
verdicts agree on every instance.

## THE RESULT (Python 3.12, Ryzen 7 5700X3D desktop — ≈ 2.3× the laptop run; mean of 5 after warm-up)

- The flattening overtakes per-pair when reachable pairs / edges exceeds the
  unit-cost ratio, now ≈ 48–50 (was ≈ 55–60 with the meet fold: ⋎ over the
  chain lattice yields fewer candidates than ⋏).  Pairs/edge is a property of
  the SHAPE (≈ depth); the ratio is a property of the implementation.
- Stacked diamonds, 515 nodes / 82 177 pairs: per-pair 0.105 s, flattening
  0.042 s, ND 0.250 s; crossing between 195 and 259 nodes.
- Chain, 1 501 nodes: 0.800 / 0.098 / 1.72 s (flattening 8×); crossing
  between 97 and 183 nodes.
- Dense multiple inheritance, 9 021 nodes / 1.77 M pairs: 2.93 / 2.68 /
  35.2 s; parity between 6 020 and 8 021 nodes.
- Sparse MI (1 500 nodes) and binary tree (1 497 nodes): per-pair wins
  throughout (ratios 0.25 and 0.18; pairs/edge ≈ 14 and ≈ 9, below the
  threshold — the tree structurally never crosses).
- The naive ND check is the slowest everywhere and diverges with size (35 s
  at dense 9 021) — the |N̄|² term.  The flattening escapes both terms: the
  witness "∃ t" is the interval it carries (combine ≠ ∅), and the two passes
  do one composition per EDGE instead of traversing the reachability closure.
- Edges ≤ reachable pairs always, so when both must PRODUCE the evidence
  table the flattening never does more work — the language-level advantage;
  the timings compare it against the bare decision.
- All instances collapse onto one curve of time-ratio vs pairs-per-edge
  (`validators_crossover_model.csv`).

## FILES

```
src/gradual/pair_validation.py       pair_valid, strict_ancestor_pairs
src/gradual/evidence/flattening.py   flatten_dp (⋎ bottom fold, ⋏ top fold, no anchor)
src/gradual/evidence/functions.py    join_evidence_intervals/_specifications, join_evidences
src/gradual/non_degenerate.py        non_degenerate, degenerate_nodes (the oracle)
src/static/subtyping.py              ancestor closure cached per Environment
src/static/functions.py              lower/upper sets, meet/join memoized
benchmarks/bench_shapes.py           chain, binary_tree, complete_binary_tree,
                                     random_dag, dense_mi_dag, alternate
benchmarks/bench_pairvalid_tex.py    THE benchmark: times all three validators,
                                     prints pgfplots coordinates, writes the CSVs
                                     (column nd_seconds added)
benchmarks/audit_flattening.py       agreement, meet AND join counts vs prediction
benchmarks/diff_rocq.py              differential check against the Rocq validators
benchmarks/validators_*.csv          the LIVE run: desktop ⋎-fold, 2026-08-20 —
                                     the run behind the current tex figures
benchmarks/validators_*_anchored.csv FROZEN (renamed from *_thesis): the 2026-08-16
                                     anchored laptop run behind the old figures and
                                     the poster.  Do not overwrite.
```

Reproduce: `python benchmarks/bench_pairvalid_tex.py` (dense goes to 9 000
nodes), `python benchmarks/audit_flattening.py`, `python -m pytest -q`
(154 tests).  Set `PYTHONIOENCODING=utf-8` on Windows.  pytest is NOT in the
project deps (pip-installed into the system Python 3.12).  ruff has
`fix = true` in pyproject — `ruff check` REWRITES files; never lint a tree
you don't mean to keep.

## KNOWN GAPS

- `benchmarks/diff_rocq.py` is STALE: its docstring still claims flattening =
  per-pair "by the flattening correctness theorem" (false in general — the
  theorem is now against NonDegenerate), and it targets `flatten_table_check`
  / `flatten_graph_table`, which were pruned from the Rocq on 2026-08-20.
  Needs a rework before its next use.
- `src/gradual/validations.py`: `is_valid_graph` is the per-edge check (not
  PairValid), and `get_all_parent_specifications` returns the declared parent
  spec where the flattened one is expected.  Untouched; the benchmark does
  not use that module.
- Function-typed fields are structurally different from the mechanization's;
  `diff_rocq.py` is scoped to first-order specs; `non_degenerate` raises on
  them (the Rocq theorem covers them).
- A smarter direct ND decider (candidates = joins of the concrete floors)
  would drop the |N̄|² term and land at ≈ 2·pairs — the honest "direct ND"
  baseline if ever plotted.  Not implemented.
- A compiled implementation (extraction from Rocq to OCaml, hash-consed
  intervals) would lower the unit-cost ratio and move every crossing left;
  not pursued (fix `reaches`' strict `&&` first).
