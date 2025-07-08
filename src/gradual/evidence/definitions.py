from typing import Set

from src.gradual.types import GradualType


class EvidenceInterval:
    """Represents an interval in the type system with lower and upper bounds"""

    def __init__(self, lower_bound: GradualType, upper_bound: GradualType):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def __eq__(self, other):
        return (
            isinstance(other, EvidenceInterval)
            and self.lower_bound == other.lower_bound
            and self.upper_bound == other.upper_bound
        )

    def __hash__(self):
        return hash((self.lower_bound, self.upper_bound))

    def __repr__(self):
        return f"EvidenceInterval(lower_bound={self.lower_bound}, \
            upper_bound={self.upper_bound})"

    def __str__(self):
        return f"[{self.lower_bound}, {self.upper_bound}]"


class EvidenceSignature:
    """Represents a signature in the type system with lower and upper bounds"""

    def __init__(self, var: str, interval: EvidenceInterval):
        self.var = var
        self.interval = interval

    def __eq__(self, other):
        return (
            isinstance(other, EvidenceSignature)
            and self.var == other.var
            and self.interval == other.interval
        )

    def __hash__(self):
        return hash((self.var, self.interval))

    def __repr__(self):
        return f"EvidenceSignature(var={self.var}, interval={self.interval})"

    def __str__(self):
        return f"{self.var}: {self.interval}"


class EvidenceSpecification:
    """Represents a specification in the type system but with lower and upper bounds"""

    def __init__(self, signatures: Set[EvidenceSignature]):
        self.signatures = signatures

    def __repr__(self):
        return f"EvidenceSpecification(signatures={self.signatures})"

    def __eq__(self, other):
        if not isinstance(other, EvidenceSpecification):
            return False
        return frozenset(self.signatures) == frozenset(other.signatures)

    def __hash__(self):
        return hash(frozenset(self.signatures))

    def __str__(self):
        return "{" + ", ".join(str(sig) for sig in self.signatures) + "}"


class Evidence:
    """Represents a collection of evidences in the type system"""

    def __init__(
        self,
        specification_1: EvidenceSpecification,
        specification_2: EvidenceSpecification,
    ):
        self.specification_1 = specification_1
        self.specification_2 = specification_2

    def __repr__(self):
        return f"Evidence(specification_1={self.specification_1}, \
            specification_2={self.specification_2})"

    def __eq__(self, other):
        if not isinstance(other, Evidence):
            return False
        return (
            self.specification_1 == other.specification_1
            and self.specification_2 == other.specification_2
        )

    def __hash__(self):
        return hash((self.specification_1, self.specification_2))

    def __str__(self):
        return f"⟨{self.specification_1}, {self.specification_2}⟩"


class CompleteEvidence:
    """Represents complete evidence in the type system"""

    def __init__(self, evidences: Set[Evidence]):
        self.evidences = evidences

    def __repr__(self):
        return f"CompleteEvidence(evidences={self.evidences})"

    def __eq__(self, other):
        if not isinstance(other, CompleteEvidence):
            return False
        return self.evidences == other.evidences

    def __hash__(self):
        return hash(frozenset(self.evidences))

    def __str__(self):
        return "{" + ", ".join(str(evidence) for evidence in self.evidences) + "}"
