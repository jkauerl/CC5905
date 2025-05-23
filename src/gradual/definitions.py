from src.static.definitions import Type, TopType, BottomType, FunctionType, ClassName, Edge, Signature, Psi, Specification

""" Exports the classes and functions from the static definitions module. """

__all__ = [
    "Type",
    "TopType",
    "BottomType",
    "FunctionType",
    "ClassName",
    "Edge",
    "Signature",
    "Psi",
    "Specification",
]

class Unknown(Type):
    """Represents an unknown type in the type system.

    :param Type: The type of the unknown type.
    """

    pass