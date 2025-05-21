from .definitions import ClassName, FunctionType, Psi, Specification, Type

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
    for T in common:
        if all(not is_subtype(psi, T, T_prime) for T_prime in common if T != T_prime):
            meet_set.add(T)

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
    for T in common:
        if all(not is_subtype(psi, T_prime, T) for T_prime in common if T != T_prime):
            join_set.add(T)

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


def proj(t: ClassName, s: Specification) -> Type | None:
    """Project the specification s onto the class name t.

    :param psi: The Psi object representing the type system.
    :param t: The class name to project onto.
    :param s: The specification to project.
    :return: The projected type or None if not found.
    """
    for sig in s.signatures:
        if sig.var == t.name:
            return sig.type
    return None


def names(s: Specification) -> set[str]:
    """Get the names of the signatures in the specification.

    :param s: The specification to get the names from.
    :return: A list of names.
    """
    return {sig.var for sig in s.signatures}


def proj_many(x: ClassName, ss: list[Specification]) -> list[Type]:
    """Project the list of specifications ss onto the class name t.

    :param psi: The Psi object representing the type system.
    :param t: The class name to project onto.
    :param ss: The list of specifications to project.
    :return: A list of projected types.
    """
    return [proj(x, s) for s in ss if proj(x, s) is not None]


""" Propositions to check the type system
"""


def is_direct_subtype(
    psi: Psi, class_name_1: ClassName, class_name_2: ClassName
) -> bool:
    """Check if class_name_1 is a direct subtype of class_name_2.

    :param psi: The Psi object representing the type system.
    :param class_name_1: The first class name to check.
    :param class_name_2: The second class name to check.
    :return: True if class_name_1 is a direct subtype of class_name_2, False otherwise.
    """
    for edge in psi.Es:
        if edge.source == class_name_1 and edge.target == class_name_2:
            return True
    return False


def is_subtype(psi: Psi, class_name_1: ClassName, class_name_2: ClassName) -> bool:
    """Check if class_name_1 is a subtype of class_name_2.

    :param psi: The Psi object representing the type system.
    :param class_name_1: The first class name to check.
    :param class_name_2: The second class name to check.
    :return: True if class_name_1 is a subtype of class_name_2, False otherwise.
    """
    if class_name_1 == class_name_2:
        return True
    for edge in psi.Es:
        if edge.source == class_name_1 and edge.target == class_name_2:
            return True
        elif edge.source == class_name_1:
            return is_subtype(psi, edge.target, class_name_2)
    return False


def is_subtype_type(t1: Type, t2: Type, psi: Psi) -> bool:
    match (t1, t2):
        case (ClassName(n1), ClassName(n2)):
            return is_subtype(psi, ClassName(n1), ClassName(n2))
        case (FunctionType(dom1, cod1), FunctionType(dom2, cod2)):
            return (
                len(dom1) == len(dom2)
                and all(is_subtype_type(t2i, t1i, psi) for t1i, t2i in zip(dom1, dom2))
                and is_subtype_type(cod1, cod2, psi)
            )
        case _:
            return False


def is_subtype_spec(s: Specification, sp: Specification, psi: Psi) -> bool:
    s_dict = {sig.var: sig.type for sig in s.signatures}
    for sig_p in sp.signatures:
        if sig_p.var not in s_dict:
            return False
        if not is_subtype_type(s_dict[sig_p.var], sig_p.type, psi):
            return False
    return True


def get_all_parent_specifications(
    psi: Psi, class_name: ClassName
) -> list[Specification]:
    """Get all parent specifications of a given class name. By checking that the class name is a direct subtype of the parent class.

    :param psi: The Psi object representing the type system.
    :param class_name: The class name to get the parent specifications for.
    :return: A list of parent specifications.
    """
    if class_name.name not in [n.name for n in psi.Ns]:
        return []

    parent_specifications = []
    for edge in psi.Es:
        if is_direct_subtype(psi, class_name, edge.target):
            parent_specifications.append(psi.sigma[edge.target.name])
    return parent_specifications
