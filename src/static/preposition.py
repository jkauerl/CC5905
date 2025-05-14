from definitions import ClassName, FunctionType, Psi, Specification, Type

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
        raise ValueError(f"Class name {class_name.name} not found in Psi object.")

    parent_specifications = []
    for edge in psi.Es:
        if is_direct_subtype(psi, class_name, edge.target):
            parent_specifications.append(psi.sigma[edge.target.name])
    return parent_specifications


