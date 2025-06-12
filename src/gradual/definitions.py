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
    Type,
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
    "Type",
]


class GradualType(ABC):
    """Abstract base class for all types."""

    pass


class Unknown(GradualType):
    """Represents an unknown type in the type system."""

    pass
