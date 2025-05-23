from collections import defaultdict

from .definitions import ClassName, FunctionType, Psi, Signature, Specification, Type
from .functions import get_all_parent_specifications, names
from .propositions import is_subtype_spec

""" Node validation propositions
"""


def is_minimal_specification(class_name: ClassName, s: Specification, psi: Psi) -> bool:
    """Check if the given specification is minimal for the given class name.

    :param class_name: The class name to check.
    :param s: The specification to check.
    :param psi: The Psi object representing the type system.
    :return: True if the specification is minimal, False otherwise.
    """
    parent_specs = get_all_parent_specifications(psi, class_name)
    for sp in parent_specs:
        if not is_subtype_spec(s, Specification(sp), psi):
            return False
    return True


def is_includes_node(class_name: ClassName, s: Specification, psi: Psi) -> bool:
    """Check if all signatures of class_name in psi.sigma are included in s."""
    if class_name.name not in psi.sigma:
        return False

    sigs_n = psi.sigma[class_name.name]
    sigs_s = s.signatures

    s_dict = {sig.var: sig.type for sig in sigs_s}
    for sig in sigs_n:
        if sig.var not in s_dict:
            return False
        if sig.type != s_dict[sig.var]:
            return False
    return True


def exists_all_signatures(psi: Psi, class_name: ClassName, s: Specification) -> bool:
    """
    Check if the specification s includes exactly the signatures that are
    either declared by the class N or inherited from its parents, with no extra methods.

    :param psi: The Psi object representing the type system.
    :param class_name: The class name to check.
    :param s: The specification to check.
    :return: True if all signatures are correct, False otherwise.
    """

    given_signatures = names(s)

    # Gather the method names declared by class N
    own_signatures = {sig.var for sig in psi.sigma[class_name.name]}

    parent_specs_raw = get_all_parent_specifications(psi, class_name)
    parent_specs = [
        Specification(spec) if not isinstance(spec, Specification) else spec
        for spec in parent_specs_raw
    ]
    inherited_signatures = {
        sig.var for parent in parent_specs for sig in parent.signatures
    }

    expected_signatures = own_signatures.union(inherited_signatures)

    return given_signatures == expected_signatures


def no_overloading(s: Specification) -> bool:
    """Check if the given specification has no overloading.

    :param s: The specification to check.
    :return: True if there is no overloading, False otherwise.
    """
    return len(s.signatures) == len(set(sig.var for sig in s.signatures))


""" Functions to check for cycles in the type system
"""


def build_adjacency_list(psi: Psi) -> dict:
    """Funtion to build an adjacency list from the given Psi object.

    :param psi: The Psi object representing the type system.
    :return: A dictionary representing the adjacency list of the graph.
    """
    adj = defaultdict(list)
    for edge in psi.Es:
        adj[edge.source].append(edge.target)
    return adj


def dfs(node: ClassName, visited: set, stack: set, adj: dict) -> bool:
    """Perform a depth-first search to detect cycles in the graph.

    :param node: The current node being visited.
    :param visited: A set of visited nodes.
    :param stack: A set of nodes in the current path.
    :param adj: A dictionary representing the adjacency list of the graph.

    :return: True if no cycle is detected, False otherwise.
    """
    visited.add(node)
    stack.add(node)
    for neighbor in adj[node]:
        if neighbor not in visited:
            if not dfs(neighbor, visited, stack, adj):
                return False
        elif neighbor in stack:
            return False
    stack.remove(node)
    return True


def acyclic(psi: Psi) -> bool:
    """Check if the given Psi object is acyclic.

    :param psi: The Psi object representing the type system.

    :return: True if the object is acyclic, False otherwise.
    """
    visited = set()
    stack = set()
    adj = build_adjacency_list(psi)
    for node in psi.Ns:
        if node not in visited:
            if not dfs(node, visited, stack, adj):
                return False
    return True


""" Validation of types
"""


def is_valid_type(psi: Psi, type: Type) -> bool:
    """Check if the given type is valid in the Psi object.

    :param psi: The Psi object representing the type system.
    :param type: The type to check.
    :return: True if the type is valid, False otherwise.
    """
    match type:
        case FunctionType(T1s, T2):
            return all([is_valid_type(psi, t) for t in T1s]) and is_valid_type(psi, T2)
        case ClassName(name):
            return name in [n.name for n in psi.Ns]


""" Validation of functions and signatures
"""


def is_valid_signature(psi: Psi, signature: list[Signature]) -> bool:
    """Check if the given signature is valid in the Psi object.
    This is a list of signatures.

    :param psi: The Psi object representing the type system.
    :param signature: The signature to check.
    :return: True if the signature is valid, False otherwise.
    """
    return all([is_valid_type(psi, signature.type) for signature in signature])


def is_valid_function(psi: Psi, function: FunctionType) -> bool:
    """Check if the given function is valid in the Psi object.

    :param psi: The Psi object representing the type system.
    :param function: The function to check.
    :return: True if the function is valid, False otherwise.
    """
    return all([is_valid_type(psi, t) for t in function.domain]) and is_valid_type(
        psi, function.codomain
    )


""" Validation of the graph
"""


def is_valid_node(psi: Psi, node: ClassName) -> bool:
    """Check if the given node is valid in the Psi object."""
    sigs = psi.sigma.get(node.name, [])
    spec = Specification(sigs)
    return (
        is_minimal_specification(node, spec, psi)
        and is_includes_node(node, spec, psi)
        and exists_all_signatures(psi, node, spec)
        and no_overloading(spec)
    )


def is_valid_edge(psi: Psi, class_name_1: ClassName, class_name_2: ClassName) -> bool:
    """Check if the given edge is valid in the Psi object.

    :param psi: The Psi object representing the type system.
    :param class_name_1: The first class name to check.
    :param class_name_2: The
    second class name to check.
    :return: True if the edge is valid, False otherwise.
    """
    return any(
        edge.source == class_name_1 and edge.target == class_name_2 for edge in psi.Es
    )


def is_valid_fun(psi: Psi) -> bool:
    """Check if the given function is valid in the Psi object.

    :param psi: The Psi object representing the type system.
    :param sigma: The function to check.
    :return: True if the function is valid, False otherwise.
    """
    for class_name in psi.Ns:
        if class_name.name in psi.sigma:
            if not is_valid_signature(psi, psi.sigma[class_name.name]):
                return False
    return True


def is_valid_graph(psi: Psi) -> bool:
    """Check if the given graph is valid in the Psi object.

    :param psi: The Psi object representing the type system.
    :return: True if the graph is valid, False otherwise.
    """
    if not is_valid_fun(psi):
        return False
    for class_name in psi.Ns:
        if class_name.name not in psi.sigma:
            return False
        spec = Specification(psi.sigma[class_name.name])
        if not is_minimal_specification(class_name, spec, psi):
            return False
        if not exists_all_signatures(psi, class_name, spec):
            return False
        if not is_valid_signature(psi, spec.signatures):
            return False
    for edge in psi.Es:
        if not is_valid_edge(psi, edge.source, edge.target):
            return False
    if not acyclic(psi):
        return False
    return True
