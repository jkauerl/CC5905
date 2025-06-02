from .definitions import ClassName, FunctionType, Psi, Signature, Specification, Type
from .propositions import (
    exists_all_signatures,
    includes_node,
    minimal_specification,
    no_overloading,
    acyclic,
)

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
            return is_valid_function(psi, type)
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
    """Check if the given node is valid in the Psi object.

    param psi: The Psi object representing the type system.
    param edge: The edge to check.
    return: True if the edge is valid, False otherwise.
    """
    sigs = psi.sigma.get(node.name, [])
    spec = Specification(sigs)
    return (
        minimal_specification(node, spec, psi)
        and includes_node(node, spec, psi)
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
        if not minimal_specification(class_name, spec, psi):
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
