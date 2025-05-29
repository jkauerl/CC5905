from .definitions import ClassName, Psi, Specification, Type
from .subtyping import is_subtype

""" Functions of the type system
"""


def lower_set(psi: Psi, ti: ClassName) -> set[ClassName]:
    """Return the set of all ClassName T such that T <: ti.

    :param psi: The Psi object representing the type system.
    :param ti: The target class name.
    :return: A set of ClassNames that are subtypes of ti.
    """
    return {T for T in psi.Ns if is_subtype(psi, T, ti)}


def upper_set(psi: Psi, ti: ClassName) -> set[ClassName]:
    """Return the set of all ClassName T such that ti <: T.

    :param psi: The Psi object representing the type system.
    :param ti: The target class name.
    :return: A set of ClassNames that are supertypes of ti.
    """
    return {T for T in psi.Ns if is_subtype(psi, ti, T)}


def meet(psi: Psi, ti: ClassName, tj: ClassName) -> set[ClassName]:
    """Return the meet (greatest lower bound) of two class names in the type system.

    :param psi: The Psi object representing the type system.
    :param ti: The first class name.
    :param tj: The second class name.
    :return: A set of ClassName representing the meet.
    """
    common = lower_set(psi, ti).intersection(lower_set(psi, tj))

    meet_set = set()
    for t in common:
        if all(not is_subtype(psi, t, t_prime) for t_prime in common if t != t_prime):
            meet_set.add(t)

    return meet_set


def meet_unique(psi: Psi, ti: ClassName, tj: ClassName) -> ClassName | None:
    """Return the unique meet of two class names in the type system.

    :param psi: The Psi object representing the type system.
    :param ti: The first class name.
    :param tj: The second class name.
    :return: The unique meet of the two class names.
    """
    meet_set = meet(psi, ti, tj)
    if len(meet_set) == 1:
        return next(iter(meet_set))
    else:
        return None


def join(psi: Psi, ti: ClassName, tj: ClassName) -> set[ClassName]:
    """Return the join (least upper bound) of two class names in the type system.

    The join is the set of minimal elements in the intersection of the higher sets
    of `ti` and `tj`.

    :param psi: The Psi object representing the type system.
    :param ti: The first class name.
    :param tj: The second class name.
    :return: A set of ClassName representing the join.
    """
    common = upper_set(psi, ti).intersection(upper_set(psi, tj))

    join_set = set()
    for t in common:
        if all(not is_subtype(psi, t_prime, t) for t_prime in common if t != t_prime):
            join_set.add(t)

    return join_set


def join_unique(psi: Psi, ti: ClassName, tj: ClassName) -> ClassName | None:
    """Return the unique join of two class names in the type system.

    :param psi: The Psi object representing the type system.
    :param ti: The first class name.
    :param tj: The second class name.
    :return: The unique join of the two class names.
    """
    join_set = join(psi, ti, tj)
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

    :param psi: The Psi object representing the type system.
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
