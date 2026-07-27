import os
import random
import re
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gradual.definitions import Edge, Environment, Signature, Specification  # noqa: E402
from src.gradual.evidence.flattening import flatten_dp, flatten_naive  # noqa: E402
from src.gradual.types import Unknown  # noqa: E402
from src.static.types import BottomType, ClassName, TopType  # noqa: E402

ROCQ_DIR = r"C:\Users\kauer\Documents\Universidad\Magister\thesis\rocq"

""" Differential test: the Python flattening (naive and table-driven) against
the mechanized Rocq validators (flatten_graph and flatten_graph_table), on the
same graph instances.

An instance is (nodes, edges, specs):
  - nodes: 1..n  (Rocq Name = nat; Python ClassName(str(i)))
  - edges: (child, parent) pairs, parent index < child index (acyclic), no
    self-loops
  - specs: complete spec assignment, fields from {1, 2, 3}, first-order types
    only (names, top, bottom, unknown); fields emitted in ascending order
    (the canonical order the Rocq computables expect)

Function-typed fields are deliberately excluded: the Python prototype's
function types are structurally different from the mechanization's, so the
comparison is scoped to the first-order fragment.
"""

# A type is one of: ("name", i), ("top",), ("bot",), ("unk",)
Ty = Tuple
Spec = Dict[int, Ty]
Instance = Tuple[str, int, List[Tuple[int, int]], Dict[int, Spec]]


def crafted_instances() -> List[Instance]:
    instances: List[Instance] = []

    # Six-class worked example (accepted by the set-valued validator).
    instances.append((
        "worked_example", 6,
        [(3, 1), (2, 1), (5, 3), (5, 2), (4, 3), (4, 2), (6, 5), (6, 4)],
        {
            1: {},
            2: {1: ("name", 2)},
            3: {1: ("name", 3), 3: ("unk",)},
            4: {1: ("unk",), 2: ("name", 1), 3: ("unk",)},
            5: {1: ("name", 5), 3: ("unk",)},
            6: {1: ("unk",), 2: ("name", 1), 3: ("name", 4)},
        },
    ))

    # Crossing diamond / separation example (accepted; PairValid holds).
    # P=1, Q=2, D=3, E=4, A1=5, A2=6, N=7, C1=8, C2=9.
    instances.append((
        "separation", 9,
        [(3, 1), (3, 2), (4, 1), (4, 2), (7, 5), (7, 6), (8, 7), (9, 7)],
        {
            1: {}, 2: {}, 3: {}, 4: {},
            5: {2: ("name", 1)},
            6: {2: ("name", 2)},
            7: {2: ("unk",)},
            8: {2: ("name", 3)},
            9: {2: ("name", 4)},
        },
    ))

    # Incompatible edge: B {x : Q} extends A {x : P}, P and Q unrelated.
    instances.append((
        "incompatible_edge", 4,
        [(4, 3)],
        {1: {}, 2: {}, 3: {1: ("name", 1)}, 4: {1: ("name", 2)}},
    ))

    # The certificate chains 0 <: 1 <: 2 with x typed bot/?/top (accept)
    # and top/?/bot (reject), shifted to 1-based names.
    instances.append((
        "chain_positive", 3,
        [(2, 1), (3, 2)],
        {1: {1: ("top",)}, 2: {1: ("unk",)}, 3: {1: ("bot",)}},
    ))
    instances.append((
        "chain_negative", 3,
        [(2, 1), (3, 2)],
        {1: {1: ("bot",)}, 2: {1: ("unk",)}, 3: {1: ("top",)}},
    ))

    return instances


def random_instances(count: int, seed: int = 42) -> List[Instance]:
    rng = random.Random(seed)
    instances: List[Instance] = []
    for i in range(count):
        n = rng.randint(3, 6)
        edges: List[Tuple[int, int]] = []
        for child in range(2, n + 1):
            k = rng.choice([0, 1, 1, 1, 2, 2])
            parents = rng.sample(range(1, child), min(k, child - 1))
            edges.extend((child, p) for p in parents)
        specs: Dict[int, Spec] = {}
        for node in range(1, n + 1):
            spec: Spec = {}
            for field in (1, 2, 3):
                r = rng.random()
                if r < 0.35:
                    continue
                elif r < 0.55:
                    spec[field] = ("unk",)
                elif r < 0.65:
                    spec[field] = ("top",)
                elif r < 0.72:
                    spec[field] = ("bot",)
                else:
                    spec[field] = ("name", rng.randint(1, n))
            specs[node] = spec
        instances.append((f"rand{i:02d}", n, edges, specs))
    return instances


# ---------------------------------------------------------------- Python side

def py_type(t: Ty):
    match t[0]:
        case "name":
            return ClassName(str(t[1]))
        case "top":
            return TopType()
        case "bot":
            return BottomType()
        case "unk":
            return Unknown()


def py_verdicts(inst: Instance) -> Tuple[bool, bool]:
    _, n, edges, specs = inst
    nodes = [ClassName(str(i)) for i in range(1, n + 1)]
    es = [Edge(ClassName(str(c)), ClassName(str(p))) for (c, p) in edges]
    sigma = {
        str(i): Specification(
            {Signature(str(f), py_type(t)) for f, t in specs.get(i, {}).items()}
        )
        for i in range(1, n + 1)
    }
    environment = Environment(nodes, es, sigma)
    return flatten_naive(environment, sigma), flatten_dp(environment, sigma)


# ---------------------------------------------------------------- Rocq side

def rocq_type(t: Ty) -> str:
    match t[0]:
        case "name":
            return f"GTName {t[1]}"
        case "top":
            return "GTTop"
        case "bot":
            return "GTBot"
        case "unk":
            return "GTUnknown"


def rocq_instance(idx: int, inst: Instance) -> str:
    name, n, edges, specs = inst
    node_list = "; ".join(str(i) for i in range(1, n + 1))
    edge_list = "; ".join(f"({c},{p})" for (c, p) in edges)
    arms = []
    for node in range(1, n + 1):
        fields = sorted(specs.get(node, {}).items())
        entries = "; ".join(f"({f}, {rocq_type(t)})" for f, t in fields)
        arms.append(f"  | {node} => [{entries}]")
    return f"""
Definition env{idx} : Env := mkEnv [{node_list}] [{edge_list}].
Definition Sigma{idx} (N : Name) : GSpec :=
  match N with
{chr(10).join(arms)}
  | _ => []
  end.
Definition phi{idx} : GGraph := mkGGraph env{idx} Sigma{idx}.
Eval lazy in ("{name}", flatten_graph phi{idx} Sigma{idx}, flatten_graph_table phi{idx} Sigma{idx}).
"""


def rocq_verdicts(instances: List[Instance]) -> Dict[str, Tuple[bool, bool]]:
    parts = [
        "From Stdlib Require Import List Bool PeanoNat String.",
        "Import ListNotations.",
        "Open Scope string_scope.",
        "Require Import StaticSystem.",
        "Require Import StaticUtils.",
        "Require Import GradualSystem.",
        "Require Import EvidenceSystem.",
        "Require Import EvidenceComputable.",
        "Require Import FlattenTable.",
    ]
    for idx, inst in enumerate(instances):
        parts.append(rocq_instance(idx, inst))
    source = "\n".join(parts) + "\n"

    path = os.path.join(ROCQ_DIR, "DiffCheck.v")
    with open(path, "w", encoding="utf-8") as f:
        f.write(source)
    try:
        result = subprocess.run(
            ["rocq", "compile", "DiffCheck.v"],
            cwd=ROCQ_DIR, capture_output=True, text=True, timeout=1200,
        )
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            raise RuntimeError("rocq compile DiffCheck.v failed")
        out = result.stdout
    finally:
        for ext in (".v", ".vo", ".glob"):
            p = os.path.join(ROCQ_DIR, "DiffCheck" + ext)
            if os.path.exists(p):
                os.remove(p)
        aux = os.path.join(ROCQ_DIR, ".DiffCheck.aux")
        if os.path.exists(aux):
            os.remove(aux)

    verdicts: Dict[str, Tuple[bool, bool]] = {}
    for m in re.finditer(r'\("([^"]+)",\s*(true|false),\s*(true|false)\)', out):
        verdicts[m.group(1)] = (m.group(2) == "true", m.group(3) == "true")
    return verdicts


# ---------------------------------------------------------------- main

def main() -> None:
    instances = crafted_instances() + random_instances(40)
    print(f"instances: {len(instances)}")

    rocq = rocq_verdicts(instances)
    if len(rocq) != len(instances):
        print(f"WARNING: parsed {len(rocq)} Rocq verdicts for {len(instances)} instances")

    header = f"{'instance':<18} {'py naive':>9} {'py dp':>7} {'rocq':>6} {'rocq tbl':>9}  status"
    print(header)
    agree = 0
    diverge: List[str] = []
    for inst in instances:
        name = inst[0]
        pn, pd = py_verdicts(inst)
        rq = rocq.get(name)
        if rq is None:
            print(f"{name:<18} {str(pn):>9} {str(pd):>7} {'?':>6} {'?':>9}  MISSING")
            diverge.append(name)
            continue
        rf, rt = rq
        ok = pn == pd == rf == rt
        status = "ok" if ok else "DIVERGE"
        if ok:
            agree += 1
        else:
            diverge.append(name)
        print(f"{name:<18} {str(pn):>9} {str(pd):>7} {str(rf):>6} {str(rt):>9}  {status}")

    print(f"\nagreement: {agree}/{len(instances)}")
    if diverge:
        print("divergent instances:", ", ".join(diverge))
        sys.exit(1)
    print("all four validators agree on every instance")


if __name__ == "__main__":
    main()
