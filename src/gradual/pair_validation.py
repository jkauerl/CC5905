from typing import Dict, List, Set, Tuple

from .definitions import Environment, Specification
from .neighbours import ancestors
from .subtyping import is_subtype_spec

""" Per-pair validator.

Purely structural on the graph plus the declared specification assignment;
no evidence is computed here.  Over the ancestors of a node
(src/gradual/neighbours.py):

    PairValid(Sigma)  <=>  for all N in nodes.  for all A in Anc(N).  Sigma(N) <~s Sigma(A)

Each pair is asked independently: there is no joint check between siblings,
and the witnesses for different ancestor relations may be unrelated.  Note
that this is strictly stronger than the per-edge check, because consistent
subtyping is not transitive in the presence of the unknown type.
"""


Sigma = Dict[str, Specification]
Pair = Tuple[str, str]


def ancestor_pairs(environment: Environment) -> Set[Pair]:
    """The pairs the validator checks: (N, A) with A in Anc(N).

    :param environment: The Environment object representing the type system.
    :return: The set of pairs (N, A) with N <: A, both nodes.
    """
    return {
        (node.name, ancestor)
        for node in environment.Ns
        for ancestor in ancestors(environment, node.name)
    }


def strict_ancestor_pairs(environment: Environment) -> Set[Pair]:
    """The ancestor pairs with N != A.

    :param environment: The Environment object representing the type system.
    :return: The set of pairs (N, A) with N <: A and N != A.
    """
    return {(n, a) for n, a in ancestor_pairs(environment) if n != a}


def failing_pairs(environment: Environment, sigma: Sigma) -> List[Pair]:
    """Every ancestor pair at which consistent subtyping fails.

    :param environment: The Environment object representing the type system.
    :param sigma: The specification assignment.
    :return: The list of pairs (N, A), A in Anc(N), with Sigma(N) not <~s Sigma(A).
    """
    failures: List[Pair] = []
    for node in environment.Ns:
        specification = sigma[node.name]
        for ancestor in ancestors(environment, node.name):
            if not is_subtype_spec(environment, specification, sigma[ancestor]):
                failures.append((node.name, ancestor))
    return failures


def pair_valid(environment: Environment, sigma: Sigma) -> bool:
    """Per-pair validator: consistent subtyping against every ancestor.

    :param environment: The Environment object representing the type system.
    :param sigma: The specification assignment.
    :return: True iff Sigma(N) <~s Sigma(A) for every node N and every A in Anc(N).
    """
    for node in environment.Ns:
        specification = sigma[node.name]
        for ancestor in ancestors(environment, node.name):
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
