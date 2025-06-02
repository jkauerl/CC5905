from .definitions import Psi, ClassName, Specification
from .functions import get_all_parent_specifications
from src.static.propositions import (
    acyclic,
    includes_node,
    exists_all_signatures,
    no_overloading,
)
from src.gradual.subtyping import is_subtype_spec

__all__ = [
    "acyclic",
    "includes_node",
    "exists_all_signatures",
    "no_overloading",
]

""" Node validation propositions
"""


def minimal_specification(psi: Psi, class_name: ClassName, s: Specification) -> bool:
    """Check if the given specification is minimal for the given class name.
    
    :param psi: The Psi object representing the type system.
    :param class_name: The class name to check.
    :param s: The specification to check.
    :return: True if the specification is minimal, False otherwise.
    """
    parent_specs = get_all_parent_specifications(psi, class_name)
    for sp in parent_specs:
        if not is_subtype_spec(s, Specification(sp), psi):
            return False
    return True
