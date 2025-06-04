from abc import ABC
from src.static.definitions import (
    BottomType,
    ClassName,
    Edge,
    FunctionType,
    Psi,
    Specification,
    TopType,
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
]


class Type(ABC):
    """Abstract base class for all types."""

    pass


class Unknown(Type):
    """Represents an unknown type in the type system."""

    pass


class Signature:
    """Represents a signature in a gradual type system."""

    def __init__(self, var: str, type: Type, lower_bound: Type, upper_bound: Type):
        self.var = var
        self.type = type
