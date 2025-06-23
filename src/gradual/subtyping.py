import src.static.subtyping as static_subtyping

from .definitions import (
    BottomType,
    ClassName,
    GradualFunctionType,
    Psi,
    Specification,
    TopType,
    Type,
    Unknown,
)
from src.static.subtyping import _is_subtype_spec_core

""" Propositions to check the type system
"""


def is_subtype(psi: Psi, t1: Type, t2: Type, visited=None) -> bool:
    """Check if t1 is a subtype of t2 in the Psi type system.

    :param psi: The Psi object representing the type system.
    :param t1: The first type to check.
    :param t2: The second type to check.
    :param visited: A set of visited types to avoid cycles.
    :return: True if t1 is a subtype of t2, False otherwise.
    """
    if visited is None:
        visited = set()

    if (t1, t2) in visited:
        return False
    visited.add((t1, t2))

    if t1 == t2:
        return True

    if isinstance(t2, TopType):
        return True

    if isinstance(t1, BottomType):
        return True

    if isinstance(t2, Unknown):
        return True

    if isinstance(t1, Unknown):
        return True

    # If t1 is a class name, check if t2 is a class name
    if isinstance(t1, GradualFunctionType) and isinstance(t2, GradualFunctionType):
        if len(t1.domain) != len(t2.domain):
            return False
        domain_check = all(
            is_subtype(psi, t2_arg, t1_arg, visited)
            for t1_arg, t2_arg in zip(t1.domain, t2.domain)
        )
        codomain_check = is_subtype(psi, t1.codomain, t2.codomain, visited)
        return domain_check and codomain_check

    if isinstance(t1, ClassName) and isinstance(t2, ClassName):
        return static_subtyping.is_subtype(psi, t1, t2)

    return False


def is_subtype_spec(s: Specification, sp: Specification, psi: Psi) -> bool:
    """Check if specification s is a subtype of specification sp.

    :param s: The first specification to check.
    :param sp: The second specification to check.
    :param psi: The Psi object representing the type system.
    :return: True if s is a subtype of sp, False otherwise.
    """
    return _is_subtype_spec_core(s, sp, psi, is_subtype)