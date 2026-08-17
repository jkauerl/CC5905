from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class GradualType:
    """Base class for all gradual types.  Not an ABC (see static.types.Type)."""

    pass


@dataclass(frozen=True)
class GradualFunctionType(GradualType):
    """Represents a function type in the gradual system."""

    domain: Tuple[GradualType, ...]
    codomain: GradualType


@dataclass(frozen=True)
class Unknown(GradualType):
    """Represents an unknown type in the type system."""

    def __str__(self):
        return "?"
