from abc import ABC
from src.static.definitions import (
    BottomType,
    ClassName,
    Edge,
    FunctionType,
    Psi,
    Specification,
    TopType,
    Signature,
)

""" Exports the classes and functions from the static definitions module. """

__all__ = [
    "TopType",
    "BottomType",
    "FunctionType",
    "ClassName",
    "Edge",
    "Psi",
    "Specification",
    "Signature",
]


class Type(ABC):
    """Abstract base class for all types."""

    pass


class Unknown(Type):
    """Represents an unknown type in the type system."""

    pass
