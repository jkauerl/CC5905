from collections import defaultdict

from .definitions import (
    BottomType,
    ClassName,
    FunctionType,
    Psi,
    Specification,
    TopType,
    Type,
)
from .functions import get_all_parent_specifications, names

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


""" Propositions to check the type system
"""


def is_direct_subtype(
    psi: Psi, class_name_1: ClassName, class_name_2: ClassName
) -> bool:
    """Check if class_name_1 is a direct subtype of class_name_2.

    :param psi: The Psi object representing the type system.
    :param class_name_1: The first class name to check.
    :param class_name_2: The second class name to check.
    :return: True if class_name_1 is a direct subtype of class_name_2, False otherwise.
    """
    for edge in psi.Es:
        if edge.source == class_name_1 and edge.target == class_name_2:
            return True
    return False


def is_subtype(psi: Psi, t1: Type, t2: Type, visited=None) -> bool:
    """Check if t1 is a subtype of t2 in the Psi type system.

    :param psi: The Psi object representing the type system.
    :param t1: The first type to check.
    :param t2: The second type to check.
    :param visited: A set of visited types to avoid cycles.
    :return: True if t1 is a subtype of t2, False otherwise.
    """
    if visited is None:
        visited = set()

    if (t1, t2) in visited:
        return False
    visited.add((t1, t2))

    if t1 == t2:
        return True

    if isinstance(t2, TopType):
        return True

    if isinstance(t1, BottomType):
        return True

    if isinstance(t1, FunctionType) and isinstance(t2, FunctionType):
        if len(t1.domain) != len(t2.domain):
            return False
        domain_check = all(
            is_subtype(psi, t2_arg, t1_arg, visited)
            for t1_arg, t2_arg in zip(t1.domain, t2.domain)
        )
        codomain_check = is_subtype(psi, t1.codomain, t2.codomain, visited)
        return domain_check and codomain_check

    if isinstance(t1, ClassName) and isinstance(t2, ClassName):
        for edge in psi.Es:
            if edge.source == t1:
                if is_subtype(psi, edge.target, t2, visited):
                    return True
    return False


def is_subtype_type(t1: Type, t2: Type, psi: Psi) -> bool:
    match (t1, t2):
        case (ClassName(n1), ClassName(n2)):
            return is_subtype(psi, ClassName(n1), ClassName(n2))
        case (FunctionType(dom1, cod1), FunctionType(dom2, cod2)):
            return (
                len(dom1) == len(dom2)
                and all(is_subtype_type(t2i, t1i, psi) for t1i, t2i in zip(dom1, dom2))
                and is_subtype_type(cod1, cod2, psi)
            )
        case _:
            return False


def is_subtype_spec(s: Specification, sp: Specification, psi: Psi) -> bool:
    s_dict = {sig.var: sig.type for sig in s.signatures}
    for sig_p in sp.signatures:
        if sig_p.var not in s_dict:
            return False
        if not is_subtype_type(s_dict[sig_p.var], sig_p.type, psi):
            return False
    return True
