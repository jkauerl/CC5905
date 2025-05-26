from src.static.definitions import (
    BottomType,
    ClassName,
    Edge,
    FunctionType,
    Psi,
    TopType,
    Type,
)

""" Exports the classes and functions from the static definitions module. """

__all__ = [
    "Type",
    "TopType",
    "BottomType",
    "FunctionType",
    "ClassName",
    "Edge",
    "Psi",
    "Specification",
]


class Unknown(Type):
    """Represents an unknown type in the type system."""

    pass


class Signature:
    """Represents a signature in a gradual type system."""

    def __init__(self, var: str, lower_bound: Type, upper_bound: Type):
        self.var = var
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
