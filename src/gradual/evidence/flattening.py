from itertools import product
from typing import Dict, Iterable, List, Optional, Set, Tuple

from ...static.functions import join
from ...static.subtyping import is_subtype
from ...static.types import BottomType, ClassName, Type
from ..definitions import Environment, Specification
from .definitions import (
    Evidence,
    EvidenceInterval,
    EvidenceSignature,
    EvidenceSpecification,
)
from .functions import (
    interior_gradual_specification,
    lift_gradual_type,
    meet_evidences,
    transitivity_specifications,
)

""" Flattening of the hierarchy, in two passes over a topological order:

    E_top(N) = MEET_{P in parents(N)}  ( edge(N, P) . E_top(P) )   [identity at roots]
    E_bot(N) = MEET_{C in children(N)} ( E_bot(C) . edge(C, N) )   [identity at leaves]
    E_comb(N) = combine(E_top(N), E_bot(N))

Valid iff E_comb(N) is non-empty at every node.  The anchored variant stores
combine(E_top(N), E_bot(N) ∪ anchor_N(E_bot(N))) per node, acceptance still
gated on the un-anchored combination.  Evidence sets are mutable sets of
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
        table[node.name] = _meet_fold(environment, chains)
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


""" The value anchor: alongside each upward element, the variant whose view
lower bound is the value slot's lower bound joined with the node's own lifted
declaration bound (upper bounds kept, filtered by interval well-formedness).
"""


def anchor_floor(sigma: Sigma, node: ClassName) -> Dict[str, Type]:
    """Per-field floor at a node: the lower bound of its lifted declaration.

    :param sigma: The complete specification assignment.
    :param node: The node whose declaration provides the floors.
    :return: A map from field name to the declared lower bound.
    """
    lifted = lift_specification(sigma[node.name])
    return {sig.var: sig.interval.lower_bound for sig in lifted.signatures}


def anchor_views(
    environment: Environment,
    value_spec: EvidenceSpecification,
    floor: Dict[str, Type],
    view_spec: EvidenceSpecification,
) -> Set[EvidenceSpecification]:
    """All anchored variants of a view spec against its value spec.

    Per field: the new lower bound ranges over the join of the value slot's
    lower bound (the view's own when the field has no value entry) with the
    node's floor, kept only when it stays below the view's upper bound.

    :param environment: The Environment object representing the type system.
    :param value_spec: The element's value slot.
    :param floor: The node's per-field declaration floors.
    :param view_spec: The element's view slot.
    :return: The set of anchored view specifications (possibly empty).
    """
    value_by_var = {sig.var: sig for sig in value_spec.signatures}
    per_var: List[Set[EvidenceSignature]] = []
    for sig in view_spec.signatures:
        interval = sig.interval
        value_sig = value_by_var.get(sig.var)
        value_lower = (
            value_sig.interval.lower_bound
            if value_sig is not None
            else interval.lower_bound
        )
        floor_lower = floor.get(sig.var, BottomType())
        candidates = set()
        for t in join(environment, value_lower, floor_lower):
            if is_subtype(environment, t, interval.upper_bound):
                candidates.add(
                    EvidenceSignature(
                        sig.var, EvidenceInterval(t, interval.upper_bound)
                    )
                )
        if not candidates:
            return set()
        per_var.append(candidates)
    views = set()
    for combo in product(*per_var):
        views.add(EvidenceSpecification(set(combo)))
    return views


def anchored_evidences(
    environment: Environment, sigma: Sigma, node: ClassName, evidences: EvidenceSet
) -> EvidenceSet:
    """The anchored variants of an upward evidence set at a node.

    :param environment: The Environment object representing the type system.
    :param sigma: The complete specification assignment.
    :param node: The node whose declaration anchors the views.
    :param evidences: The node's upward evidence set.
    :return: The set of anchored variants (value slots kept).
    """
    floor = anchor_floor(sigma, node)
    result: EvidenceSet = set()
    for evidence in evidences:
        for view in anchor_views(
            environment, evidence.specification_1, floor, evidence.specification_2
        ):
            result.add(Evidence(evidence.specification_1, view))
    return result


def flatten_anchored(environment: Environment, sigma: Sigma) -> bool:
    """Anchored flattening: the validator that also builds the anchored table.

    Acceptance is gated on the un-anchored combination; the anchored entry
    grows the same set in place with the combinations against the anchored
    variants.

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
        entry = combine_evidences(environment, top[node.name], bot[node.name])
        if not entry:
            return False
        extra = anchored_evidences(environment, sigma, node, bot[node.name])
        if extra:
            entry.update(combine_evidences(environment, top[node.name], extra))
    return True
