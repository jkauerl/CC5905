from .definitions import Type


class Evidence:
    """A class to represent the evidence of a type in a gradual type system.
    In this implementation it is done with an interval.
    """

    def __init__(self, lower_bound: Type, upper_bound: Type):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound


class CompleteEvidence:
    """A class to represent complete evidence of a type in a gradual type system."""

    def __init__(self, evidence1: Evidence, evidence2: Evidence):
        self.evidences = (evidence1, evidence2)
