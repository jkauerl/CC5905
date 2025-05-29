from .definitions import Psi, ClassName, Specification, Edge, FunctionType
from .functions import (
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
