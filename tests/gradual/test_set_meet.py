import unittest

from src.gradual.definitions import Edge, Environment, Signature, Specification
from src.gradual.functions import (
    get_specifications,
    join_unique_consistent_many,
    meet_unique_consistent_many,
)
from src.gradual.types import GradualFunctionType, Unknown
from src.static.types import BottomType, ClassName, TopType


def _env(names, edges, sigma=None):
    return Environment(
        Ns=[ClassName(n) for n in names],
        Es=[Edge(ClassName(a), ClassName(b)) for a, b in edges],
        sigma=sigma or {},
    )


class TestGradualSetMeet(unittest.TestCase):
    def setUp(self):
        self.A, self.C, self.E = ClassName("A"), ClassName("C"), ClassName("E")
        self.D1, self.D2 = ClassName("D1"), ClassName("D2")
        self.three = _env(
            ["A", "C", "E", "D1", "D2", "D3", "D4", "N"],
            [("D1", "A"), ("D1", "C"), ("D1", "E"), ("D2", "A"), ("D2", "C"),
             ("D3", "A"), ("D3", "E"), ("D4", "C"), ("D4", "E"),
             ("N", "A"), ("N", "C"), ("N", "E"), ("N", "D1")],
            sigma={
                "A": Specification([Signature("x", self.A)]),
                "C": Specification([Signature("x", self.C)]),
                "E": Specification([Signature("x", self.E)]),
                "D1": Specification([]),
                "N": Specification([]),
            },
        )
        self.arrow = GradualFunctionType((Unknown(),), Unknown())

    def test_names(self):
        A, C, E = self.A, self.C, self.E
        for order in ([A, C, E], [E, C, A]):
            self.assertEqual(meet_unique_consistent_many(self.three, order), self.D1)
        self.assertIsNone(meet_unique_consistent_many(self.three, [A, C]))

    def test_unknown_cases(self):
        A, C = self.A, self.C
        m = meet_unique_consistent_many
        self.assertEqual(m(self.three, [Unknown(), A, C]), Unknown())
        self.assertEqual(m(self.three, [Unknown(), A, self.arrow]), BottomType())
        self.assertEqual(m(self.three, [Unknown()]), Unknown())
        self.assertEqual(m(self.three, [Unknown(), TopType()]), Unknown())
        self.assertEqual(m(self.three, [TopType(), A]), A)
        self.assertEqual(m(self.three, [A, BottomType()]), BottomType())
        self.assertEqual(m(self.three, [A, self.arrow]), BottomType())
        # names with no common node beside a ?: ⊥
        no_common = _env(["A", "C"], [])
        self.assertEqual(m(no_common, [Unknown(), ClassName("A"), ClassName("C")]), BottomType())

    def test_functions(self):
        A, C, E = self.A, self.C, self.E
        fun = meet_unique_consistent_many(
            self.three,
            [GradualFunctionType((A,), A), GradualFunctionType((C,), C),
             GradualFunctionType((E,), E)],
        )
        self.assertEqual(fun, GradualFunctionType((TopType(),), self.D1))
        self.assertIsNone(meet_unique_consistent_many(
            self.three,
            [GradualFunctionType((Unknown(),), A), GradualFunctionType((self.D2,), C)]))
        self.assertEqual(
            join_unique_consistent_many(self.three, [Unknown(), A, self.arrow]), TopType())

    def test_spec_calculation(self):
        spec = get_specifications(self.three, ClassName("N"))
        self.assertIn(Signature("x", self.D1), spec.signatures)


if __name__ == "__main__":
    unittest.main()
