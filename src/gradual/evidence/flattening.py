from typing import Dict, Iterable, List, Optional, Set, Tuple

from ...static.types import ClassName
from ..definitions import Environment, Specification
from .definitions import (
    Evidence,
    EvidenceSignature,
    EvidenceSpecification,
)
from .functions import (
    interior_gradual_specification,
    join_evidences,
    lift_gradual_type,
    meet_evidences,
    transitivity_specifications,
)

""" Flattening of the hierarchy, in two passes over a topological order:

    E_top(N) = MEET_{P in parents(N)}  ( edge(N, P) . E_top(P) )   [identity at roots]
    E_bot(N) = JOIN_{C in children(N)} ( E_bot(C) . edge(C, N) )   [identity at leaves]
    E_comb(N) = combine(E_top(N), E_bot(N))

Valid iff E_comb(N) is non-empty at every node; this decides NonDegenerate
(src/gradual/non_degenerate.py).  The top pass meets across parents, the
bottom pass joins across children.  Evidence sets are mutable sets of
Evidence updated in place.
"""


Sigma = Dict[str, Specification]
Adjacency = Dict[str, List[ClassName]]
EvidenceSet = Set[Evidence]


def adjacency(environment: Environment) -> Tuple[Adjacency, Adjacency]:
    """Precompute the parent and child adjacency of every node.

    :param environment: The Environment object representing the type system.
    :return: A pair (parents, children) of maps from node name to node lists.
    """
    parents: Adjacency = {node.name: [] for node in environment.Ns}
    children: Adjacency = {node.name: [] for node in environment.Ns}
    for edge in environment.Es:
        parents[edge.source.name].append(edge.target)
        children[edge.target.name].append(edge.source)
    return parents, children


def lift_specification(specification: Specification) -> EvidenceSpecification:
    """Lift a (gradual) specification pointwise to an evidence specification.

    :param specification: The specification to lift.
    :return: The lifted EvidenceSpecification.
    """
    return EvidenceSpecification(
        {
            EvidenceSignature(sig.var, lift_gradual_type(sig.type))
            for sig in specification.signatures
        }
    )


def edge_evidence(
    environment: Environment, sigma: Sigma, node: ClassName, parent: ClassName
) -> EvidenceSet:
    """Edge evidence: the spec-level interior of the two lifted complete specs.

    :param environment: The Environment object representing the type system.
    :param sigma: The complete specification assignment.
    :param node: The child endpoint of the edge.
    :param parent: The parent endpoint of the edge.
    :return: The set of edge Evidences (possibly empty).
    """
    lifted_node = lift_specification(sigma[node.name])
    lifted_parent = lift_specification(sigma[parent.name])
    pairs = interior_gradual_specification(environment, lifted_node, lifted_parent)
    return {Evidence(s1, s2) for (s1, s2) in pairs}


def edge_table(
    environment: Environment, sigma: Sigma
) -> Dict[Tuple[str, str], EvidenceSet]:
    """Edge evidence for every edge, computed once and shared by both passes.

    :param environment: The Environment object representing the type system.
    :param sigma: The complete specification assignment.
    :return: A map from (child name, parent name) to the edge evidence set.
    """
    lifted = {node.name: lift_specification(sigma[node.name]) for node in environment.Ns}
    table: Dict[Tuple[str, str], EvidenceSet] = {}
    for edge in environment.Es:
        pairs = interior_gradual_specification(
            environment, lifted[edge.source.name], lifted[edge.target.name]
        )
        table[(edge.source.name, edge.target.name)] = {
            Evidence(s1, s2) for (s1, s2) in pairs
        }
    return table


def identity_evidences(sigma: Sigma, node: ClassName) -> EvidenceSet:
    """Identity evidence at a node: the singleton of its lifted spec.

    :param sigma: The complete specification assignment.
    :param node: The node to build the identity evidence for.
    :return: The identity evidence set at the node.
    """
    lifted = lift_specification(sigma[node.name])
    return {Evidence(lifted, lifted)}


def trans_evidences(
    environment: Environment, evidences_1: EvidenceSet, evidences_2: EvidenceSet
) -> EvidenceSet:
    """Consistent transitivity of two evidence sets, accumulated in place.

    :param environment: The Environment object representing the type system.
    :param evidences_1: The first evidence set.
    :param evidences_2: The second evidence set.
    :return: The set of composed Evidences (possibly empty).
    """
    result: EvidenceSet = set()
    for evidence_1 in evidences_1:
        for evidence_2 in evidences_2:
            result.update(
                transitivity_specifications(environment, evidence_1, evidence_2)
            )
    return result


def meet_evidence_sets(
    environment: Environment, evidences_1: EvidenceSet, evidences_2: EvidenceSet
) -> EvidenceSet:
    """Meet of two evidence sets, accumulated in place.

    :param environment: The Environment object representing the type system.
    :param evidences_1: The first evidence set.
    :param evidences_2: The second evidence set.
    :return: The set of met Evidences (possibly empty).
    """
    result: EvidenceSet = set()
    for evidence_1 in evidences_1:
        for evidence_2 in evidences_2:
            result.update(meet_evidences(environment, evidence_1, evidence_2))
    return result


def _meet_fold(
    environment: Environment, evidence_sets: List[EvidenceSet]
) -> EvidenceSet:
    """Right fold of the evidence-set meet across the sibling chains."""
    result = evidence_sets[-1]
    for evidence_set in reversed(evidence_sets[:-1]):
        result = meet_evidence_sets(environment, evidence_set, result)
    return result


def join_evidence_sets(
    environment: Environment, evidences_1: EvidenceSet, evidences_2: EvidenceSet
) -> EvidenceSet:
    """Join of two evidence sets, accumulated in place.

    :param environment: The Environment object representing the type system.
    :param evidences_1: The first evidence set.
    :param evidences_2: The second evidence set.
    :return: The set of joined Evidences (possibly empty).
    """
    result: EvidenceSet = set()
    for evidence_1 in evidences_1:
        for evidence_2 in evidences_2:
            result.update(join_evidences(environment, evidence_1, evidence_2))
    return result


def _join_fold(
    environment: Environment, evidence_sets: List[EvidenceSet]
) -> EvidenceSet:
    """Right fold of the evidence-set join across the sibling chains."""
    result = evidence_sets[-1]
    for evidence_set in reversed(evidence_sets[:-1]):
        result = join_evidence_sets(environment, evidence_set, result)
    return result


def combine_evidences(
    environment: Environment,
    top_evidences: EvidenceSet,
    bot_evidences: Iterable[Evidence],
) -> EvidenceSet:
    """Per-node combination: spec-level interior on the two "N at N" slots.

    :param environment: The Environment object representing the type system.
    :param top_evidences: The downward (ancestors) evidence set.
    :param bot_evidences: The upward (descendants) evidences.
    :return: The combined evidence set (possibly empty).
    """
    combined: EvidenceSet = set()
    for evidence_top in top_evidences:
        for evidence_bot in bot_evidences:
            pairs = interior_gradual_specification(
                environment,
                evidence_bot.specification_2,
                evidence_top.specification_1,
            )
            combined.update(Evidence(s1, s2) for (s1, s2) in pairs)
    return combined


def topological_order(environment: Environment) -> Optional[List[ClassName]]:
    """Order the nodes so that every node appears after all its parents.

    :param environment: The Environment object representing the type system.
    :return: The ordered list of nodes, or None if the hierarchy is cyclic.
    """
    parents, children = adjacency(environment)
    pending = {node.name: len(parents[node.name]) for node in environment.Ns}
    ready = [node for node in environment.Ns if pending[node.name] == 0]
    order: List[ClassName] = []
    while ready:
        node = ready.pop()
        order.append(node)
        for child in children[node.name]:
            pending[child.name] -= 1
            if pending[child.name] == 0:
                ready.append(child)
    if len(order) != len(environment.Ns):
        return None
    return order


def e_top_table(
    environment: Environment,
    sigma: Sigma,
    order: List[ClassName],
    edges: Optional[Dict[Tuple[str, str], EvidenceSet]] = None,
) -> Dict[str, EvidenceSet]:
    """Downward pass over the whole graph, each node computed once.

    :param environment: The Environment object representing the type system.
    :param sigma: The complete specification assignment.
    :param order: A topological order (parents before children).
    :param edges: An edge_table to reuse; computed on the spot when absent.
    :return: The table of downward evidence sets, indexed by node name.
    """
    if edges is None:
        edges = edge_table(environment, sigma)
    parents, _ = adjacency(environment)
    table: Dict[str, EvidenceSet] = {}
    for node in order:
        node_parents = parents[node.name]
        if not node_parents:
            table[node.name] = identity_evidences(sigma, node)
            continue
        chains = [
            trans_evidences(
                environment,
                edges[(node.name, parent.name)],
                table[parent.name],
            )
            for parent in node_parents
        ]
        table[node.name] = _meet_fold(environment, chains)
    return table


def e_bot_table(
    environment: Environment,
    sigma: Sigma,
    order: List[ClassName],
    edges: Optional[Dict[Tuple[str, str], EvidenceSet]] = None,
) -> Dict[str, EvidenceSet]:
    """Upward pass over the whole graph, each node computed once.

    :param environment: The Environment object representing the type system.
    :param sigma: The complete specification assignment.
    :param order: A topological order (parents before children); traversed reversed.
    :param edges: An edge_table to reuse; computed on the spot when absent.
    :return: The table of upward evidence sets, indexed by node name.
    """
    if edges is None:
        edges = edge_table(environment, sigma)
    _, children = adjacency(environment)
    table: Dict[str, EvidenceSet] = {}
    for node in reversed(order):
        node_children = children[node.name]
        if not node_children:
            table[node.name] = identity_evidences(sigma, node)
            continue
        chains = [
            trans_evidences(
                environment,
                table[child.name],
                edges[(child.name, node.name)],
            )
            for child in node_children
        ]
        table[node.name] = _join_fold(environment, chains)
    return table


def flatten_dp(environment: Environment, sigma: Sigma) -> bool:
    """Flattening validator: each node's evidence computed exactly once.

    :param environment: The Environment object representing the type system.
    :param sigma: The complete specification assignment.
    :return: True iff the combined evidence is non-empty at every node.
    """
    order = topological_order(environment)
    if order is None:
        return False
    edges = edge_table(environment, sigma)
    top = e_top_table(environment, sigma, order, edges)
    bot = e_bot_table(environment, sigma, order, edges)
    for node in environment.Ns:
        if not combine_evidences(environment, top[node.name], bot[node.name]):
            return False
    return True
