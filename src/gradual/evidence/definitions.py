from typing import Set
from src.gradual.definitions import GradualType


class EvidenceInterval:
    def __init__(self, lower_bound: GradualType, upper_bound: GradualType):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def __eq__(self, other):
        return (
            isinstance(other, EvidenceInterval) and
            self.lower_bound == other.lower_bound and
            self.upper_bound == other.upper_bound
        )

    def __hash__(self):
        return hash((self.lower_bound, self.upper_bound))

    def __repr__(self):
        return f"EvidenceInterval(lower_bound={self.lower_bound}, upper_bound={self.upper_bound})"


class EvidenceSignature:
    """Represents a signature in the type system with lower and upper bounds"""

    def __init__(self, var: str, interval: EvidenceInterval):
        self.var = var
        self.interval = interval

    def __eq__(self, other):
        return (
            isinstance(other, EvidenceSignature) and
            self.var == other.var and
            self.interval == other.interval
        )

    def __hash__(self):
        return hash((self.var, self.interval))

    def __repr__(self):
        return f"EvidenceSignature(var={self.var}, interval={self.interval})"


class EvidenceSpecification:
    """Represents a specification in the type system but with lower and upper bounds"""

    def __init__(self, signatures: Set[EvidenceSignature]):
        self.signatures = signatures


class Evidence:
    """Represents a collection of evidences in the type system"""

    def __init__(
        self,
        specification_1: EvidenceSpecification,
        specification_2: EvidenceSpecification,
    ):
        self.specification_1 = specification_1
        self.specification_2 = specification_2


class CompleteEvidence:
    """Represents complete evidence in the type system"""

    def __init__(self, evidences: Set[Evidence]):
        self.evidences = evidences
