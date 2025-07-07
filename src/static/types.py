from abc import ABC
from dataclasses import dataclass
from typing import Tuple


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

    def __str__(self):
        return "⊤"


class BottomType(Type):
    """Represents the bottom type in the type system."""

    def __repr__(self):
        return "BottomType"

    def __str__(self):
        return "⊥"


@dataclass(frozen=True)
class FunctionType(Type):
    """Represents a function type."""

    domain: Tuple[Type, ...]
    codomain: Type

    def __hash__(self):
        return hash((self.domain, self.codomain))

    def __str__(self):
        domain_str = ", ".join(str(d) for d in self.domain)
        return f"({domain_str}) → {self.codomain}"


@dataclass(frozen=True)
class ClassName(Type):
    """Represents a class name. Which in part represents a node in the type system."""

    name: str

    def __repr__(self):
        return self.name
