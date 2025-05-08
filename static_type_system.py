from abc import ABC
from collections import defaultdict


class Type(ABC):
    """Abstract base class for all types.

    :param ABC: Abstract Base Class
    """

    pass


class FunctionType(Type):
    """Represents a function type.

    :param Type: The type of the function.
    """

    def __init__(self, domain: list[Type], codomain: Type):
        self.domain = domain
        self.codomain = codomain


class ClassName(Type):
    """Represents a class name. Which in part represents a node in the type system.

    :param Type: The type of the class.
    """

    def __init__(self, name: str):
        self.name = name


class Edge:
    """Represents a directed edge in the type system."""

    def __init__(self, source: ClassName, target: ClassName):
        self.source = source
        self.target = target


class Signature:
    """Represents a signature in the type system."""

    def __init__(self, var: str, type: Type):
        self.var = var
        self.type = type


class Psi:
    """Represents the class (node) relationship in the type system."""

    def __init__(
        self, Ns: list[ClassName], Es: list[Edge], sigma: map[str, list[Signature]]
    ):
        self.Ns = Ns
        self.Es = Es
        self.sigma = sigma  # This represents a function


class Specification:
    """Represents the specification of a class in the type system."""
    def __init__(self, signatures: list[Signature]):
        self.signatures = signatures


def is_direct_subtype(psi: Psi, class_name_1: ClassName, class_name_2: ClassName) -> bool:
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


def is_subtype(psi: Psi, class_name_1: ClassName, class_name_2: ClassName) -> bool:
    """Check if class_name_1 is a subtype of class_name_2.

    :param psi: The Psi object representing the type system.
    :param class_name_1: The first class name to check.
    :param class_name_2: The second class name to check.
    :return: True if class_name_1 is a subtype of class_name_2, False otherwise.
    """
    if class_name_1 == class_name_2:
        return True
    for edge in psi.Es:
        if edge.source == class_name_1 and edge.target == class_name_2:
            return True
        elif edge.source == class_name_1:
            return is_subtype(psi, edge.target, class_name_2)
    return False


def is_subtype_type(t1: Type, t2: Type, psi: Psi) -> bool:
    match (t1, t2):
        case (ClassName(n1), ClassName(n2)):
            return is_subtype(psi, ClassName(n1), ClassName(n2))
        case (FunctionType(dom1, cod1), FunctionType(dom2, cod2)):
            return (
                len(dom1) == len(dom2) and
                all(is_subtype_type(t2i, t1i, psi) for t1i, t2i in zip(dom1, dom2)) and
                is_subtype_type(cod1, cod2, psi)
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


def get_all_parent_specifications(
    psi: Psi, class_name: ClassName
) -> list[Specification]:
    """Get all parent specifications of a given class name. By checking that the class name is a direct subtype of the parent class.

    :param psi: The Psi object representing the type system.
    :param class_name: The class name to get the parent specifications for.
    :return: A list of parent specifications.
    """
    if class_name.name not in [n.name for n in psi.Ns]:
        raise ValueError(f"Class name {class_name.name} not found in Psi object.")

    parent_specifications = []
    for edge in psi.Es:
        if is_direct_subtype(psi, class_name, edge.target):
            parent_specifications.append(psi.sigma[edge.target.name])
    return parent_specifications
    

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


""" Validation of functions and records
"""

def is_valid_record(psi: Psi, record: list[Signature]) -> bool:
    """Check if the given record is valid in the Psi object. This is a list of signatures.

    :param psi: The Psi object representing the type system.
    :param record: The record to check.
    :return: True if the record is valid, False otherwise.
    """
    return all([is_valid_type(psi, signature.type) for signature in record])


def is_valid_function(psi: Psi, function: FunctionType) -> bool:
    """Check if the given function is valid in the Psi object.

    :param psi: The Psi object representing the type system.
    :param function: The function to check.
    :return: True if the function is valid, False otherwise.
    """
    return all([is_valid_type(psi, t) for t in function.domain]) and is_valid_type(psi, function.codomain)