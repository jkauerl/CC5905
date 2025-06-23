from abc import ABC
from dataclasses import dataclass
from typing import Tuple

""" Static type system for a programming language.
"""


class Type(ABC):
    """Abstract base class for all types."""

    pass


class TopType(Type):
    """Represents the top type in the type system."""

    pass


class BottomType(Type):
    """Represents the bottom type in the type system."""

    pass


@dataclass(frozen=True)
class FunctionType(Type):
    """Represents a function type."""

    domain: Tuple[Type, ...]
    codomain: Type


@dataclass(frozen=True)
class ClassName(Type):
    """Represents a class name. Which in part represents a node in the type system."""

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


class Environment:
    """Represents the class (node) relationship in the type system."""

    def __init__(
        self, Ns: list[ClassName], Es: list[Edge], sigma: dict[str, list[Signature]]
    ):
        self.Ns = Ns
        self.Es = Es
        self.sigma = sigma  # This represents a function


class Specification:
    """Represents the specification of a class in the type system."""

    def __init__(self, signatures: list):
        self.signatures = signatures
