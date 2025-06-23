from abc import ABC
from dataclasses import dataclass
from typing import Tuple

from src.static.definitions import (
    BottomType,
    ClassName,
    Edge,
    Psi,
    Signature,
    Specification,
    TopType,
    Type,
)

""" Exports the classes and functions from the static definitions module. """

__all__ = [
    "TopType",
    "BottomType",
    "ClassName",
    "Edge",
    "Psi",
    "Specification",
    "Signature",
    "Type",
]


@dataclass(frozen=True)
class GradualType(ABC):
    """Abstract base class for all types."""

    pass


@dataclass(frozen=True)
class GradualFunctionType(Type):
    """Represents a function type in the gradual system."""

    domain: Tuple[Type, ...]
    codomain: Type


class Unknown(GradualType):
    """Represents an unknown type in the type system."""

    pass
