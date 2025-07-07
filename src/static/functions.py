from typing import Callable, Set

from .definitions import Environment, Signature, Specification
from .types import Type, TopType, BottomType, ClassName
from .subtyping import is_direct_subtype, is_subtype

""" Function to get parent specifications
"""


def get_all_parent_specifications(
    environment: Environment, class_name: ClassName
) -> Set[Specification]:
    """Get all parent specifications of a given class name.
    By checking that the class name is a direct subtype of the parent class.

    :param environment: The Environment object representing the type system.
    :param class_name: The class name to get the parent specifications for.
    :return: A list of parent specifications.
    """
    if class_name.name not in [n.name for n in environment.Ns]:
        return set()

    parent_specifications = set()
    for edge in environment.Es:
        if edge.source == class_name and is_direct_subtype(environment, edge.source, edge.target):
            parent_specifications.add(environment.sigma[edge.target.name])
    return parent_specifications


""" Functions of the type system
"""


def lower_set(environment: Environment, ti: Type) -> set[Type]:
    """Return the set of all Type T such that T <: ti.

    :param environment: The Environment object representing the type system.
    :param ti: The target class name.
    :return: A set of Types that are subtypes of ti.
    """
    result = {ti}
    for t in environment.Ns:
        if is_subtype(environment, t, ti) and t != ti:
            result.add(t)
    if is_subtype(environment, BottomType(), ti):
        result.add(BottomType())
    return result


def upper_set(environment: Environment, ti: Type) -> set[Type]:
    """Return the set of all Type T such that ti <: T.

    :param environment: The Environment object representing the type system.
    :param ti: The target class name.
    :return: A set of Types that are supertypes of ti.
    """
    return {T for T in environment.Ns if is_subtype(environment, ti, T)}


def meet(environment: Environment, ti: Type, tj: Type) -> set[Type]:
    """Return the meet (greatest lower bound) of two class names in the type system.

    :param environment: The Environment object representing the type system.
    :param ti: The first class name.
    :param tj: The second class name.
    :return: A set of Type representing the meet.
    """
    if ti == tj:
        return {ti}

    lower_ti = lower_set(environment, ti)
    lower_tj = lower_set(environment, tj)

    common = lower_ti.intersection(lower_tj)

    meet_set = set()
    for t in common:
        if all(not is_subtype(environment, t, t_prime) for t_prime in common if t_prime != t):
            meet_set.add(t)

    return meet_set


def meet_unique(environment: Environment, ti: Type, tj: Type) -> Type | None:
    """Return the unique meet of two class names in the type system.

    :param environment: The Environment object representing the type system.
    :param ti: The first class name.
    :param tj: The second class name.
    :return: The unique meet of the two class names.
    """
    meet_set = meet(environment, ti, tj)
    if len(meet_set) == 1:
        return next(iter(meet_set))
    else:
        return None


def join(environment: Environment, ti: Type, tj: Type) -> set[Type]:
    """Return the join (least upper bound) of two class names in the type system.

    The join is the set of minimal elements in the intersection of the higher sets
    of `ti` and `tj`.

    :param environment: The Environment object representing the type system.
    :param ti: The first class name.
    :param tj: The second class name.
    :return: A set of Type representing the join.
    """
    common = upper_set(environment, ti).intersection(upper_set(environment, tj))

    join_set = set()
    for t in common:
        if all(
            not is_subtype(environment, t_prime, t)
            for t_prime in common
            if t != t_prime
        ):
            join_set.add(t)

    return join_set


def join_unique(environment: Environment, ti: Type, tj: Type) -> Type | None:
    """Return the unique join of two class names in the type system.

    :param environment: The Environment object representing the type system.
    :param ti: The first class name.
    :param tj: The second class name.
    :return: The unique join of the two class names.
    """
    join_set = join(environment, ti, tj)
    if len(join_set) == 1:
        return next(iter(join_set))
    else:
        return None


def proj(x: str, s: Specification) -> Type | None:
    """Returns the type of the variable x in the specification s.

    :param x: The variable name to look up.
    :param s: The specification to project.
    :return: The type associated with x in s, or None if not found.
    """
    for sig in s.signatures:
        if sig.var == x:
            return sig.type
    return None


def names(s: Specification) -> set[str]:
    """Get the names of the signatures in the specification.

    :param s: The specification to get the names from.
    :return: A list of names.
    """
    return {sig.var for sig in s.signatures}


def proj_many(var: str, ss: list[Specification]) -> list[Type]:
    """Project the list of specifications ss onto the class name t.

    :param environment: The Environment object representing the type system.
    :param t: The class name to project onto.
    :param ss: The list of specifications to project.
    :return: A list of projected types.
    """
    result = []
    for s in ss:
        t = proj(var, s)
        if t is not None:
            result.append(t)
    return result


def undeclared(environment: Environment, class_name: ClassName) -> set[str]:
    """Return the set of undeclared variable names in the specification of a class name.

    These are names inherited from parents but not declared explicitly in the class.

    :param environment: The Environment object representing the type system.
    :param class_name: The class name to check.
    :return: A set of undeclared variable names.
    """
    sigma_spec = environment.sigma.get(class_name.name)
    if sigma_spec is None:
        return set()

    declared_names = set(names(sigma_spec))

    parent_specs = get_all_parent_specifications(environment, class_name)

    inherited_names = set()
    for spec in parent_specs:
        inherited_names.update(names(spec))

    undeclared_names = inherited_names - declared_names

    return undeclared_names


def _inherited_core(
    environment: Environment,
    class_name: ClassName,
    proj_many_function: Callable[[str, Specification], Type | None],
    meet_unique_function: Callable[[Environment, Type, Type], Type | None],
) -> Set[Signature]:
    """Core function to get the inherited variable names and their types.

    Only includes variables inherited but not declared in the class.

    :param environment: The Environment object representing the type system.
    :param class_name: The class name to check.
    :return: A dictionary mapping variable names to their inferred types.
    """
    undeclared_names = undeclared(environment, class_name)
    parent_specs = get_all_parent_specifications(environment, class_name)

    inherited_vars = set()

    for var in undeclared_names:
        projected_types = proj_many_function(var, parent_specs)

        if not projected_types:
            continue

        current_meet = projected_types[0]

        for other_type in projected_types[1:]:
            m = meet_unique_function(environment, current_meet, other_type)
            if m is None:
                current_meet = None
                break
            current_meet = m

        if current_meet is not None:
            inherited_vars.add(Signature(var=var, type=current_meet))

    return inherited_vars


def inherited(environment: Environment, class_name: ClassName) -> Set[Signature]:
    """Wrapper function to get the inherited variable names and their types.

    :param environment: The Environment object representing the type system.
    :param class_name: The class name to check.
    :return: A dictionary mapping variable names to their inferred types.
    """
    return _inherited_core(
        environment,
        class_name,
        proj_many,
        meet_unique,
    )


def _get_specifications_core(
    environment: Environment,
    class_name: ClassName,
    inherited_function: Callable[[Environment, ClassName], Signature],
) -> Specification:
    """Core function to get the full specification of a class name, including inherited
    variables.

    :param environment: The Environment object representing the type system.
    :param class_name: The class name to get the specification for.
    :return: The combined Specification of the class name.
    """
    explicit_spec = environment.sigma.get(class_name.name)
    if explicit_spec is None:
        explicit_signatures = []
    else:
        explicit_signatures = explicit_spec.signatures

    inherited_signatures = inherited_function(environment, class_name)

    combined_signatures_dict = {sig.var: sig for sig in explicit_signatures}

    for sig in inherited_signatures:
        if sig.var not in combined_signatures_dict:
            combined_signatures_dict[sig.var] = sig

    combined_signatures = list(combined_signatures_dict.values())

    return Specification(signatures=combined_signatures)


def get_specifications(
    environment: Environment, class_name: ClassName
) -> Specification:
    """Wrapper function to return the full specification of a class name, including
    inherited variables.

    :param environment: The Environment object representing the type system.
    :param class_name: The class name to get the specification for.
    :return: The combined Specification of the class name.
    """
    return _get_specifications_core(
        environment,
        class_name,
        inherited,
    )
