from typing import Dict, List, Set, Tuple

from ..static.types import ClassName
from .definitions import Environment, Specification
from .subtyping import is_subtype_spec

""" Per-pair naive validator.

Two definitions, both purely structural on the graph plus the declared
specification assignment --- no evidence is computed anywhere here.

Edge reachability (Figure 53) is the strict transitive closure of the edge
relation: one direct edge is a path (R-EDGE), and a direct edge extended by
an existing path is a path (R-STEP).  It carries no subtyping content; it
only says that A is graph-reachable from N along directed edges.

The per-pair validator (Figure 54) then asks consistent subtyping at every
reachable pair, and only there:

    PairValid(Sigma)  <=>  for all N, A.  ( N ->+ A  =>  Sigma(N) <~s Sigma(A) )

The quantification is over every ordered pair of nodes, but a pair whose
antecedent fails satisfies the implication vacuously, so the implementation
enumerates the reachable pairs directly --- the two readings agree.

Each pair is asked independently: there is no joint check between siblings,
and the witnesses for different ancestor relations may be unrelated.  Note
that this is strictly stronger than the per-edge check, because consistent
subtyping is not transitive in the presence of the unknown type.
"""


Sigma = Dict[str, Specification]
Pair = Tuple[str, str]


def parent_adjacency(environment: Environment) -> Dict[str, List[ClassName]]:
    """Map every node to its direct parents.

    :param environment: The Environment object representing the type system.
    :return: A map from node name to the list of its direct parents.
    """
    parents: Dict[str, List[ClassName]] = {node.name: [] for node in environment.Ns}
    for edge in environment.Es:
        parents[edge.source.name].append(edge.target)
    return parents


def reachable_ancestors(environment: Environment) -> Dict[str, Set[str]]:
    """The strict transitive closure of the edge relation, per node.

    Computed by one traversal per node, so a node's ancestor set is derived
    without reusing any other node's --- the closure mirrors the inductive
    definition rather than sharing work across nodes.

    :param environment: The Environment object representing the type system.
    :return: A map from node name to the names of the nodes it reaches.
    """
    parents = parent_adjacency(environment)
    ancestors: Dict[str, Set[str]] = {}
    for node in environment.Ns:
        reached: Set[str] = set()
        pending = list(parents[node.name])
        while pending:
            ancestor = pending.pop()
            if ancestor.name in reached:
                continue
            reached.add(ancestor.name)
            pending.extend(parents[ancestor.name])
        ancestors[node.name] = reached
    return ancestors


def reachable_pairs(environment: Environment) -> Set[Pair]:
    """The reachability relation as an explicit set of pairs.

    :param environment: The Environment object representing the type system.
    :return: The set of pairs (N, A) such that N reaches A along directed edges.
    """
    ancestors = reachable_ancestors(environment)
    return {
        (name, ancestor) for name, reached in ancestors.items() for ancestor in reached
    }


def failing_pairs(environment: Environment, sigma: Sigma) -> List[Pair]:
    """Every reachable pair at which consistent subtyping fails.

    :param environment: The Environment object representing the type system.
    :param sigma: The specification assignment.
    :return: The list of reachable pairs (N, A) with Sigma(N) not <~s Sigma(A).
    """
    ancestors = reachable_ancestors(environment)
    failures: List[Pair] = []
    for node in environment.Ns:
        specification = sigma[node.name]
        for ancestor in ancestors[node.name]:
            if not is_subtype_spec(environment, specification, sigma[ancestor]):
                failures.append((node.name, ancestor))
    return failures


def pair_valid(environment: Environment, sigma: Sigma) -> bool:
    """Per-pair naive validator: consistent subtyping at every reachable pair.

    :param environment: The Environment object representing the type system.
    :param sigma: The specification assignment.
    :return: True iff Sigma(N) <~s Sigma(A) holds for every pair with N ->+ A.
    """
    ancestors = reachable_ancestors(environment)
    for node in environment.Ns:
        specification = sigma[node.name]
        for ancestor in ancestors[node.name]:
            if not is_subtype_spec(environment, specification, sigma[ancestor]):
                return False
    return True


def per_edge_valid(environment: Environment, sigma: Sigma) -> bool:
    """The weaker per-edge check: consistent subtyping at every direct edge.

    Kept for contrast: consistent subtyping is not transitive, so this accepts
    hierarchies that the per-pair validator rejects.

    :param environment: The Environment object representing the type system.
    :param sigma: The specification assignment.
    :return: True iff Sigma(N) <~s Sigma(A) holds for every edge (N, A).
    """
    for edge in environment.Es:
        if not is_subtype_spec(
            environment, sigma[edge.source.name], sigma[edge.target.name]
        ):
            return False
    return True
