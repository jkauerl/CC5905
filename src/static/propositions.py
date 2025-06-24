from collections import defaultdict
from typing import Callable

from .definitions import (
    ClassName,
    Environment,
    Specification,
    Type,
)
from .functions import get_all_parent_specifications, names
from .subtyping import is_subtype_spec

""" Node validation propositions
"""


def _minimal_specification_core(
    class_name: ClassName,
    s: Specification,
    environment: Environment,
    is_subtype: Callable[[Environment, Type, Type], bool],
) -> bool:
    """Core function to check if the given specification is minimal for the given class name.

    :param class_name: The class name to check.
    :param s: The specification to check.
    :param environment: The Environment object representing the type system.
    :return: True if the specification is minimal, False otherwise.
    """
    parent_specs = get_all_parent_specifications(environment, class_name)
    for sp in parent_specs:
        if not is_subtype(s, Specification(sp), environment):
            return False
    return True


def minimal_specification(class_name: ClassName, s: Specification, environment: Environment) -> bool:
    """Wrapper function to check if the given specification is minimal for the given class name.

    :param environment: The Environment object representing the type system.
    :param class_name: The class name to check.
    :param s: The specification to check.
    :return: True if the specification is minimal, False otherwise.
    """
    return _minimal_specification_core(class_name, s, environment, is_subtype_spec)


def includes_node(class_name: ClassName, s: Specification, environment: Environment) -> bool:
    """Check if all signatures of class_name in environment.sigma are included in s."""
    if class_name.name not in environment.sigma:
        return False

    sigs_n = environment.sigma[class_name.name]
    sigs_s = s.signatures

    s_dict = {sig.var: sig.type for sig in sigs_s}
    for sig in sigs_n:
        if sig.var not in s_dict:
            return False
        if sig.type != s_dict[sig.var]:
            return False
    return True


def exists_all_signatures(environment: Environment, class_name: ClassName, s: Specification) -> bool:
    """
    Check if the specification s includes exactly the signatures that are
    either declared by the class N or inherited from its parents, with no extra methods.

    :param environment: The Environment object representing the type system.
    :param class_name: The class name to check.
    :param s: The specification to check.
    :return: True if all signatures are correct, False otherwise.
    """

    given_signatures = names(s)

    # Gather the method names declared by class N
    own_signatures = {sig.var for sig in environment.sigma[class_name.name]}

    parent_specs_raw = get_all_parent_specifications(environment, class_name)
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


def build_adjacency_list(environment: Environment) -> dict:
    """Funtion to build an adjacency list from the given Environment object.

    :param environment: The Environment object representing the type system.
    :return: A dictionary representing the adjacency list of the graph.
    """
    adj = defaultdict(list)
    for edge in environment.Es:
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


def acyclic(environment: Environment) -> bool:
    """Check if the given Environment object is acyclic.

    :param environment: The Environment object representing the type system.

    :return: True if the object is acyclic, False otherwise.
    """
    visited = set()
    stack = set()
    adj = build_adjacency_list(environment)
    for node in environment.Ns:
        if node not in visited:
            if not dfs(node, visited, stack, adj):
                return False
    return True
