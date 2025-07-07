from typing import Optional

from src.static.functions import (
    _get_specifications_core,
    _inherited_core,
    get_all_parent_specifications,
    join_unique,
    lower_set,
    meet_unique,
    names,
    undeclared,
    upper_set,
)

from ..static.types import BottomType, ClassName, TopType, Type
from .definitions import (
    Environment,
    Signature,
    Specification,
)
from .types import GradualFunctionType, GradualType, Unknown

__all__ = [
    "join_unique",
    "lower_set",
    "meet_unique",
    "names",
    "upper_set",
    "get_all_parent_specifications",
    "undeclared",
]


def meet_unique_consistent(
    environment: Environment, ti: GradualType, tj: GradualType
) -> Optional[GradualType]:
    """Calculate the meet of two types, ensuring consistency in the type system.

    :param environment: The Environment object representing the type system.
    :param ti: The first type to meet.
    :param tj: The second type to meet.
    :return: The meet of the two types if consistent, otherwise None.
    """
    match ti, tj:
        case GradualFunctionType(fi1, fj1), GradualFunctionType(fi2, fj2):
            if len(fi1) != len(fi2):
                raise ValueError(
                    "Function types must have the same number of arguments"
                )
            args = [
                join_unique_consistent(environment, a1, a2) for a1, a2 in zip(fi1, fi2)
            ]
            if any(a is None for a in args):
                return None
            ret = meet_unique_consistent(environment, fj1, fj2)
            if ret is None:
                return None
            return GradualFunctionType(args, ret)
        case Type(), Type():
            return meet_unique(environment, ti, tj)
        case BottomType(), _:
            return BottomType()
        case _, BottomType():
            return BottomType()
        case TopType(), _:
            return tj
        case _, TopType():
            return ti
        case Unknown(), _:
            return Unknown()
        case _, Unknown():
            return Unknown()

    return None


def join_unique_consistent(
    environment: Environment, ti: GradualType, tj: GradualType
) -> Optional[GradualType]:
    """Calculate the join of two types, ensuring consistency in the type system.

    :param environment: The Environment object representing the type system.
    :param ti: The first type to join.
    :param tj: The second type to join.
    :return: The join of the two types if consistent, otherwise None.
    """
    match ti, tj:
        case GradualFunctionType(fi1, fj1), GradualFunctionType(fi2, fj2):
            if len(fi1) != len(fi2):
                raise ValueError(
                    "Function types must have the same number of arguments"
                )
            args = [
                meet_unique_consistent(environment, a1, a2) for a1, a2 in zip(fi1, fi2)
            ]
            if any(a is None for a in args):
                return None
            ret = join_unique_consistent(environment, fj1, fj2)
            if ret is None:
                return None
            return GradualFunctionType(args, ret)
        case Type(), Type():
            return meet_unique(environment, ti, tj)
        case BottomType(), _:
            return BottomType()
        case _, BottomType():
            return BottomType()
        case TopType(), _:
            return tj
        case _, TopType():
            return ti
        case Unknown(), _:
            return Unknown()
        case _, Unknown():
            return Unknown()

    return None


def proj(x: str, s: Specification) -> Optional[GradualType]:
    """Project a variable name from a specification to its type.

    :param x: The variable name to project.
    :param s: The specification containing the signatures.
    :return: The type of the variable if found, otherwise None.
    """
    for sig in s.signatures:
        if sig.var == x:
            return sig.type
    return None


def proj_many(var: str, ss: list[Specification]) -> list[GradualType]:
    """Project a variable name from multiple specifications to their types.

    :param var: The variable name to project.
    :param ss: A list of specifications to project onto.
    :return: A list of types associated with the variable in the specifications.
    """
    result = []
    for s in ss:
        t = proj(var, s)
        if t is not None:
            result.append(t)
    return result


def inherited(environment: Environment, class_name: ClassName) -> Signature:
    """Wrapper function to get inherited specifications for a class name.

    :param environment: The Environment object representing the type system.
    :param class_name: The class name to get inherited specifications for.
    :return: A list of inherited specifications.
    """
    return _inherited_core(environment, class_name, proj_many, meet_unique_consistent)


def get_specifications(
    environment: Environment, class_name: ClassName
) -> Specification:
    """Wrapper function to get specifications for a class name.

    :param environment: The Environment object representing the type system.
    :param class_name: The class name to get specifications for.
    :return: A list of specifications.
    """
    return _get_specifications_core(environment, class_name, inherited)
