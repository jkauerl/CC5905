from abc import ABC
from collections import defaultdict


""" Static type system for a programming language.
"""

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


""" Functions of the type system
"""

def names(s: Specification) -> set[str]:
    """Get the names of the signatures in the specification.

    :param s: The specification to get the names from.
    :return: A list of names.
    """
    return {sig.var for sig in s.signatures}


def lower_set(psi: Psi, ti: ClassName) -> set[ClassName]:
    """Return the set of all ClassName T such that T <: ti.
    
    :param psi: The Psi object representing the type system.
    :param ti: The target class name.
    :return: A set of ClassNames that are subtypes of ti.
    """
    return {T for T in psi.Ns if is_subtype(psi, T, ti)}


def upper_set(psi: Psi, ti: ClassName) -> set[ClassName]:
    """Return the set of all ClassName T such that ti <: T.
    
    :param psi: The Psi object representing the type system.
    :param ti: The target class name.
    :return: A set of ClassNames that are supertypes of ti.
    """
    return {T for T in psi.Ns if is_subtype(psi, ti, T)}


def meet(psi: Psi, ti: ClassName, tj: ClassName) -> set[ClassName]:
    """Return the meet (greatest lower bound) of two class names in the type system.

    :param psi: The Psi object representing the type system.
    :param ti: The first class name.
    :param tj: The second class name.
    :return: A set of ClassName representing the meet.
    """
    common = lower_set(psi, ti).intersection(lower_set(psi, tj))

    meet_set = set()
    for T in common:
        if all(not is_subtype(psi, T, T_prime) for T_prime in common if T != T_prime):
            meet_set.add(T)

    return meet_set


def meet_unique(psi: Psi, ti: ClassName, tj: ClassName) -> ClassName | None:
    """Return the unique meet of two class names in the type system.
    
    :param psi: The Psi object representing the type system.
    :param ti: The first class name.
    :param tj: The second class name.
    :return: The unique meet of the two class names.
    """
    meet_set = meet(psi, ti, tj)
    if len(meet_set) == 1:
        return next(iter(meet_set))
    else:
        return None


def join(psi: Psi, ti: ClassName, tj: ClassName) -> set[ClassName]:
    """Return the join (least upper bound) of two class names in the type system.

    The join is the set of minimal elements in the intersection of the higher sets
    of `ti` and `tj`.

    :param psi: The Psi object representing the type system.
    :param ti: The first class name.
    :param tj: The second class name.
    :return: A set of ClassName representing the join.
    """
    common = upper_set(psi, ti).intersection(upper_set(psi, tj))

    join_set = set()
    for T in common:
        if all(not is_subtype(psi, T_prime, T) for T_prime in common if T != T_prime):
            join_set.add(T)

    return join_set


def join_unique(psi: Psi, ti: ClassName, tj: ClassName) -> ClassName | None:
    """Return the unique join of two class names in the type system.

    :param psi: The Psi object representing the type system.
    :param ti: The first class name.
    :param tj: The second class name.
    :return: The unique join of the two class names.
    """
    join_set = join(psi, ti, tj)
    if len(join_set) == 1:
        return next(iter(join_set))
    else:
        return None


""" Propositions to check the type system
"""

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


def is_includes_node(class_name: ClassName, s: Specification) -> bool:
    """Check if the given specification includes the given class name.

    :param class_name: The class name to check.
    :param s: The specification to check.
    :return: True if the specification includes the class name, False otherwise.
    """
    for sig in s.signatures:
        if sig.var == class_name.name:
            return True
    return False


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
    
    parent_specs = get_all_parent_specifications(psi, class_name)
    inherited_signatures = {sig.var for parent in parent_specs for sig in parent.signatures}
    
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
    """Check if the given signature is valid in the Psi object. This is a list of signatures.

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
    return all([is_valid_type(psi, t) for t in function.domain]) and is_valid_type(psi, function.codomain)


""" Validation of the graph
"""

def is_valid_node(psi: Psi, node: ClassName) -> bool:
    """Check if the given node is valid in the Psi object.

    :param psi: The Psi object representing the type system.
    :param node: The node to check.
    :return: True if the node is valid, False otherwise.
    """
    if is_minimal_specification(node, psi.sigma[node.name], psi):
        if is_includes_node(node, psi.sigma[node.name]):
            if exists_all_signatures(psi, node, psi.sigma[node.name]):
                if no_overloading(psi.sigma[node.name]):
                    return True
                

def is_valid_edge(psi: Psi, class_name_1: ClassName, class_name_2: ClassName) -> bool:
    """Check if the given edge is valid in the Psi object.

    :param psi: The Psi object representing the type system.
    :param class_name_1: The first class name to check.
    :param class_name_2: The
    second class name to check.
    :return: True if the edge is valid, False otherwise.
    """
    return any(
        edge.source == class_name_1 and edge.target == class_name_2
        for edge in psi.Es
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
            if not exists_all_signatures(class_name, spec, psi):
                return False
            if not is_valid_signature(psi, spec.signatures):
                return False
    for edge in psi.Es:
        if not is_valid_edge(psi, edge.source, edge.target):
            return False
    if not acyclic(psi):
        return False
    return True