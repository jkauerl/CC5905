from abc import ABC
from dataclasses import dataclass

""" Static type system for a programming language.
"""


class Type(ABC):
    """Abstract base class for all types.

    :param ABC: Abstract Base Class
    """

    pass


class TopType(Type):
    """Represents the top type in the type system.

    :param Type: The type of the top type.
    """

    pass


class BottomType(Type):
    """Represents the bottom type in the type system.

    :param Type: The type of the bottom type.
    """

    pass


@dataclass
class FunctionType(Type):
    """Represents a function type.

    :param Type: The type of the function.
    """

    domain: list[Type]
    codomain: Type


@dataclass(frozen=True)
class ClassName(Type):
    """Represents a class name. Which in part represents a node in the type system.

    :param Type: The type of the class.
    """

    name: str


class Edge:
    """Represents a directed edge in the type system."""

    def __init__(self, source: ClassName, target: ClassName):
        self.source = source
        self.target = target


class Signature:
    """Represents a signature in the type system."""

    def __init__(self, var: str, type: Type):
        self.var = var
        self.type = type


class Psi:
    """Represents the class (node) relationship in the type system."""

    def __init__(
        self, Ns: list[ClassName], Es: list[Edge], sigma: dict[str, list[Signature]]
    ):
        self.Ns = Ns
        self.Es = Es
        self.sigma = sigma  # This represents a function


class Specification:
    """Represents the specification of a class in the type system."""

    def __init__(self, signatures: list[Signature]):
        self.signatures = signatures
