from abc import ABC
from dataclasses import dataclass
from typing import Tuple

""" Static type system for a programming language.
"""


class Type(ABC):
    """Abstract base class for all types."""

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __hash__(self):
        return hash(self.__class__.__name__)

    def __repr__(self):
        return self.__class__.__name__



class TopType(Type):
    """Represents the top type in the type system."""

    def __repr__(self):
        return "TopType"


class BottomType(Type):
    """Represents the bottom type in the type system."""

    def __repr__(self):
        return "BottomType"


@dataclass(frozen=True)
class FunctionType(Type):
    """Represents a function type."""

    domain: Tuple[Type, ...]
    codomain: Type

    def __hash__(self):
        return hash((self.domain, self.codomain))


@dataclass(frozen=True)
class ClassName(Type):
    """Represents a class name. Which in part represents a node in the type system."""

    name: str

    def __repr__(self):
        return self.name


class Edge:
    """Represents a directed edge in the type system."""

    def __init__(self, source: ClassName, target: ClassName):
        self.source = source
        self.target = target


class Signature:
    """Represents a signature in the type system."""

    def __init__(self, var: str, type):
        self.var = var
        self.type = type

    def __repr__(self):
        return f"Signature(var={self.var}, type={self.type})"

    def __eq__(self, other):
        if not isinstance(other, Signature):
            return NotImplemented
        return self.var == other.var and self.type == other.type

    def __hash__(self):
        return hash((self.var, self.type))


class Specification:
    """Represents the specification of a class in the type system."""

    def __init__(self, signatures):
        self.signatures = set(signatures)

    def __repr__(self):
        return f"Specification(signatures={self.signatures})"

    def __eq__(self, other):
        if not isinstance(other, Specification):
            return NotImplemented
        return self.signatures == other.signatures

    def __hash__(self):
        return hash(frozenset(self.signatures))
    
    def keys(self):
        return {sig.var for sig in self.signatures}
    
    def get_signature(self, var):
        for sig in self.signatures:
            if sig.var == var:
                return sig
        return None


class Environment:
    """Represents the class (node) relationship in the type system."""

    def __init__(
        self, Ns: list[ClassName], Es: list[Edge], sigma: dict[str, Specification]
    ):
        self.Ns = Ns
        self.Es = Es
        self.sigma = sigma  # This represents a function
