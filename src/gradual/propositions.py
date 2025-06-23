from src.gradual.subtyping import is_subtype_spec
from src.static.propositions import (
    acyclic,
    exists_all_signatures,
    includes_node,
    no_overloading,
    _minimal_specification_core,
)

from .definitions import ClassName, Psi, Specification

__all__ = [
    "acyclic",
    "includes_node",
    "exists_all_signatures",
    "no_overloading",
]

""" Node validation propositions
"""


def minimal_specification(class_name: ClassName, s: Specification, psi: Psi) -> bool:
    """Check if the given specification is minimal for the given class name.

    :param psi: The Psi object representing the type system.
    :param class_name: The class name to check.
    :param s: The specification to check.
    :return: True if the specification is minimal, False otherwise.
    """
    return _minimal_specification_core(class_name, s, psi, is_subtype_spec)
