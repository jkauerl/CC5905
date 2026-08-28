from typing import Optional

from src.static.functions import (
    _get_specifications_core,
    _inherited_core,
    get_all_parent_specifications,
    join_many,
    join_unique,
    join_unique_many,
    lower_set,
    meet_many,
    meet_unique,
    meet_unique_many,
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
        case TopType(), _:
            return tj
        case _, TopType():
            return ti
        case BottomType(), _:
            return BottomType()
        case _, BottomType():
            return BottomType()
        case Unknown(), _:
            return Unknown()
        case _, Unknown():
            return Unknown()
        # order-sensitive: must stay below the Top/Bottom/Unknown arms
        # (fun meet Top = fun, fun meet ? = ?); these arms only cover
        # function vs class name, which have no common lower bound.
        case GradualFunctionType(), _:
            return BottomType()
        case _, GradualFunctionType():
            return BottomType()
        case Type(), Type():
            return meet_unique(environment, ti, tj)

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
                raise ValueError("Function types must have the same number of arguments")
            args = [meet_unique_consistent(environment, a1, a2) for a1, a2 in zip(fi1, fi2)]
            if any(a is None for a in args):
                return None
            ret = join_unique_consistent(environment, fj1, fj2)
            if ret is None:
                return None
            return GradualFunctionType(args, ret)
        case TopType(), _:
            return TopType()
        case _, TopType():
            return TopType()
        case BottomType(), _:
            return tj
        case _, BottomType():
            return ti
        case Unknown(), _:
            return Unknown()
        case _, Unknown():
            return Unknown()
        # order-sensitive: must stay below the Top/Bottom/Unknown arms
        # (fun join Bottom = fun, fun join ? = ?); these arms only cover
        # function vs class name, whose only common upper bound is Top.
        case GradualFunctionType(), _:
            return TopType()
        case _, GradualFunctionType():
            return TopType()
        case Type(), Type():
            return join_unique(environment, ti, tj)

    return None


def meet_unique_consistent_many(
    environment: Environment, types: list[GradualType]
) -> Optional[GradualType]:
    """The gradual unique meet of a family of types (Rocq ``gunique_meet_set``):
    the abstraction of the static meets of the family's concretizations.

    ⊥ absorbs and ⊤ is neutral.  With a ? among the rest, the result is ⊥ when
    the remaining types are a class name beside a function type, or class names
    with no common lower node, and ? otherwise.  Without ?, class names meet as
    static types, function types by the join of their domains and the meet of
    their codomains, and a name beside a function type gives ⊥.

    :param environment: The Environment object representing the type system.
    :param types: The family of gradual types.
    :return: The unique meet, or None when it is absent or ambiguous.
    """
    ts = list(types)
    if any(isinstance(t, BottomType) for t in ts):
        return BottomType()
    ts = [t for t in ts if not isinstance(t, TopType)]
    if not ts:
        return TopType()
    if any(isinstance(t, Unknown) for t in ts):
        rest = [t for t in ts if not isinstance(t, Unknown)]
        if not rest:
            return Unknown()
        if all(isinstance(t, ClassName) for t in rest):
            if meet_many(environment, rest) == {BottomType()}:
                return BottomType()
            return Unknown()
        if all(isinstance(t, GradualFunctionType) for t in rest):
            return Unknown()
        return BottomType()
    if all(isinstance(t, ClassName) for t in ts):
        return meet_unique_many(environment, ts)
    if all(isinstance(t, GradualFunctionType) for t in ts):
        arity = len(ts[0].domain)
        if any(len(t.domain) != arity for t in ts):
            return BottomType()
        args = [
            join_unique_consistent_many(environment, [t.domain[i] for t in ts])
            for i in range(arity)
        ]
        if any(a is None for a in args):
            return None
        ret = meet_unique_consistent_many(environment, [t.codomain for t in ts])
        if ret is None:
            return None
        return GradualFunctionType(tuple(args), ret)
    return BottomType()


def join_unique_consistent_many(
    environment: Environment, types: list[GradualType]
) -> Optional[GradualType]:
    """The gradual unique join of a family of types (Rocq ``gunique_join_set``),
    dual to ``meet_unique_consistent_many``.

    :param environment: The Environment object representing the type system.
    :param types: The family of gradual types.
    :return: The unique join, or None when it is absent or ambiguous.
    """
    ts = list(types)
    if any(isinstance(t, TopType) for t in ts):
        return TopType()
    ts = [t for t in ts if not isinstance(t, BottomType)]
    if not ts:
        return BottomType()
    if any(isinstance(t, Unknown) for t in ts):
        rest = [t for t in ts if not isinstance(t, Unknown)]
        if not rest:
            return Unknown()
        if all(isinstance(t, ClassName) for t in rest):
            if join_many(environment, rest) == {TopType()}:
                return TopType()
            return Unknown()
        if all(isinstance(t, GradualFunctionType) for t in rest):
            return Unknown()
        return TopType()
    if all(isinstance(t, ClassName) for t in ts):
        return join_unique_many(environment, ts)
    if all(isinstance(t, GradualFunctionType) for t in ts):
        arity = len(ts[0].domain)
        if any(len(t.domain) != arity for t in ts):
            return TopType()
        args = [
            meet_unique_consistent_many(environment, [t.domain[i] for t in ts])
            for i in range(arity)
        ]
        if any(a is None for a in args):
            return None
        ret = join_unique_consistent_many(environment, [t.codomain for t in ts])
        if ret is None:
            return None
        return GradualFunctionType(tuple(args), ret)
    return TopType()


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
    return _inherited_core(
        environment, class_name, proj_many, meet_unique_consistent_many
    )


def get_specifications(
    environment: Environment, class_name: ClassName
) -> Specification:
    """Wrapper function to get specifications for a class name.

    :param environment: The Environment object representing the type system.
    :param class_name: The class name to get specifications for.
    :return: A list of specifications.
    """
    return _get_specifications_core(environment, class_name, inherited)
