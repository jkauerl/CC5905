
from .definitions import Psi, Type, ClassName, FunctionType, BottomType, TopType, Specification

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


def is_subtype(psi: Psi, t1: Type, t2: Type, visited=None) -> bool:
    """Check if t1 is a subtype of t2 in the Psi type system.

    :param psi: The Psi object representing the type system.
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

    if isinstance(t1, FunctionType) and isinstance(t2, FunctionType):
        if len(t1.domain) != len(t2.domain):
            return False
        domain_check = all(
            is_subtype(psi, t2_arg, t1_arg, visited)
            for t1_arg, t2_arg in zip(t1.domain, t2.domain)
        )
        codomain_check = is_subtype(psi, t1.codomain, t2.codomain, visited)
        return domain_check and codomain_check

    if isinstance(t1, ClassName) and isinstance(t2, ClassName):
        for edge in psi.Es:
            if edge.source == t1:
                if is_subtype(psi, edge.target, t2, visited):
                    return True
    return False


def is_subtype_type(t1: Type, t2: Type, psi: Psi) -> bool:
    """Check if t1 is a subtype of t2, considering the Psi type system.
    
    :param t1: The first type to check.
    :param t2: The second type to check.
    :param psi: The Psi object representing the type system.
    :return: True if t1 is a subtype of t2, False otherwise.
    """
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
    """Check if specification s is a subtype of specification sp.
    
    :param s: The first specification to check.
    :param sp: The second specification to check.
    :param psi: The Psi object representing the type system.
    :return: True if s is a subtype of sp, False otherwise.
    """
    s_dict = {sig.var: sig.type for sig in s.signatures}
    for sig_p in sp.signatures:
        if sig_p.var not in s_dict:
            return False
        if not is_subtype_type(s_dict[sig_p.var], sig_p.type, psi):
            return False
    return True
