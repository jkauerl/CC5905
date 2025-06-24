from src.static.functions import (
    get_all_parent_specifications,
    join_unique,
    lower_set,
    meet_unique,
    names,
    undeclared,
    upper_set,
)
from src.static.definitions import (
    Type,
)

from .definitions import (
    BottomType,
    ClassName,
    GradualFunctionType,
    Environment,
    Signature,
    Specification,
    TopType,
    GradualType,
    Unknown,
)

__all__ = [
    "join_unique",
    "lower_set",
    "meet_unique",
    "names",
    "upper_set",
    "get_all_parent_specifications",
    "undeclared",
]


def meet_unique_consistent(environment: Environment, ti: GradualType, tj: GradualType) -> GradualType | None:
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
            args = [join_unique_consistent(environment, a1, a2) for a1, a2 in zip(fi1, fi2)]
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


def join_unique_consistent(environment: Environment, ti: GradualType, tj: GradualType) -> GradualType | None:
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
            args = [meet_unique_consistent(environment, a1, a2) for a1, a2 in zip(fi1, fi2)]
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


def proj(x: str, s: Specification) -> GradualType | None:
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


def inherited(environment: Environment, class_name: ClassName) -> dict[str, Type]:
    """Return the mapping of inherited variable names to their inferred types
    in the specification of a class name.

    Only includes variables inherited but not declared in the class.

    :param environment: The Environment object representing the type system.
    :param class_name: The class name to check.
    :return: A dictionary mapping variable names to their inferred types.
    """
    undeclared_names = undeclared(environment, class_name)
    parent_specs = get_all_parent_specifications(environment, class_name)

    inherited_vars = {}

    for var in undeclared_names:
        projected_types = proj_many(var, parent_specs)

        if not projected_types:
            continue

        current_meet = projected_types[0]

        for other_type in projected_types[1:]:
            if isinstance(current_meet, ClassName) and isinstance(
                other_type, ClassName
            ):
                m = meet_unique_consistent(environment, current_meet, other_type)
                if m is None:
                    current_meet = None
                    break
                current_meet = m
            else:
                current_meet = None
                break

        if current_meet is not None:
            inherited_vars[var] = current_meet

    return inherited_vars


def get_specifications(environment: Environment, class_name: ClassName) -> Specification:
    """Return the full specification of a class name, including inherited variables.

    :param environment: The Environment object representing the type system.
    :param class_name: The class name to get the specification for.
    :return: The combined Specification of the class name.
    """
    explicit_spec = environment.sigma.get(class_name.name)
    if explicit_spec is None:
        explicit_signatures = []
    else:
        explicit_signatures = explicit_spec.signatures

    inherited_vars = inherited(environment, class_name)

    inherited_signatures = [
        Signature(var=var, type=typ) for var, typ in inherited_vars.items()
    ]

    combined_signatures_dict = {sig.var: sig for sig in explicit_signatures}
    for sig in inherited_signatures:
        if sig.var not in combined_signatures_dict:
            combined_signatures_dict[sig.var] = sig

    combined_signatures = list(combined_signatures_dict.values())

    return Specification(signatures=combined_signatures)
