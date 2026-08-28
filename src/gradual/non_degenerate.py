from typing import Dict, List, Optional, Tuple

from ..static.subtyping import is_subtype
from ..static.types import BottomType, TopType, Type
from .definitions import Environment, Specification
from .neighbours import ancestors, descendants
from .types import GradualFunctionType, GradualType, Unknown

""" Non-degeneracy: the specification the flattening decides.

    NonDegenerate(Sigma)  <=>  for all N in nodes.  exists t_N in gamma(Sigma(N)).
        ( for all A in Anc(N).   exists t_A in gamma(Sigma(A)).  t_N <:s t_A )
      and
        ( for all C in Desc(N).  exists t_C in gamma(Sigma(C)).  t_C <:s t_N )

One concrete witness per node, shared by every pair through it (ancestors
and descendants from src/gradual/neighbours.py).  It implies PairValid (each
pair's witnesses are t_N and t_A); the converse fails on graphs with
non-unique meets (the crossing diamond).

Decision procedure.  Static spec subtyping t <:s t' is width + pointwise
covariant, and gamma keeps a spec's fields, so the witness exists iff the
field domains nest (dom Sigma(A) <= dom Sigma(N) <= dom Sigma(C)) and, per
field x of N independently, some T in gamma(Sigma(N)(x)) lies above every
concrete descendant declaration of x and below every concrete ancestor one
(an unknown declaration on the other side is met by bottom / top).  Fields
are first-order: gamma(?) is the finite set of names plus bottom and top;
function-typed fields are out of scope here and rejected.
"""


Sigma = Dict[str, Specification]


def concretizations(environment: Environment, t: GradualType) -> List[Type]:
    """gamma of a first-order gradual type: the type itself, or every static
    type of the environment for the unknown.

    :param environment: The Environment object representing the type system.
    :param t: The (first-order) gradual type.
    :return: The list of concrete types.
    """
    if isinstance(t, Unknown):
        return [BottomType(), TopType()] + list(environment.Ns)
    if isinstance(t, GradualFunctionType):
        raise ValueError("non_degenerate: function-typed fields are not supported")
    return [t]


def _by_var(specification: Specification) -> Dict[str, GradualType]:
    return {sig.var: sig.type for sig in specification.signatures}


def degenerate_nodes(
    environment: Environment, sigma: Sigma
) -> List[Tuple[str, Optional[str]]]:
    """Every node without a shared witness, with the field that blocks it.

    :param environment: The Environment object representing the type system.
    :param sigma: The specification assignment.
    :return: The list of (node, field) pairs; field is None when the domains
        fail to nest.
    """
    specs = {node.name: _by_var(sigma[node.name]) for node in environment.Ns}
    failures: List[Tuple[str, Optional[str]]] = []
    for node in environment.Ns:
        own = specs[node.name]
        above = [specs[a] for a in ancestors(environment, node.name)]
        below = [specs[c] for c in descendants(environment, node.name)]
        if any(not spec.keys() <= own.keys() for spec in above) or any(
            not own.keys() <= spec.keys() for spec in below
        ):
            failures.append((node.name, None))
            continue
        for var, declared in own.items():
            ceilings = [
                spec[var] for spec in above if var in spec
                and not isinstance(spec[var], Unknown)
            ]
            floors = [
                spec[var] for spec in below
                if not isinstance(spec[var], Unknown)
            ]
            if not any(
                all(is_subtype(environment, t, ceiling) for ceiling in ceilings)
                and all(is_subtype(environment, floor, t) for floor in floors)
                for t in concretizations(environment, declared)
            ):
                failures.append((node.name, var))
                break
    return failures


def non_degenerate(environment: Environment, sigma: Sigma) -> bool:
    """Non-degeneracy: a shared concrete witness at every node.

    :param environment: The Environment object representing the type system.
    :param sigma: The specification assignment.
    :return: True iff every node admits a witness below all its ancestors'
        concretizations and above all its descendants'.
    """
    return not degenerate_nodes(environment, sigma)
