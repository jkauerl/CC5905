from .definitions import ClassName, Psi, Signature, Specification, Type
from .subtyping import is_direct_subtype, is_subtype

""" Function to get parent specifications
"""


def get_all_parent_specifications(
    psi: Psi, class_name: ClassName
) -> list[Specification]:
    """Get all parent specifications of a given class name.
    By checking that the class name is a direct subtype of the parent class.

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


def meet(psi: Psi, ti: Type, tj: Type) -> set[Type]:
    """Return the meet (greatest lower bound) of two class names in the type system.

    :param psi: The Psi object representing the type system.
    :param ti: The first class name.
    :param tj: The second class name.
    :return: A set of Type representing the meet.
    """
    common = lower_set(psi, ti).intersection(lower_set(psi, tj))

    meet_set = set()
    for t in common:
        if all(not is_subtype(psi, t, t_prime) for t_prime in common if t != t_prime):
            meet_set.add(t)

    return meet_set


def meet_unique(psi: Psi, ti: Type, tj: Type) -> Type | None:
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


def join(psi: Psi, ti: Type, tj: Type) -> set[Type]:
    """Return the join (least upper bound) of two class names in the type system.

    The join is the set of minimal elements in the intersection of the higher sets
    of `ti` and `tj`.

    :param psi: The Psi object representing the type system.
    :param ti: The first class name.
    :param tj: The second class name.
    :return: A set of Type representing the join.
    """
    common = upper_set(psi, ti).intersection(upper_set(psi, tj))

    join_set = set()
    for t in common:
        if all(not is_subtype(psi, t_prime, t) for t_prime in common if t != t_prime):
            join_set.add(t)

    return join_set


def join_unique(psi: Psi, ti: Type, tj: Type) -> Type | None:
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


def undeclared(psi: Psi, class_name: ClassName) -> set[str]:
    """Return the set of undeclared variable names in the specification of a class name.

    These are names inherited from parents but not declared explicitly in the class.

    :param psi: The Psi object representing the type system.
    :param class_name: The class name to check.
    :return: A set of undeclared variable names.
    """
    sigma_spec = psi.sigma.get(class_name.name)
    if sigma_spec is None:
        return set()

    declared_names = set(names(sigma_spec))

    parent_specs = get_all_parent_specifications(psi, class_name)

    inherited_names = set()
    for spec in parent_specs:
        inherited_names.update(names(spec))

    undeclared_names = inherited_names - declared_names

    return undeclared_names


def inherited(psi: Psi, class_name: ClassName) -> dict[str, Type]:
    """Return the mapping of inherited variable names to their inferred types
    in the specification of a class name.

    Only includes variables inherited but not declared in the class.

    :param psi: The Psi object representing the type system.
    :param class_name: The class name to check.
    :return: A dictionary mapping variable names to their inferred types.
    """
    undeclared_names = undeclared(psi, class_name)
    parent_specs = get_all_parent_specifications(psi, class_name)

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
                m = meet_unique(psi, current_meet, other_type)
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


def specifications(psi: Psi, class_name: ClassName) -> Specification:
    """Return the full specification of a class name, including inherited variables.

    :param psi: The Psi object representing the type system.
    :param class_name: The class name to get the specification for.
    :return: The combined Specification of the class name.
    """
    explicit_spec = psi.sigma.get(class_name.name)
    if explicit_spec is None:
        explicit_signatures = []
    else:
        explicit_signatures = explicit_spec.signatures

    inherited_vars = inherited(psi, class_name)

    inherited_signatures = [
        Signature(var=var, type=typ) for var, typ in inherited_vars.items()
    ]

    combined_signatures_dict = {sig.var: sig for sig in explicit_signatures}
    for sig in inherited_signatures:
        if sig.var not in combined_signatures_dict:
            combined_signatures_dict[sig.var] = sig

    combined_signatures = list(combined_signatures_dict.values())

    return Specification(signatures=combined_signatures)
