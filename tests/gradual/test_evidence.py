import unittest

from src.gradual.evidence.definitions import (
    EvidenceInterval,
    EvidenceSignature,
    EvidenceSpecification,
    Evidence,
    CompleteEvidence,
)
from src.gradual.definitions import ClassName, Edge, Specification, Signature, Unknown, Environment


class TestSimpleEvidence(unittest.TestCase):
    def setUp(self):
        self.lower_bound = ClassName("Int")
        self.upper_bound = ClassName("Float")
        self.evidence_interval = EvidenceInterval(self.lower_bound, self.upper_bound)

        self.evidence_signature = EvidenceSignature("x", self.evidence_interval)

        self.evidence_specification = EvidenceSpecification(
            [self.evidence_signature]
        )

        self.evidence_1 = Evidence(
            specification_1=self.evidence_specification,
            specification_2=self.evidence_specification,
        )

        self.complete_evidence = CompleteEvidence([self.evidence_1])

    def test_evidence_interval_initialization(self):
        self.assertEqual(
            self.evidence_interval.lower_bound, self.lower_bound
        )
        self.assertEqual(
            self.evidence_interval.upper_bound, self.upper_bound
        )


class TestEvidenceProgressive(unittest.TestCase):
    def setUp(self):
        self.A = ClassName("A")
        self.B = ClassName("B")
        self.C = ClassName("C")
        self.D = ClassName("D")
        self.E = ClassName("E")
        self.F = ClassName("F")

        self.edges = [
            Edge(source=self.B, target=self.A),
            Edge(source=self.C, target=self.A),
            Edge(source=self.D, target=self.B),
            Edge(source=self.D, target=self.C),
            Edge(source=self.E, target=self.B),
            Edge(source=self.E, target=self.C),
            Edge(source=self.F, target=self.D),
            Edge(source=self.F, target=self.E),
        ]

        self.A = Specification(signatures=[])
        self.spec_B = Specification(signatures=[Signature(var="x", type=self.B)])
        self.spec_C = Specification(
            signatures=[
                Signature(var="x", type=self.C),
                Signature(var="z", type=Unknown()),
            ]
        )
        self.spec_D = Specification(
            signatures=[
                Signature(var="x", type=Unknown()),
                Signature(var="z", type=Unknown()),
            ]
        )
        self.spec_E = Specification(
            signatures=[
                Signature(var="x", type=self.E),
            ]
        )
        self.spec_F = Specification(
            signatures=[
                Signature(var="z", type=self.F),
            ]
        )

        self.environment = Environment(
            Ns=[self.A, self.B, self.C, self.D, self.E, self.F],
            Es=self.edges,
            sigma={
                "A": Specification(signatures=[]),
                "B": self.spec_B,
                "C": self.spec_C,
                "D": self.spec_D,
                "E": self.spec_E,
                "F": self.spec_F,
            },
        )

    def test_declared_specification(self):
        # Check that the specifications are correctly declared and inherited
        self.assertIn(self.spec_B, self.environment.sigma.values())
        self.assertIn(self.spec_C, self.environment.sigma.values())
        self.assertIn(self.spec_D, self.environment.sigma.values())
        self.assertIn(self.spec_E, self.environment.sigma.values())
        self.assertIn(self.spec_F, self.environment.sigma.values())

if __name__ == "__main__":
    unittest.main()
