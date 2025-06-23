import unittest

from src.gradual.evidence.definitions import (
    EvidenceInterval,
    EvidenceSignature,
    EvidenceSpecification,
    Evidence,
    CompleteEvidence,
)
from src.gradual.definitions import Type, ClassName


class TestEvidence(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
