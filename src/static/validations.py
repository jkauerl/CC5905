from .definitions import (
    Environment,
    Specification,
)
from .functions import get_specifications
from .propositions import (
    acyclic,
    exists_all_signatures,
    includes_node,
    minimal_specification,
    no_overloading,
)
from .types import BottomType, ClassName, FunctionType, TopType, Type

""" Validation of types
"""


def is_valid_type(environment: Environment, type: Type) -> bool:
    """Check if the given type is valid in the Environment object.

    :param environment: The Environment object representing the type system.
    :param type: The type to check.
    :return: True if the type is valid, False otherwise.
    """
    match type:
        case FunctionType(_, _):
            return is_valid_function(environment, type)
        case ClassName(name):
            return name in [n.name for n in environment.Ns]
        case TopType():
            return True
        case BottomType():
            return True


""" Validation of functions and signatures
"""


def is_valid_signature(environment: Environment, specification: Specification) -> bool:
    """Check if the given signature is valid in the Environment object.

    :param environment: The Environment object representing the type system.
    :param signature: The signature to check.
    :return: True if the signature is valid, False otherwise.
    """
    return all(is_valid_type(environment, sig.type) for sig in specification.signatures)


def is_valid_function(environment: Environment, function: FunctionType) -> bool:
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


def _is_valid_node_core(
    environment: Environment,
    node: ClassName,
    spec: Specification,
    minimal_specification_fun,
    includes_node_fun,
    exists_all_signatures_fun,
    no_overloading_fun,
) -> bool:
    """Core function to check if the given node is valid in the Environment object.

    :param environment: The Environment object representing the type system.
    :param node: The node to check.
    :param spec: The specification of the node.
    :param minimal_specification_fun: Function to check minimal specification.
    :param includes_node_fun: Function to check if the node is included.
    :param exists_all_signatures_fun: Function to check if all signatures exist.
    :param no_overloading_fun: Function to check if there is no overloading.
    :return: True if the node is valid, False otherwise.
    """
    return (
        minimal_specification_fun(environment, node, spec)
        and includes_node_fun(environment, node, spec)
        and exists_all_signatures_fun(environment, node, spec)
        and no_overloading_fun(spec)
    )


def is_valid_node(environment: Environment, node: ClassName) -> bool:
    """Wrapper function to check if the given node is valid in the Environment object.

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


def is_valid_edge(
    environment: Environment, class_name_1: ClassName, class_name_2: ClassName
) -> bool:
    """Check if the given edge is valid in the Environment object.

    :param environment: The Environment object representing the type system.
    :param class_name_1: The first class name to check.
    :param class_name_2: The
    second class name to check.
    :return: True if the edge is valid, False otherwise.
    """
    return any(
        edge.source == class_name_1 and edge.target == class_name_2
        for edge in environment.Es
    )


def _is_valid_fun_core(
    environment: Environment,
    is_valid_signature_fun,
) -> bool:
    """Core function to check if the given function is valid in the Environment object.

    :param environment: The Environment object representing the type system.
    :param is_valid_signature_fun: Function to check if a signature is valid.
    :return: True if the function is valid, False otherwise.
    """
    for class_name in environment.Ns:
        if class_name.name not in environment.sigma:
            return False
        signature = environment.sigma[class_name.name]
        if not is_valid_signature_fun(environment, signature):
            return False
    return True


def is_valid_fun(environment: Environment) -> bool:
    """Wrapper function to check if the given function is valid in the Environment
        object.

    :param environment: The Environment object representing the type system.
    :param sigma: The function to check.
    :return: True if the function is valid, False otherwise.
    """
    return _is_valid_fun_core(
        environment,
        is_valid_signature,
    )


def _is_valid_graph_core(
    environment: Environment,
    is_valid_node_fun,
    is_valid_fun_fun,
) -> bool:
    """Core function to check if the given graph is valid in the Environment object.

    :param environment: The Environment object representing the type system.
    :param is_valid_node_fun: Function to check if a node is valid.
    :return: True if the graph is valid, False otherwise.
    """
    if not is_valid_fun_fun(environment):
        return False
    for class_name in environment.Ns:
        if class_name.name not in environment.sigma:
            return False
        if not is_valid_node_fun(environment, class_name):
            return False
    for edge in environment.Es:
        if not is_valid_edge(environment, edge.source, edge.target):
            return False
    if not acyclic(environment):
        return False
    return True


def is_valid_graph(environment: Environment) -> bool:
    """Wrapper function to check if the given graph is valid in the Environment object.

    :param environment: The Environment object representing the type system.
    :return: True if the graph is valid, False otherwise.
    """
    return _is_valid_graph_core(
        environment,
        is_valid_node,
        is_valid_fun,
    )
