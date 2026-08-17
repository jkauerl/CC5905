# Checkpoint — 2026-08-16 — validator benchmark (per-pair vs the flattening)

State of the benchmark side of the thesis (the mechanization's checkpoint is
`thesis/rocq/CHECKPOINT.md`).  This rewrite supersedes the 2026-08-11 file,
whose headline ("the flattening loses by 100x–3000x") was an artefact of the
implementation, not a finding: the type-level primitives (subtyping, lower/
upper sets, meets/joins) were being recomputed inside every evidence
operation.  With them memoized (2026-08-14) the picture is the one below.

## WHAT IS COMPARED

- **PairValid** (`src/gradual/pair_validation.py`, `pair_valid`) — the
  specification: consistent subtyping at every reachable pair.  With `?` the
  relation is not transitive, so a per-edge check is unsound (C{x:P} <: M{x:?}
  <: A{x:Q}: every edge passes, the pair (C,A) fails).
- **the flattening** (`src/gradual/evidence/flattening.py`) — `flatten_dp`
  (two passes over a topological order, meet across siblings, combine per
  node) and **`flatten_anchored`** (same passes; the stored entry also
  combines against the value-anchored variants; acceptance gated on the
  un-anchored combination).  The anchored one is the language's class-table
  ingredient and the one benchmarked.
- The two agree on every hierarchy (the mechanized equivalence theorem);
  `benchmarks/diff_rocq.py` checks Python `flatten_dp` = `pair_valid` = Rocq
  `flatten_check` = Rocq `flatten_table_check` on crafted + random instances.

Every benchmarked family carries ALTERNATING specs (`bench_shapes.alternate`:
concrete / ? / concrete down the hierarchy over a fresh chain-shaped type
lattice), so consistent subtyping is genuinely non-transitive on every
instance and every hierarchy is valid by construction.

## THE RESULT (Python 3.12, Ryzen 7 5700X3D; mean of 5 runs after warm-up)

- Per-pair costs ≈ 1.3–1.7 µs per reachable pair; the flattening ≈ 70–90 µs
  per edge (evidence construction: interiors, meets, set combines).
- The flattening overtakes when reachable pairs / edges exceeds that unit-cost
  ratio, ≈ 55–60.  Pairs/edge is a property of the SHAPE (depth); the ratio
  is a property of the implementation.
- Anchored crossings: stacked diamonds ≈ 259 nodes; chain ≈ 183; dense
  multiple inheritance parity at 6 020, flipped at 8 021; sparse MI not in the
  measured range (≈ 30 000 by extrapolation); binary tree never (pairs/edge =
  depth, logarithmic).  Un-anchored `flatten_dp`: diamonds ≈ 215, dense
  ≈ 4 500.
- Edges ≤ reachable pairs always (equality only for depth-one forests), so
  when both must PRODUCE the evidence table the flattening never does more
  work — that is the language-level advantage; the timings above compare it
  against the bare decision.
- All instances of all families collapse onto one curve of time-ratio vs
  pairs-per-edge (`validators_crossover_model.csv`).

## FILES

```
src/gradual/pair_validation.py       pair_valid, reachable_pairs
src/gradual/evidence/flattening.py   flatten_dp, flatten_anchored (in-place sets, shared edge_table)
src/static/subtyping.py              ancestor closure cached per Environment
src/static/functions.py              lower/upper sets, meet/join memoized
benchmarks/bench_flattening.py       stacked_diamonds, measure
benchmarks/bench_shapes.py           chain, binary_tree, random_dag, dense_mi_dag, alternate
benchmarks/bench_pairvalid_tex.py    THE benchmark: prints pgfplots coordinates, writes the CSVs
benchmarks/audit_flattening.py       agreement, operation counts vs prediction, unit costs
benchmarks/diff_rocq.py              differential check against the Rocq validators
benchmarks/validators_*_thesis.csv   FROZEN: the run behind the thesis figures and the
                                     poster (diamonds / families / crossover model,
                                     2026-08-16).  Do not overwrite.
benchmarks/validators_*.csv          the latest run (bench_pairvalid_tex.py overwrites
                                     these; same code, differs from _thesis by noise)
```

Reproduce: `python benchmarks/bench_pairvalid_tex.py` (a few minutes; the
dense family goes to 8 000 nodes), `python benchmarks/audit_flattening.py`,
`python benchmarks/diff_rocq.py` (needs the Rocq build), `python -m pytest -q`
(147 tests).  Set `PYTHONIOENCODING=utf-8` on Windows.

## KNOWN GAPS

- `src/gradual/validations.py`: `is_valid_graph` is the per-edge check (not
  PairValid), and `get_all_parent_specifications` returns the declared parent
  spec where the flattened one is expected.  Untouched; the benchmark does not
  use that module.
- Function-typed fields are structurally different from the mechanization's;
  `diff_rocq.py` is scoped to first-order specs.
- A compiled implementation (extraction from Rocq to OCaml, hash-consed
  intervals) would lower the unit-cost ratio and move every crossing left;
  not pursued.
