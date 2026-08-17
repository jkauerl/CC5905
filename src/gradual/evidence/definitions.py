from typing import FrozenSet, Set

from src.gradual.types import GradualType

""" Evidence objects.

These are immutable once built and are used almost exclusively as set members,
so each caches its hash at construction and the two set-shaped ones store a
frozenset rather than a set.  Recomputing a hash here walks the whole nested
structure --- specification, signature, interval, type --- so an uncached hash
is paid again on every set insertion, membership test and dictionary lookup.
"""


class EvidenceInterval:
    """Represents an interval in the type system with lower and upper bounds"""

    __slots__ = ("lower_bound", "upper_bound", "_hash")

    def __init__(self, lower_bound: GradualType, upper_bound: GradualType):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self._hash = hash((lower_bound, upper_bound))

    def __eq__(self, other):
        return (
            isinstance(other, EvidenceInterval)
            and self._hash == other._hash
            and self.lower_bound == other.lower_bound
            and self.upper_bound == other.upper_bound
        )

    def __hash__(self):
        return self._hash

    def __repr__(self):
        return f"EvidenceInterval(lower_bound={self.lower_bound}, \
            upper_bound={self.upper_bound})"

    def __str__(self):
        return f"[{self.lower_bound}, {self.upper_bound}]"


class EvidenceSignature:
    """Represents a signature in the type system with lower and upper bounds"""

    __slots__ = ("var", "interval", "_hash")

    def __init__(self, var: str, interval: EvidenceInterval):
        self.var = var
        self.interval = interval
        self._hash = hash((var, interval))

    def __eq__(self, other):
        return (
            isinstance(other, EvidenceSignature)
            and self._hash == other._hash
            and self.var == other.var
            and self.interval == other.interval
        )

    def __hash__(self):
        return self._hash

    def __repr__(self):
        return f"EvidenceSignature(var={self.var}, interval={self.interval})"

    def __str__(self):
        return f"{self.var}: {self.interval}"


class EvidenceSpecification:
    """Represents a specification in the type system but with lower and upper bounds"""

    __slots__ = ("signatures", "_hash")

    def __init__(self, signatures: Set[EvidenceSignature]):
        frozen: FrozenSet[EvidenceSignature] = frozenset(signatures)
        self.signatures = frozen
        self._hash = hash(frozen)

    def __repr__(self):
        return f"EvidenceSpecification(signatures={set(self.signatures)})"

    def __eq__(self, other):
        if not isinstance(other, EvidenceSpecification):
            return False
        return self._hash == other._hash and self.signatures == other.signatures

    def __hash__(self):
        return self._hash

    def __str__(self):
        return "{" + ", ".join(str(sig) for sig in self.signatures) + "}"


class Evidence:
    """Represents a collection of evidences in the type system"""

    __slots__ = ("specification_1", "specification_2", "_hash")

    def __init__(
        self,
        specification_1: EvidenceSpecification,
        specification_2: EvidenceSpecification,
    ):
        self.specification_1 = specification_1
        self.specification_2 = specification_2
        self._hash = hash((specification_1, specification_2))

    def __repr__(self):
        return f"Evidence(specification_1={self.specification_1}, \
            specification_2={self.specification_2})"

    def __eq__(self, other):
        if not isinstance(other, Evidence):
            return False
        return (
            self._hash == other._hash
            and self.specification_1 == other.specification_1
            and self.specification_2 == other.specification_2
        )

    def __hash__(self):
        return self._hash

    def __str__(self):
        return f"⟨{self.specification_1}, {self.specification_2}⟩"


class CompleteEvidence:
    """Represents complete evidence in the type system"""

    __slots__ = ("evidences", "_hash")

    def __init__(self, evidences: Set[Evidence]):
        frozen: FrozenSet[Evidence] = frozenset(evidences)
        self.evidences = frozen
        self._hash = hash(frozen)

    def __repr__(self):
        return f"CompleteEvidence(evidences={set(self.evidences)})"

    def __eq__(self, other):
        if not isinstance(other, CompleteEvidence):
            return False
        return self._hash == other._hash and self.evidences == other.evidences

    def __hash__(self):
        return self._hash

    def __str__(self):
        return "{" + ", ".join(str(evidence) for evidence in self.evidences) + "}"
