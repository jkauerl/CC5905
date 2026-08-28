from typing import Any, Callable

from .definitions import (
    Environment,
    Specification,
)
from .types import BottomType, ClassName, FunctionType, TopType, Type

""" Propositions to check the type system
"""


def is_direct_subtype(
    environment: Environment, class_name_1: ClassName, class_name_2: ClassName
) -> bool:
    """Check if class_name_1 is a direct subtype of class_name_2.

    :param environment: The Environment object representing the type system.
    :param class_name_1: The first class name to check.
    :param class_name_2: The second class name to check.
    :return: True if class_name_1 is a direct subtype of class_name_2, False otherwise.
    """
    for edge in environment.Es:
        if edge.source == class_name_1 and edge.target == class_name_2:
            return True
    return False


def _ancestor_closure(environment: Environment) -> dict:
    """The transitive closure of the (name-level) edge relation, computed
    once per environment and cached on it: name -> set of ancestor names."""
    cache = getattr(environment, "_ancestor_closure", None)
    if cache is None:
        parents: dict = {}
        for edge in environment.Es:
            parents.setdefault(edge.source.name, []).append(edge.target.name)
        cache = {}

        def ancestors(name: str) -> set:
            known = cache.get(name)
            if known is not None:
                return known
            cache[name] = set()  # cycle guard
            reached: set = set()
            for parent in parents.get(name, ()):
                reached.add(parent)
                reached |= ancestors(parent)
            cache[name] = reached
            return reached

        for node in environment.Ns:
            ancestors(node.name)
        environment._ancestor_closure = cache
    return cache


def _descendant_closure(environment: Environment) -> dict:
    """The inverse of the ancestor closure, cached: name -> set of names
    reaching it."""
    cache = getattr(environment, "_descendant_closure", None)
    if cache is None:
        cache = {}
        for name, ancestors in _ancestor_closure(environment).items():
            cache.setdefault(name, set())
            for ancestor in ancestors:
                cache.setdefault(ancestor, set()).add(name)
        environment._descendant_closure = cache
    return cache


def supertype_names(environment: Environment, name: str) -> set:
    """{ A | N <: A } on names: N itself and everything it reaches.

    :param environment: The Environment object representing the type system.
    :param name: The name N.
    :return: The set of names A with N <: A.
    """
    return {name} | _ancestor_closure(environment).get(name, set())


def subtype_names(environment: Environment, name: str) -> set:
    """{ C | C <: N } on names: N itself and everything reaching it.

    :param environment: The Environment object representing the type system.
    :param name: The name N.
    :return: The set of names C with C <: N.
    """
    return {name} | _descendant_closure(environment).get(name, set())


def is_subtype(environment: Environment, t1: Type, t2: Type, visited=None) -> bool:
    """Check if t1 is a subtype of t2 in the Environment type system.

    Name-level subtyping is answered from the environment's cached
    transitive closure; function types recurse structurally.

    :param environment: The Environment object representing the type system.
    :param t1: The first type to check.
    :param t2: The second type to check.
    :param visited: Pairs already under consideration; a pre-seeded pair is
        reported as not-a-subtype, preserving the cycle-guard contract.
    :return: True if t1 is a subtype of t2, False otherwise.
    """
    if visited is not None and (t1, t2) in visited:
        return False

    if t1 == t2:
        return True

    if isinstance(t2, TopType):
        return True

    if isinstance(t1, BottomType):
        return True

    # If t1 is a function type, check if t2 is a function type
    if isinstance(t1, FunctionType) and isinstance(t2, FunctionType):
        if len(t1.domain) != len(t2.domain):
            return False
        domain_check = all(
            is_subtype(environment, t2_arg, t1_arg)
            for t1_arg, t2_arg in zip(t1.domain, t2.domain)
        )
        return domain_check and is_subtype(environment, t1.codomain, t2.codomain)

    if isinstance(t1, ClassName) and isinstance(t2, ClassName):
        return t2.name in _ancestor_closure(environment).get(t1.name, ())

    return False


def _is_subtype_spec_core(
    environment: Environment,
    s: Specification,
    sp: Specification,
    is_subtype_function: Callable[[Environment, Any, Any], bool],
) -> bool:
    """Core function to check if specification s is a subtype of specification sp.

    :param environment: The Environment object representing the type system.
    :param s: The first specification to check.
    :param sp: The second specification to check.
    :return: True if s is a subtype of sp, False otherwise.
    """
    s_dict = {sig.var: sig.type for sig in s.signatures}
    for sig_p in sp.signatures:
        if sig_p.var not in s_dict:
            return False
        s_type = s_dict[sig_p.var]
        if not is_subtype_function(environment, s_type, sig_p.type):
            return False
    return True


def is_subtype_spec(
    environment: Environment, s: Specification, sp: Specification
) -> bool:
    """Wrapper function to check if specification s is a subtype of specification sp.

    :param environment: The Environment object representing the type system.
    :param s: The first specification to check.
    :param sp: The second specification to check.
    :return: True if s is a subtype of sp, False otherwise.
    """
    return _is_subtype_spec_core(environment, s, sp, is_subtype)
