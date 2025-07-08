from src.static.subtyping import _is_subtype_spec_core, is_subtype

from ..static.types import BottomType, ClassName, TopType
from .definitions import (
    Environment,
    Specification,
)
from .types import GradualFunctionType, GradualType, Unknown

""" Propositions to check the type system
"""


def is_gradual_subtype(
    environment: Environment, t1: GradualType, t2: GradualType, visited=None
) -> bool:
    """Check if t1 is a subtype of t2 in the Environment type system.

    :param environment: The Environment object representing the type system.
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
            is_subtype(environment, t2_arg, t1_arg, visited)
            for t1_arg, t2_arg in zip(t1.domain, t2.domain)
        )
        codomain_check = is_subtype(environment, t1.codomain, t2.codomain, visited)
        return domain_check and codomain_check

    if isinstance(t1, ClassName) and isinstance(t2, ClassName):
        return is_subtype(environment, t1, t2)

    return False


def is_subtype_spec(
    environment: Environment,s: Specification, sp: Specification
) -> bool:
    """Wrapper function to check if a specification s is a subtype of another
    specification sp.

    :param s: The first specification to check.
    :param sp: The second specification to check.
    :param environment: The Environment object representing the type system.
    :return: True if s is a subtype of sp, False otherwise.
    """
    return _is_subtype_spec_core(environment, s, sp, is_gradual_subtype)
