from src.static.definitions import Type


class EvidenceInterval:
    """Represents a type with lower and upper bounds in the type system"""

    def __init__(self, lower_bound: Type, upper_bound: Type):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound


class EvidenceSignature:
    """Represents a signature in the type system with lower and upper bounds"""

    def __init__(self, var: str, interval: EvidenceInterval):
        self.var = var
        self.interval = interval


class EvidenceSpecification:
    """Represents a specification in the type system but with lower and upper bounds"""

    def __init__(self, signatures: list[EvidenceSignature]):
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

    def __init__(self, evidences: list[Evidence]):
        self.evidences = evidences
