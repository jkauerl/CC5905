from src.static.definitions import Type


class Signature:
    """ Represents a signature in the type system with lower and upper bounds"""

    def __init__(self, var: str, lower_bound: Type, upper_bound: Type):
        self.var = var
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound


class Specification:
    """ Represents a specification in the type system but with lower and upper bounds"""

    def __init__(self, signatures: list[Signature]):        
        self.signatures = signatures


class Evidence:
    """ Represents a collection of evidences in the type system"""

    def __init__(self, specification_1: Specification, specification_2: Specification):
        self.specification_1 = specification_1
        self.specification_2 = specification_2


class CompleteEvidence:
    """ Represents complete evidence in the type system"""

    def __init__(self, evidences: list[Evidence]):
        self.evidences = evidences
