from src.gradual.subtyping import is_subtype_spec
from src.static.propositions import (
    _minimal_specification_core,
    acyclic,
    exists_all_signatures,
    includes_node,
    no_overloading,
)

from ..static.types import ClassName
from .definitions import Environment, Specification

__all__ = [
    "acyclic",
    "includes_node",
    "exists_all_signatures",
    "no_overloading",
]

""" Node validation propositions
"""


def minimal_specification(
    environment: Environment, class_name: ClassName, s: Specification
) -> bool:
    """Wrapper function to check if the given specification is minimal for the given
    class name.

    :param environment: The Environment object representing the type system.
    :param class_name: The class name to check.
    :param s: The specification to check.
    :return: True if the specification is minimal, False otherwise.
    """
    return _minimal_specification_core(environment, class_name, s, is_subtype_spec)
