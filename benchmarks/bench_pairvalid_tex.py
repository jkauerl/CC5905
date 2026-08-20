import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.bench_flattening import measure, stacked_diamonds  # noqa: E402
from benchmarks.bench_shapes import (  # noqa: E402
    alternate,
    binary_tree,
    chain,
    dense_mi_dag,
    random_dag,
)
from src.gradual.evidence.flattening import flatten_dp  # noqa: E402
from src.gradual.non_degenerate import non_degenerate  # noqa: E402
from src.gradual.pair_validation import pair_valid, reachable_pairs  # noqa: E402

""" The benchmark: the flattening vs the per-pair validator and the direct
non-degeneracy check, alternating specs, on every family.  Prints the pgfplots coordinates for the three thesis
figures and records the measurements in three CSVs next to this file:

  validators_diamonds.csv          fig:flatten-benchmark
  validators_families.csv          fig:flatten-shapes-panels
  validators_crossover_model.csv   fig:flatten-crossover-model

Protocol: mean of five timed runs after one untimed warm-up (measure). """

HERE = os.path.dirname(os.path.abspath(__file__))


def _print_coords(header, coords):
    print(f"% {header}")
    line = "  " + " ".join(coords)
    while len(line) > 92:
        cut = line.rfind(" ", 0, 92)
        print(line[:cut])
        line = "  " + line[cut + 1 :]
    print(line)


def emit(label, instances, rows):
    pair_coords = []
    anch_coords = []
    nd_coords = []
    stats = []
    for environment, sigma in instances:
        nodes = len(environment.Ns)
        verdict = pair_valid(environment, sigma)
        assert verdict == flatten_dp(environment, sigma)
        assert verdict == non_degenerate(environment, sigma)
        pair_mean, _ = measure(lambda: pair_valid(environment, sigma))
        anch_mean, _ = measure(lambda: flatten_dp(environment, sigma))
        nd_mean, _ = measure(lambda: non_degenerate(environment, sigma))
        pair_coords.append(f"({nodes},{pair_mean:.6f})")
        anch_coords.append(f"({nodes},{anch_mean:.6f})")
        nd_coords.append(f"({nodes},{nd_mean:.6f})")
        stats.append((nodes, len(environment.Es),
                      len(reachable_pairs(environment)), pair_mean, anch_mean,
                      nd_mean))

    print(f"\n% {label}")
    _print_coords("flattening", anch_coords)
    _print_coords("per-pair validator", pair_coords)
    _print_coords("non-degeneracy check", nd_coords)
    print(f"%   {'nodes':>6} {'edges':>6} {'pairs':>8} {'pair_s':>10} "
          f"{'flat_s':>10} {'nd_s':>10}")
    for nodes, edges, pairs, pair_mean, anch_mean, nd_mean in stats:
        print(f"%   {nodes:>6} {edges:>6} {pairs:>8} "
              f"{pair_mean:>10.6f} {anch_mean:>10.6f} {nd_mean:>10.6f}")
        rows.append((label, nodes, edges, pairs,
                     f"{pair_mean:.6f}", f"{anch_mean:.6f}", f"{nd_mean:.6f}",
                     f"{pairs / edges:.2f}", f"{pair_mean / anch_mean:.4f}"))


def write_csv(name, rows):
    path = os.path.join(HERE, name)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["family", "nodes", "edges", "reachable_pairs",
                         "pair_seconds", "flatten_seconds", "nd_seconds",
                         "pairs_per_edge", "pair_over_flatten"])
        writer.writerows(rows)
    print(f"% written: {path}")


def main() -> None:
    print("=" * 72)
    print("FIGURE: validation running time on stacked diamonds")
    print("=" * 72)
    diamonds = []
    emit("stacked diamonds",
         [alternate(stacked_diamonds(k)[0])
          for k in (1, 2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128)],
         diamonds)
    write_csv("validators_diamonds.csv", diamonds)

    print()
    print("=" * 72)
    print("FIGURE: per-family size sweeps")
    print("=" * 72)
    families = []
    emit("dense multiple inheritance",
         [alternate(dense_mi_dag(n, seed=7)[0])
          for n in (8, 16, 32, 64, 121, 200, 290, 375, 600, 1200, 2000, 3000,
                    4500, 6000, 8000)],
         families)
    emit("sparse multiple inheritance",
         [alternate(random_dag(n, 2, seed=7)[0])
          for n in (8, 16, 32, 64, 121, 200, 290, 375)],
         families)
    emit("chain",
         [alternate(chain(n)[0]) for n in (8, 16, 32, 64, 121, 180, 250)],
         families)
    emit("binary tree",
         [alternate(binary_tree(d)[0]) for d in (3, 4, 5, 6, 7, 8)],
         families)
    write_csv("validators_families.csv", families)

    print()
    print("=" * 72)
    print("FIGURE: crossover model (time ratio vs reachable pairs per edge)")
    print("=" * 72)
    model = diamonds + families
    by_family = {}
    for row in model:
        by_family.setdefault(row[0], []).append(row)
    for label, fam_rows in by_family.items():
        print(f"\n% {label}")
        _print_coords("pair/flattening time ratio vs pairs-per-edge",
                      [f"({r[7]},{r[8]})" for r in fam_rows])
    write_csv("validators_crossover_model.csv", model)


if __name__ == "__main__":
    main()
