import unittest

from src.static.definitions import (
    ClassName,
    Edge,
    FunctionType,
    Psi,
    Signature,
    Specification,
)
from src.static.functions import (
    join,
    join_unique,
    lower_set,
    meet,
    meet_unique,
    names,
    proj,
    proj_many,
    upper_set,
)
from src.static.propositions import (
    is_direct_subtype,
    is_subtype,
    is_subtype_spec,
    is_subtype_type,
)


class TestFunctions(unittest.TestCase):
    def setUp(self):
        self.A = ClassName("A")
        self.B = ClassName("B")
        self.C = ClassName("C")
        self.D = ClassName("D")

        self.edges = [
            Edge(source=self.B, target=self.A),  # B <: A
            Edge(source=self.C, target=self.A),  # C <: A
            Edge(source=self.D, target=self.B),  # D <: B
            Edge(source=self.D, target=self.C),  # D <: C
        ]

        self.spec_A = Specification(signatures=[Signature(var="x", type=self.A)])
        self.spec_B = Specification(
            signatures=[
                Signature(var="x", type=self.A),
                Signature(var="y", type=FunctionType(domain=[self.A], codomain=self.B)),
            ]
        )

        self.spec_C = Specification(signatures=[Signature(var="x", type=self.A)])

        self.spec_D = Specification(signatures=[Signature(var="x", type=self.A)])

        self.psi = Psi(
            Ns=[self.A, self.B, self.C, self.D],
            Es=self.edges,
            sigma={
                "A": self.spec_A,
                "B": self.spec_B,
                "C": self.spec_C,
                "D": self.spec_D,
            },
        )

    def test_lower_set(self):
        result = lower_set(self.psi, self.A)
        print("result", result)
        self.assertIn(self.B, result)
        self.assertIn(self.C, result)
        self.assertIn(self.D, result)
        self.assertIn(self.A, result)

    def test_upper_set(self):
        self.assertIn(self.A, upper_set(self.psi, self.B))
        self.assertNotIn(self.C, upper_set(self.psi, self.B))

    def test_meet(self):
        m = meet(self.psi, self.B, self.C)
        self.assertIn(self.D, m)

    def test_meet_inheritance(self):
        m = meet(self.psi, self.A, self.B)
        self.assertIn(self.B, m)
        self.assertNotIn(self.A, m)

    def test_meet_unique(self):
        m = meet_unique(self.psi, self.B, self.C)

    def test_join(self):
        j = join(self.psi, self.B, self.C)
        self.assertIn(self.A, j)

    def test_join_inheritance(self):
        j = join(self.psi, self.A, self.B)
        self.assertIn(self.A, j)
        self.assertNotIn(self.B, j)

    def test_join_unique(self):
        self.assertEqual(join_unique(self.psi, self.B, self.C), self.A)

    def test_proj(self):
        self.assertEqual(proj("x", self.spec_B), self.A)
        self.assertEqual(
            proj("y", self.spec_B), FunctionType(domain=[self.A], codomain=self.B)
        )
        self.assertIsNone(proj("z", self.spec_B))

    def test_names(self):
        self.assertEqual(names(self.spec_B), {"x", "y"})

    def test_proj_many(self):
        specs = [self.spec_A, self.spec_B]
        results = proj_many("x", specs)
        print("results", results)
        self.assertEqual(results, [self.A, self.A])

    def test_is_direct_subtype(self):
        self.assertTrue(is_direct_subtype(self.psi, self.B, self.A))
        self.assertFalse(is_direct_subtype(self.psi, self.B, self.C))

    def test_is_subtype(self):
        self.assertTrue(is_subtype(self.psi, self.B, self.A))
        self.assertTrue(is_subtype(self.psi, self.C, self.A))
        self.assertFalse(is_subtype(self.psi, self.A, self.B))

    def test_is_subtype_type(self):
        self.assertTrue(is_subtype_type(ClassName("B"), ClassName("A"), self.psi))
        self.assertFalse(is_subtype_type(ClassName("A"), ClassName("B"), self.psi))

        t1 = FunctionType(domain=[ClassName("A")], codomain=ClassName("B"))
        t2 = FunctionType(domain=[ClassName("B")], codomain=ClassName("A"))

        self.assertTrue(is_subtype_type(t1, t2, self.psi))
        self.assertFalse(is_subtype_type(t2, t1, self.psi))

    def test_is_subtype_spec(self):
        self.assertTrue(is_subtype_spec(self.spec_B, self.spec_A, self.psi))
        self.assertFalse(is_subtype_spec(self.spec_A, self.spec_B, self.psi))


if __name__ == "__main__":
    unittest.main()
