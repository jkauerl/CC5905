# Checkpoint — 2026-08-29 — validator benchmark (per-pair vs the flattening vs the naive ND check)

State of the benchmark side of the thesis (the mechanization's checkpoint is
`thesis/rocq/CHECKPOINT.md`).  Supersedes the 2026-08-21 file.  On 2026-08-29
the Python was synced to the FIXED validator: the sibling meet keeps only the
maximal candidates and the sibling join only the minimal ones, so that ⋏ and
⋎ are operations on sets (Rocq `flatten_graph`,
`flatten_graph_NonDegenerate_equiv`, higher-order fields included).  The
former fold that kept every candidate is `flatten_unfiltered` (Rocq
`flatten_graph_unfiltered`), the proof engine of the completeness proof.
Branch `evidence-max-filter`.

## WHAT IS COMPARED

- **PairValid** (`src/gradual/pair_validation.py`, `pair_valid`) — consistent
  subtyping at every reachable pair.  With `?` the relation is not transitive,
  so a per-edge check is unsound.  PairValid is the BASELINE, not an
  equivalent decider: it is strictly weaker than NonDegenerate (the crossing
  diamond is PairValid yet rejected — `tests/gradual/test_non_degenerate.py`).
- **the flattening** (`src/gradual/evidence/flattening.py`, `flatten_dp`) —
  two passes over a topological order: the top pass MEETS across parents
  (`_meet_fold_max`: `meet_evidence_sets` then `max_filter` after every pair
  step, a single chain unfiltered), the bottom pass JOINS across children
  (`_join_fold_min`: `join_evidence_sets` then `min_filter`), combine per
  node.  The filter's order is `evidence_below` (Rocq `ev_below`): every
  field of the first spec has an entry in the second with both bounds below,
  on both slots.  `e_top_table`/`e_bot_table` take `filtered=` (default
  True); `flatten_unfiltered` is the same with `filtered=False`.  The
  mechanized theorem (`flatten_graph_NonDegenerate_equiv`, axiom-free):
  acceptance ⟺ NonDegenerate; the unfiltered engine decides the same
  (`flatten_graph_unfiltered_NonDegenerate_equiv`).
- **the naive ND check** (`src/gradual/non_degenerate.py`, `non_degenerate` /
  `degenerate_nodes`) — a direct first-order decision procedure of the Rocq
  definition: per node a witness from γ(Σ(N)(x)) above every concrete
  descendant declaration and below every concrete ancestor one.  It is the
  correctness ORACLE, not a contender: for a `?` field it enumerates every
  name of the environment, cost ≈ |N̄|² + 2·pairs.  Function-typed fields
  raise.

Every benchmarked family carries ALTERNATING specs (`bench_shapes.alternate`),
so consistent subtyping is genuinely non-transitive and every instance is
valid (hence ND) by construction; `bench_pairvalid_tex.py` asserts all four
verdicts (per-pair, flattening, unfiltered, ND) agree on every instance.

## THE RESULT (Python 3.12, Ryzen 7 5700X3D desktop; mean of 5 after warm-up; run of 2026-08-29)

- On every benchmark family the meets and joins are unique, so the filter
  never removes anything and the flattening tracks its unfiltered engine
  within noise (−5 % to +19 %, the cost of the `evidence_below` comparisons
  on singletons).  The filter pays off only where candidates are non-unique
  (`k > 1` families), which the benchmark does not contain.
- The flattening overtakes per-pair when reachable pairs / edges exceeds the
  unit-cost ratio, ≈ 50.  Pairs/edge is a property of the SHAPE (≈ depth);
  the ratio is a property of the implementation.
- Stacked diamonds, 515 nodes / 82 177 pairs: per-pair 0.101 s, flattening
  0.047 s (unfiltered 0.043), ND 0.259 s; crossing between 195 and 259 nodes.
- Chain, 1 501 nodes: 0.784 / 0.118 (0.117) / 1.77 s (flattening 6.7×);
  crossing between 97 and 183 nodes.
- Dense multiple inheritance, 9 021 nodes / 1.77 M pairs: 2.95 / 3.16
  (2.88) / 35.6 s; parity at the top of the sweep (ratio 0.91–0.94 at
  8 021–9 021).
- Sparse MI (1 500 nodes) and binary tree (1 497 nodes): per-pair wins
  throughout (ratios 0.23 and 0.17; pairs/edge ≈ 14 and ≈ 9, below the
  threshold — the tree structurally never crosses).
- The naive ND check is the slowest everywhere and diverges with size (35.6 s
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
src/gradual/evidence/flattening.py   flatten_dp (filtered ⋏ top fold, filtered ⋎ bottom fold),
                                     flatten_unfiltered, evidence_below, max_filter, min_filter
src/gradual/evidence/functions.py    join_evidence_intervals/_specifications, join_evidences
src/gradual/non_degenerate.py        non_degenerate, degenerate_nodes (the oracle)
src/static/subtyping.py              ancestor closure cached per Environment
src/static/functions.py              lower/upper sets, meet/join memoized
benchmarks/bench_shapes.py           chain, binary_tree, complete_binary_tree,
                                     random_dag, dense_mi_dag, alternate
benchmarks/bench_pairvalid_tex.py    THE benchmark: times the four validators,
                                     prints pgfplots coordinates, writes the CSVs
                                     (columns nd_seconds, flatten_unfiltered_seconds)
benchmarks/audit_flattening.py       agreement, meet AND join counts vs prediction
benchmarks/diff_rocq.py              differential check: flatten_dp / flatten_unfiltered
                                     against Rocq flatten_graph / flatten_check_unfiltered
                                     (45 instances; agreement 45/45 on 2026-08-29)
benchmarks/validators_*.csv          the LIVE run: desktop, 2026-08-29 — the run behind
                                     the current tex figures ("flattening" = flatten_dp)
benchmarks/validators_*_anchored.csv FROZEN (renamed from *_thesis): the 2026-08-16
                                     anchored laptop run behind the old figures and
                                     the poster.  Do not overwrite.
```

Reproduce: `python benchmarks/bench_pairvalid_tex.py` (dense goes to 9 000
nodes, ≈ 10 min), `python benchmarks/diff_rocq.py` (compiles a `DiffCheck.v`
in the Rocq tree and removes it), `python benchmarks/audit_flattening.py`,
`python -m pytest -q` (169 tests).  Set `PYTHONIOENCODING=utf-8` on Windows.
pytest is NOT in the project deps (pip-installed into the system Python 3.12).
ruff has `fix = true` in pyproject — `ruff check` REWRITES files; never lint a
tree you don't mean to keep (ruff is not installed in the system Python).

## KNOWN GAPS

- `src/gradual/validations.py`: `is_valid_graph` is the per-edge check (not
  PairValid), and `get_all_parent_specifications` returns the declared parent
  spec where the flattened one is expected.  Untouched; the benchmark does
  not use that module.
- Function-typed fields are structurally different from the mechanization's;
  `diff_rocq.py` is scoped to first-order specs; `non_degenerate` raises on
  them (the Rocq theorem covers them).
- `is_subtype_evidence_spec` (evidence subtyping, thesis (SSi)) polices width
  with the wider spec on the LEFT; `evidence_below` (the filter's order,
  Rocq `ev_below`) iterates the first spec.  They coincide on the sets the
  filter sees (uniform fields per slot) — Rocq `ev_below_iff_E_evidence_sub`.
- No benchmark family exercises non-unique meets (`k > 1`), so the filter's
  effect on running time is unmeasured.
- A smarter direct ND decider (candidates = joins of the concrete floors)
  would drop the |N̄|² term and land at ≈ 2·pairs — the honest "direct ND"
  baseline if ever plotted.  Not implemented.
- A compiled implementation (extraction from Rocq to OCaml, hash-consed
  intervals) would lower the unit-cost ratio and move every crossing left;
  not pursued (fix `reaches`' strict `&&` first).
