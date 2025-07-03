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

    def test_get_specifications_D(self):
        correct_specs_D = Specification(
            signatures={
                Signature(var="x", type=Unknown()),
                Signature(var="y", type=self.A),
                Signature(var="z", type=Unknown()),
            }
        )
        specs_D = get_specifications(self.environment, self.D)
        self.assertEqual(specs_D, correct_specs_D)


    def test_get_specifications_E(self):
        correct_specs_E = Specification(
            signatures={
                Signature(var="x", type=self.E),
                Signature(var="z", type=Unknown()),
            }
        )
        specs_E = get_specifications(self.environment, self.E)
        self.assertEqual(specs_E, correct_specs_E)


    def test_get_specifications_F(self):
        correct_specs_F = Specification(
            signatures={
                Signature(var="x", type=Unknown()),
                Signature(var="y", type=self.A),
                Signature(var="z", type=self.D),
            }
        )
        specs_F = get_specifications(self.environment, self.F)
        self.assertEqual(specs_F, correct_specs_F)

    def test_interior_b_a(self):
        expected = Evidence(
            EvidenceSpecification({
                EvidenceSignature("x", EvidenceInterval(self.B, self.B))
            }),
            EvidenceSpecification(set())
        )

        result = interior_class_specification(
            self.environment,
            get_specifications(self.environment, self.B),
            get_specifications(self.environment, self.A)
        )
        self.assertIsNotNone(result)
        self.assertEqual(result, expected)

    def test_interior_c_a(self):
        expected = Evidence(
            EvidenceSpecification({
                EvidenceSignature("x", EvidenceInterval(self.C, self.C)),
                EvidenceSignature("z", EvidenceInterval(BottomType(), TopType())),
            }),
            EvidenceSpecification(set())
        )

        result = interior_class_specification(
            self.environment,
            get_specifications(self.environment, self.C),
            get_specifications(self.environment, self.A)
        )
        self.assertIsNotNone(result)
        self.assertEqual(result, expected)

    def test_interior_d_b(self):
        expected = Evidence(
            EvidenceSpecification({
                EvidenceSignature("x", EvidenceInterval(BottomType(), self.B)),
                EvidenceSignature("y", EvidenceInterval(self.A, self.A)),
                EvidenceSignature("z", EvidenceInterval(BottomType(), TopType())),
            }),
            EvidenceSpecification({
                EvidenceSignature("x", EvidenceInterval(self.B, self.B)),
            })
        )

        result = interior_class_specification(
            self.environment,
            get_specifications(self.environment, self.D),
            get_specifications(self.environment, self.B)
        )
        self.assertIsNotNone(result)
        self.assertEqual(result, expected)

    def test_interior_d_c(self):
        expected = Evidence(
            EvidenceSpecification({
                EvidenceSignature("x", EvidenceInterval(BottomType(), self.C)),
                EvidenceSignature("y", EvidenceInterval(self.A, self.A)),
                EvidenceSignature("z", EvidenceInterval(BottomType(), TopType())),
            }),
            EvidenceSpecification({
                EvidenceSignature("x", EvidenceInterval(self.C, self.C)),
                EvidenceSignature("z", EvidenceInterval(BottomType(), TopType())),
            })
        )

        result = interior_class_specification(
            self.environment,
            get_specifications(self.environment, self.D),
            get_specifications(self.environment, self.C)
        )
        self.assertIsNotNone(result)
        self.assertEqual(result, expected)

    def test_interior_e_b(self):
        expected = Evidence(
            EvidenceSpecification({
                EvidenceSignature("x", EvidenceInterval(self.E, self.E)),
                EvidenceSignature("z", EvidenceInterval(BottomType(), TopType())),
            }),
            EvidenceSpecification({
                EvidenceSignature("x", EvidenceInterval(self.B, self.B)),
            })
        )

        result = interior_class_specification(
            self.environment,
            get_specifications(self.environment, self.E),
            get_specifications(self.environment, self.B)
        )
        self.assertIsNotNone(result)
        self.assertEqual(result, expected)

    def test_interior_e_c(self):
        expected = Evidence(
            EvidenceSpecification({
                EvidenceSignature("x", EvidenceInterval(self.E, self.E)),
                EvidenceSignature("z", EvidenceInterval(BottomType(), TopType())),
            }),
            EvidenceSpecification({
                EvidenceSignature("x", EvidenceInterval(self.C, self.C)),
                EvidenceSignature("z", EvidenceInterval(BottomType(), TopType())),
            })
        )

        result = interior_class_specification(
            self.environment,
            get_specifications(self.environment, self.E),
            get_specifications(self.environment, self.C)
        )
        self.assertIsNotNone(result)
        self.assertEqual(result, expected)

    def test_interior_f_d(self):
        expected = Evidence(
            EvidenceSpecification({
                EvidenceSignature("x", EvidenceInterval(BottomType(), TopType())),
                EvidenceSignature("y", EvidenceInterval(self.A, self.A)),
                EvidenceSignature("z", EvidenceInterval(self.D, self.D)),
            }),
            EvidenceSpecification({
                EvidenceSignature("x", EvidenceInterval(BottomType(), TopType())),
                EvidenceSignature("y", EvidenceInterval(self.A, self.A)),
                EvidenceSignature("z", EvidenceInterval(self.D, TopType())),
            })
        )

        result = interior_class_specification(
            self.environment,
            get_specifications(self.environment, self.F),
            get_specifications(self.environment, self.D)
        )
        self.assertIsNotNone(result)
        self.assertEqual(result, expected)

    def test_interior_f_e(self):
        expected = Evidence(
            EvidenceSpecification({
                EvidenceSignature("x", EvidenceInterval(BottomType(), self.E)),
                EvidenceSignature("y", EvidenceInterval(self.A, self.A)),
                EvidenceSignature("z", EvidenceInterval(self.D, self.D)),
            }),
            EvidenceSpecification({
                EvidenceSignature("x", EvidenceInterval(self.E, self.E)),
                EvidenceSignature("z", EvidenceInterval(self.D, TopType())),
            })
        )

        result = interior_class_specification(
            self.environment,
            get_specifications(self.environment, self.F),
            get_specifications(self.environment, self.E)
        )
        self.assertIsNotNone(result)
        self.assertEqual(result, expected)

    

if __name__ == "__main__":
    unittest.main()
