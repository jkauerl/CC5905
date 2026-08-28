from typing import Set

from ..static.subtyping import subtype_names, supertype_names
from .definitions import Environment

""" Parents, children, ancestors and descendants of a node.

    parents(N)     = { P in nodes | N <:1 P }      children(N)    = { C in nodes | C <:1 N }
    Anc(N)         = { A in nodes | N <: A }       Desc(N)        = { C in nodes | C <: N }

Parents and children read the edges; ancestors and descendants read name
subtyping, so both contain N itself.  All four are sets of node names.
"""


def node_names(environment: Environment) -> Set[str]:
    """The names of the nodes, cached on the environment.

    :param environment: The Environment object representing the type system.
    :return: The set of node names.
    """
    cache = getattr(environment, "_node_names", None)
    if cache is None:
        cache = {node.name for node in environment.Ns}
        environment._node_names = cache
    return cache


def parents(environment: Environment, name: str) -> Set[str]:
    """parents(N): the nodes P with N <:1 P.

    :param environment: The Environment object representing the type system.
    :param name: The node N.
    :return: The set of direct supertypes of N.
    """
    return {edge.target.name for edge in environment.Es if edge.source.name == name}


def children(environment: Environment, name: str) -> Set[str]:
    """children(N): the nodes C with C <:1 N.

    :param environment: The Environment object representing the type system.
    :param name: The node N.
    :return: The set of direct subtypes of N.
    """
    return {edge.source.name for edge in environment.Es if edge.target.name == name}


def ancestors(environment: Environment, name: str) -> Set[str]:
    """Anc(N): the nodes A with N <: A.

    :param environment: The Environment object representing the type system.
    :param name: The node N.
    :return: The set of supertypes of N among the nodes, N included.
    """
    return node_names(environment) & supertype_names(environment, name)


def descendants(environment: Environment, name: str) -> Set[str]:
    """Desc(N): the nodes C with C <: N.

    :param environment: The Environment object representing the type system.
    :param name: The node N.
    :return: The set of subtypes of N among the nodes, N included.
    """
    return node_names(environment) & subtype_names(environment, name)
