from ..static.types import BottomType, ClassName, TopType
from .definitions import (
    Environment,
    Specification,
)
from .propositions import (
    acyclic,
    exists_all_signatures,
    includes_node,
    minimal_specification,
    no_overloading,
)
from .types import GradualFunctionType, GradualType, Unknown
from .functions import get_specifications
from src.static.validations import (
    _is_valid_node_core,
    _is_valid_fun_core,
    _is_valid_graph_core,
    is_valid_edge,
    is_valid_fun,
    is_valid_graph,
)

__all__ = [
    "is_valid_edge",
    "is_valid_fun",
    "is_valid_graph",
]

""" Validation of types
"""


def is_valid_type(environment: Environment, type: GradualType) -> bool:
    """Check if the given type is valid in the Environment object.

    :param environment: The Environment object representing the type system.
    :param type: The type to check.
    :return: True if the type is valid, False otherwise.
    """
    match type:
        case GradualFunctionType(_, _):
            return is_valid_function(environment, type)
        case ClassName(name):
            return name in [n.name for n in environment.Ns]
        case TopType():
            return True
        case BottomType():
            return True
        case Unknown():
            return True


""" Validation of functions and signatures
"""


def is_valid_signature(environment: Environment, specification: Specification) -> bool:
    """Check if the given signature is valid in the Environment object.
    This is a list of signatures.

    :param environment: The Environment object representing the type system.
    :param signature: The signature to check.
    :return: True if the signature is valid, False otherwise.
    """
    return all(
        [
            is_valid_type(environment, signature.type)
            for signature in specification.signatures
        ]
    )


def is_valid_function(environment: Environment, function: GradualFunctionType) -> bool:
    """Check if the given function is valid in the Environment object.

    :param environment: The Environment object representing the type system.
    :param function: The function to check.
    :return: True if the function is valid, False otherwise.
    """
    return all(
        [is_valid_type(environment, t) for t in function.domain]
    ) and is_valid_type(environment, function.codomain)


""" Validation of the graph
"""


def is_valid_node(environment: Environment, node: ClassName) -> bool:
    """Check if the given node is valid in the Environment object.

    param environment: The Environment object representing the type system.
    param edge: The edge to check.
    return: True if the edge is valid, False otherwise.
    """
    return _is_valid_node_core(
        environment,
        node,
        get_specifications(environment, node),
        minimal_specification,
        includes_node,
        exists_all_signatures,
        no_overloading,
    )


def is_valid_fun(
    environment: Environment
) -> bool:
    """Check if the given function is valid in the Environment object.

    :param environment: The Environment object representing the type system.
    :param function: The function to check.
    :return: True if the function is valid, False otherwise.
    """
    return _is_valid_fun_core(
        environment,
        is_valid_signature,
    )


def is_valid_graph(environment: Environment) -> bool:
    """Check if the given graph is valid in the Environment object.

    :param environment: The Environment object representing the type system.
    :return: True if the graph is valid, False otherwise.
    """
    return _is_valid_graph_core(
        environment,
        is_valid_node,
        is_valid_fun,
    )
