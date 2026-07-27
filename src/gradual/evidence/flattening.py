from typing import Dict, List, Optional, Tuple

from ...static.types import ClassName
from ..definitions import Environment, Specification
from .definitions import (
    CompleteEvidence,
    Evidence,
    EvidenceSignature,
    EvidenceSpecification,
)
from .functions import (
    interior_gradual_specification,
    lift_gradual_type,
    meet_complete_evidences,
    transitivity_complete_evidences,
)

""" Flattening of the hierarchy: per-node evidence computed in two passes.

Two implementations of the same equations:

- the *naive* one evaluates the recursive equations directly, recomputing
  the evidence of shared ancestors once per path reaching them;
- the *table-driven* (dynamic-programming) one evaluates the nodes in
  topological order, storing each node's evidence in a table so every
  node is computed exactly once.

Both compute, for every node N:

    E_top(N) = MEET_{P in parents(N)} ( edge(N, P) . E_top(P) )   [identity at roots]
    E_bot(N) = MEET_{C in children(N)} ( E_bot(C) . edge(C, N) )  [identity at leaves]
    E_comb(N) = combine(E_top(N), E_bot(N))

and the graph is flattening-valid iff E_comb(N) is non-empty at every node.
"""


Sigma = Dict[str, Specification]
Adjacency = Dict[str, List[ClassName]]


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
) -> CompleteEvidence:
    """Edge evidence: the spec-level interior of the two lifted complete specs.

    :param environment: The Environment object representing the type system.
    :param sigma: The complete specification assignment.
    :param node: The child endpoint of the edge.
    :param parent: The parent endpoint of the edge.
    :return: The CompleteEvidence of the edge (possibly empty).
    """
    lifted_node = lift_specification(sigma[node.name])
    lifted_parent = lift_specification(sigma[parent.name])
    pairs = interior_gradual_specification(environment, lifted_node, lifted_parent)
    return CompleteEvidence({Evidence(s1, s2) for (s1, s2) in pairs})


def identity_complete(sigma: Sigma, node: ClassName) -> CompleteEvidence:
    """Identity complete evidence at a node: the singleton of its lifted spec.

    :param sigma: The complete specification assignment.
    :param node: The node to build the identity evidence for.
    :return: The identity CompleteEvidence at the node.
    """
    lifted = lift_specification(sigma[node.name])
    return CompleteEvidence({Evidence(lifted, lifted)})


def _transitivity(
    environment: Environment,
    complete_evidence_1: CompleteEvidence,
    complete_evidence_2: CompleteEvidence,
) -> CompleteEvidence:
    """Consistent transitivity, normalising the empty result to the empty set."""
    result = transitivity_complete_evidences(
        environment, complete_evidence_1, complete_evidence_2
    )
    if result is None:
        return CompleteEvidence(set())
    return result


def _meet_fold(
    environment: Environment, complete_evidences: List[CompleteEvidence]
) -> CompleteEvidence:
    """Right fold of the complete-evidence meet across the sibling chains."""
    result = complete_evidences[-1]
    for complete_evidence in reversed(complete_evidences[:-1]):
        result = meet_complete_evidences(environment, complete_evidence, result)
    return result


def combine_evidences(
    environment: Environment,
    complete_top: CompleteEvidence,
    complete_bot: CompleteEvidence,
) -> CompleteEvidence:
    """Per-node combination: spec-level interior on the two "N at N" slots.

    :param environment: The Environment object representing the type system.
    :param complete_top: The downward (ancestors) complete evidence.
    :param complete_bot: The upward (descendants) complete evidence.
    :return: The combined CompleteEvidence (possibly empty).
    """
    combined = set()
    for evidence_top in complete_top.evidences:
        for evidence_bot in complete_bot.evidences:
            pairs = interior_gradual_specification(
                environment,
                evidence_bot.specification_2,
                evidence_top.specification_1,
            )
            combined.update(Evidence(s1, s2) for (s1, s2) in pairs)
    return CompleteEvidence(combined)


""" Naive evaluation: direct recursion, no table
"""


def _e_top_naive(
    environment: Environment, sigma: Sigma, parents: Adjacency, node: ClassName
) -> CompleteEvidence:
    """Downward pass at a node by direct recursion (shared ancestors recomputed)."""
    node_parents = parents[node.name]
    if not node_parents:
        return identity_complete(sigma, node)
    chains = [
        _transitivity(
            environment,
            edge_evidence(environment, sigma, node, parent),
            _e_top_naive(environment, sigma, parents, parent),
        )
        for parent in node_parents
    ]
    return _meet_fold(environment, chains)


def _e_bot_naive(
    environment: Environment, sigma: Sigma, children: Adjacency, node: ClassName
) -> CompleteEvidence:
    """Upward pass at a node by direct recursion (shared descendants recomputed)."""
    node_children = children[node.name]
    if not node_children:
        return identity_complete(sigma, node)
    chains = [
        _transitivity(
            environment,
            _e_bot_naive(environment, sigma, children, child),
            edge_evidence(environment, sigma, child, node),
        )
        for child in node_children
    ]
    return _meet_fold(environment, chains)


def e_top_naive(
    environment: Environment, sigma: Sigma, node: ClassName
) -> CompleteEvidence:
    """Downward pass at a node, evaluated by direct recursion.

    :param environment: The Environment object representing the type system.
    :param sigma: The complete specification assignment.
    :param node: The node to compute the evidence for.
    :return: The node's downward CompleteEvidence.
    """
    parents, _ = adjacency(environment)
    return _e_top_naive(environment, sigma, parents, node)


def e_bot_naive(
    environment: Environment, sigma: Sigma, node: ClassName
) -> CompleteEvidence:
    """Upward pass at a node, evaluated by direct recursion.

    :param environment: The Environment object representing the type system.
    :param sigma: The complete specification assignment.
    :param node: The node to compute the evidence for.
    :return: The node's upward CompleteEvidence.
    """
    _, children = adjacency(environment)
    return _e_bot_naive(environment, sigma, children, node)


def flatten_naive(environment: Environment, sigma: Sigma) -> bool:
    """Flattening validator, naive evaluation (recomputes shared ancestors).

    :param environment: The Environment object representing the type system.
    :param sigma: The complete specification assignment.
    :return: True iff the combined evidence is non-empty at every node.
    """
    parents, children = adjacency(environment)
    for node in environment.Ns:
        combined = combine_evidences(
            environment,
            _e_top_naive(environment, sigma, parents, node),
            _e_bot_naive(environment, sigma, children, node),
        )
        if not combined.evidences:
            return False
    return True


""" Table-driven (dynamic-programming) evaluation: topological order
"""


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
    environment: Environment, sigma: Sigma, order: List[ClassName]
) -> Dict[str, CompleteEvidence]:
    """Downward pass over the whole graph, each node computed once.

    :param environment: The Environment object representing the type system.
    :param sigma: The complete specification assignment.
    :param order: A topological order (parents before children).
    :return: The table of downward CompleteEvidences, indexed by node name.
    """
    parents, _ = adjacency(environment)
    table: Dict[str, CompleteEvidence] = {}
    for node in order:
        node_parents = parents[node.name]
        if not node_parents:
            table[node.name] = identity_complete(sigma, node)
            continue
        chains = [
            _transitivity(
                environment,
                edge_evidence(environment, sigma, node, parent),
                table[parent.name],
            )
            for parent in node_parents
        ]
        table[node.name] = _meet_fold(environment, chains)
    return table


def e_bot_table(
    environment: Environment, sigma: Sigma, order: List[ClassName]
) -> Dict[str, CompleteEvidence]:
    """Upward pass over the whole graph, each node computed once.

    :param environment: The Environment object representing the type system.
    :param sigma: The complete specification assignment.
    :param order: A topological order (parents before children); traversed reversed.
    :return: The table of upward CompleteEvidences, indexed by node name.
    """
    _, children = adjacency(environment)
    table: Dict[str, CompleteEvidence] = {}
    for node in reversed(order):
        node_children = children[node.name]
        if not node_children:
            table[node.name] = identity_complete(sigma, node)
            continue
        chains = [
            _transitivity(
                environment,
                table[child.name],
                edge_evidence(environment, sigma, child, node),
            )
            for child in node_children
        ]
        table[node.name] = _meet_fold(environment, chains)
    return table


def flatten_dp(environment: Environment, sigma: Sigma) -> bool:
    """Flattening validator, table-driven evaluation (each node computed once).

    :param environment: The Environment object representing the type system.
    :param sigma: The complete specification assignment.
    :return: True iff the combined evidence is non-empty at every node.
    """
    order = topological_order(environment)
    if order is None:
        return False
    top = e_top_table(environment, sigma, order)
    bot = e_bot_table(environment, sigma, order)
    for node in environment.Ns:
        combined = combine_evidences(environment, top[node.name], bot[node.name])
        if not combined.evidences:
            return False
    return True
