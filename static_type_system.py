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


def get_all_parent_specifications(
    psi: Psi, class_name: ClassName
) -> list[Specification]:
    """Get all parent specifications of a given class name.

    :param psi: The Psi object representing the type system.
    :param class_name: The class name to get the parent specifications for.
    :return: A list of parent specifications.
    """
    if class_name not in [n.name for n in psi.Ns]:
        raise ValueError(f"Class {class_name} not found in Psi object.")
    parent_specifications = []
    for edge in psi.Ns:
        if edge.name == class_name.name:
            for parent in psi.Es:
                if parent.target == edge:
                    parent_specifications.append(parent)
    return parent_specifications


def get_minimal_specification(class_name: ClassName, psi: Psi) -> Specification:
    """Get the minimal specification of a given class name.

    :param class_name: The class name to get
    :param psi: The Psi object representing the type system.
    :return: The minimal specification of the class name.
    """
    for parent_spec in get_all_parent_specifications(psi, class_name):
        if parent_spec.signatures:
            return parent_spec
    raise ValueError(f"Minimal specification for {class_name} not found.")


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


"""
Validation of functions and records
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