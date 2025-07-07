from abc import ABC
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class GradualType(ABC):
    """Abstract base class for all types."""

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
