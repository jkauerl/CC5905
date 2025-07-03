import unittest

from src.gradual.evidence.definitions import (
    EvidenceInterval,
    EvidenceSignature,
    EvidenceSpecification,
    Evidence,
    CompleteEvidence,
)
from src.gradual.evidence.functions import (
    interior_class_specification,
    meet_complete_evidences,
    transitivity_complete_evidences,
    meet_evidence_intervals,
)
from src.gradual.functions import (
    get_specifications,
)
from src.gradual.definitions import (
    ClassName,
    Edge,
    Environment,
    Signature,
    Specification,
    Unknown,
    BottomType,
    TopType,
)


class TestSimpleEvidence(unittest.TestCase):
    def setUp(self):
        self.lower_bound = ClassName("A")
        self.upper_bound = ClassName("B")
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

        self.spec_A = Specification(signatures=[])
        self.spec_B = Specification(signatures=[Signature(var="x", type=self.B)])
        self.spec_C = Specification(
            signatures={
                Signature(var="x", type=self.C),
                Signature(var="z", type=Unknown()),
            }
        )
        self.spec_D = Specification(
            signatures={
                Signature(var="x", type=Unknown()),
                Signature(var="y", type=self.A),
                # Signature(var="z", type=Unknown()), # Inherited
            }
        )
        self.spec_E = Specification(
            signatures={
                Signature(var="x", type=self.E),
                # Signature(var="z", type=Unknown()), # inherited
            }
        )
        self.spec_F = Specification(
            signatures={
                # Signature(var="x", type=Unknown()), # inherited
                # Signature(var="y", type=self.A), # inherited
                Signature(var="z", type=self.D),
            }
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
        self.assertIn(self.spec_B, self.environment.sigma.values())
        self.assertIn(self.spec_C, self.environment.sigma.values())
        self.assertIn(self.spec_D, self.environment.sigma.values())
        self.assertIn(self.spec_E, self.environment.sigma.values())
        self.assertIn(self.spec_F, self.environment.sigma.values())

    def test_get_all_parent_specifications(self):
        # No need to test A, B and C, as they don't inherit anything.
        correct_specs_D = Specification(
            signatures={
                Signature(var="x", type=Unknown()),
                Signature(var="y", type=self.A),
                Signature(var="z", type=Unknown()),
            }
        )
        correct_specs_E = Specification(
            signatures={
                Signature(var="x", type=self.E),
                Signature(var="z", type=Unknown()),
            }
        )
        correct_specs_F = Specification(
            signatures={
                Signature(var="x", type=Unknown()),
                Signature(var="y", type=self.A),
                Signature(var="z", type=self.D),
            }
        )

        specs_D = get_specifications(self.environment, self.D)
        specs_E = get_specifications(self.environment, self.E)
        specs_F = get_specifications(self.environment, self.F)

        self.assertEqual(specs_D, correct_specs_D)
        self.assertEqual(specs_E, correct_specs_E)
        self.assertEqual(specs_F, correct_specs_F)

    def test_interior_class_specifications(self):
        interior_b_a = set([
            (
                frozenset({EvidenceSignature("x", EvidenceInterval(self.B, self.B))}),
                frozenset()
            )
        ])
        interior_c_a = set([
            (
                frozenset({
                    EvidenceSignature("x", EvidenceInterval(self.C, self.C)),
                    EvidenceSignature("z", EvidenceInterval(BottomType(), TopType())),
                }),
                frozenset()
            )
        ])
        interior_d_b = set([
            (
                frozenset({
                    EvidenceSignature("x", EvidenceInterval(BottomType(), self.B)),
                    EvidenceSignature("y", EvidenceInterval(self.A, self.A)),
                    EvidenceSignature("z", EvidenceInterval(BottomType(), TopType())),
                }),
                frozenset({
                    EvidenceSignature("x", EvidenceInterval(self.B, self.B)),
                })
            )
        ])
        interior_d_c = set([
            (
                frozenset({
                    EvidenceSignature("x", EvidenceInterval(BottomType(), self.C)),
                    EvidenceSignature("y", EvidenceInterval(self.A, self.A)),
                    EvidenceSignature("z", EvidenceInterval(BottomType(), TopType())),
                }),
                frozenset({
                    EvidenceSignature("x", EvidenceInterval(self.C, self.C)),
                    EvidenceSignature("z", EvidenceInterval(BottomType(), TopType())),
                })
            )
        ])
        interior_e_b = set([
            (
                frozenset({
                    EvidenceSignature("x", EvidenceInterval(self.E, self.E)),
                    EvidenceSignature("z", EvidenceInterval(BottomType(), TopType())),
                }),
                frozenset({
                    EvidenceSignature("x", EvidenceInterval(self.B, self.B)),
                })
            )
        ])
        interior_e_c = set([
            (
                frozenset({
                    EvidenceSignature("x", EvidenceInterval(self.E, self.E)),
                    EvidenceSignature("z", EvidenceInterval(BottomType(), TopType())),
                }),
                frozenset({
                    EvidenceSignature("x", EvidenceInterval(self.C, self.C)),
                    EvidenceSignature("z", EvidenceInterval(BottomType(), TopType())),
                })
            )
        ])
        interior_f_d = set([
            (
                frozenset({
                    EvidenceSignature("x", EvidenceInterval(BottomType(), TopType())),
                    EvidenceSignature("y", EvidenceInterval(self.A, self.A)),
                    EvidenceSignature("z", EvidenceInterval(self.D, self.D)),
                }),
                frozenset({
                    EvidenceSignature("x", EvidenceInterval(BottomType(), TopType())),
                    EvidenceSignature("y", EvidenceInterval(self.A, self.A)),
                    EvidenceSignature("z", EvidenceInterval(self.D, TopType())),
                })
            )
        ])
        interior_f_e = set([
            (
                frozenset({
                    EvidenceSignature("x", EvidenceInterval(BottomType(), self.E)),
                    EvidenceSignature("y", EvidenceInterval(self.A, self.A)),
                    EvidenceSignature("z", EvidenceInterval(self.D, self.D)),
                }),
                frozenset({
                    EvidenceSignature("x", EvidenceInterval(self.E, self.E)),
                    EvidenceSignature("z", EvidenceInterval(self.D, TopType())),
                })
            )
        ])

        calculated_interior_b_a = interior_class_specification(
            self.environment, get_specifications(self.environment, self.B), get_specifications(self.environment, self.A)
        )
        calculated_interior_c_a = interior_class_specification(
            self.environment, get_specifications(self.environment, self.C), get_specifications(self.environment, self.A)
        )
        calculated_interior_d_b = interior_class_specification(
            self.environment, get_specifications(self.environment, self.D), get_specifications(self.environment, self.B)
        )
        calculated_interior_d_c = interior_class_specification(
            self.environment, get_specifications(self.environment, self.D), get_specifications(self.environment, self.C)
        )
        calculated_interior_e_b = interior_class_specification(
            self.environment, get_specifications(self.environment, self.E), get_specifications(self.environment, self.B)
        )
        calculated_interior_e_c = interior_class_specification(
            self.environment, get_specifications(self.environment, self.E), get_specifications(self.environment, self.C)
        )
        calculated_interior_f_d = interior_class_specification(
            self.environment, get_specifications(self.environment, self.F), get_specifications(self.environment, self.D)
        )
        calculated_interior_f_e = interior_class_specification(
            self.environment, get_specifications(self.environment, self.F), get_specifications(self.environment, self.E)
        )

        self.assertEqual(calculated_interior_b_a, interior_b_a)
        self.assertEqual(calculated_interior_c_a, interior_c_a)
        self.assertEqual(calculated_interior_d_b, interior_d_b)
        self.assertEqual(calculated_interior_d_c, interior_d_c)
        self.assertEqual(calculated_interior_e_b, interior_e_b)
        self.assertEqual(calculated_interior_e_c, interior_e_c)
        self.assertEqual(calculated_interior_f_d, interior_f_d)
        self.assertEqual(calculated_interior_f_e, interior_f_e)


if __name__ == "__main__":
    unittest.main()
