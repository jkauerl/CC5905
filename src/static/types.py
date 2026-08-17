from dataclasses import dataclass
from typing import Tuple


class Type:
    """Base class for all types.

    Deliberately not an ABC: these classes sit on the hot path of the
    validators and ABCMeta's __instancecheck__ makes every isinstance
    (and match/case) dispatch an order of magnitude slower.
    """

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
