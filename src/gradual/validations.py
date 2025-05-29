from .definitions import Psi, ClassName, Specification, Edge, FunctionType
from .propositions import (
    is_minimal_specification,
    is_includes_node,
    exists_all_signatures,
    no_overloading,
    is_valid_signature,
    acyclic,
)

# Validation of a gradual graph

def is_node(psi: Psi, node: ClassName) -> bool:
    """Check if the given node is a valid node in the Psi object."""
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
    
    param psi: The Psi object representing the type system.
    param edge: The edge to check.
    return: True if the edge is valid, False otherwise.
    """
    return any(
        edge.source == class_name_1 and edge.target == class_name_2 for edge in psi.Es
    )


def is_valid_fun(psi: Psi) -> bool:
    """Check if the given function is valid in the Psi object.

    :param psi: The Psi object representing the type system.
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
