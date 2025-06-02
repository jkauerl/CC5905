from .definitions import ClassName, Psi, Type, Specification, Signature
from src.static.functions import (
    join_unique,
    lower_set,
    meet_unique,
    names,
    proj,
    proj_many,
    upper_set,
    get_all_parent_specifications,
    undeclared,
)

__all__ = [
    "join_unique",
    "lower_set",
    "meet_unique",
    "names",
    "proj",
    "proj_many",
    "upper_set",
    "get_all_parent_specifications",
    "undeclared",
]


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
            if isinstance(current_meet, ClassName) and isinstance(other_type, ClassName):
                m = meet_unique_consistent(psi, current_meet, other_type)
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

    inherited_signatures = [Signature(var=var, type=typ) for var, typ in inherited_vars.items()]

    combined_signatures_dict = {sig.var: sig for sig in explicit_signatures}
    for sig in inherited_signatures:
        if sig.var not in combined_signatures_dict:
            combined_signatures_dict[sig.var] = sig

    combined_signatures = list(combined_signatures_dict.values())

    return Specification(signatures=combined_signatures)
