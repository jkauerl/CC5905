import unittest

from src.static.definitions import Edge, Environment, Signature, Specification
from src.static.functions import (
    get_specifications,
    join_unique_many,
    meet_unique_many,
)
from src.static.propositions import minimal_specification
from src.static.types import BottomType, ClassName, FunctionType, TopType


def _env(names, edges, sigma=None):
    return Environment(
        Ns=[ClassName(n) for n in names],
        Es=[Edge(ClassName(a), ClassName(b)) for a, b in edges],
        sigma=sigma or {},
    )


class TestSetMeet(unittest.TestCase):
    """The meet is taken over the whole family, not folded pairwise."""

    def setUp(self):
        self.A, self.C, self.E = ClassName("A"), ClassName("C"), ClassName("E")
        self.D1, self.D2, self.D3, self.D4 = (
            ClassName("D1"), ClassName("D2"), ClassName("D3"), ClassName("D4"))
        self.B = ClassName("B")
        # A, C with two incomparable common lower bounds D1, D2; B below D1.
        self.two = _env(
            ["A", "C", "D1", "D2", "B"],
            [("D1", "A"), ("D1", "C"), ("D2", "A"), ("D2", "C"), ("B", "D1")],
        )
        # A, C, E pairwise ambiguous, with D1 below all three.
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

    def test_order_independent(self):
        A, B, C = self.A, self.B, self.C
        for order in ([A, B, C], [A, C, B], [B, A, C]):
            self.assertEqual(meet_unique_many(self.two, order), B)
        self.assertIsNone(meet_unique_many(self.two, [A, C]))

    def test_every_pair_ambiguous_family_unique(self):
        A, C, E = self.A, self.C, self.E
        for order in ([A, C, E], [A, E, C], [C, A, E], [C, E, A], [E, A, C], [E, C, A]):
            self.assertEqual(meet_unique_many(self.three, order), self.D1)
        self.assertIsNone(meet_unique_many(self.three, [A, C]))

    def test_top_bottom_and_functions(self):
        A, C, E = self.A, self.C, self.E
        self.assertEqual(meet_unique_many(self.three, [TopType(), A]), A)
        self.assertEqual(meet_unique_many(self.three, [A, BottomType()]), BottomType())
        self.assertEqual(meet_unique_many(self.three, []), TopType())
        fun = meet_unique_many(
            self.three,
            [FunctionType((A,), A), FunctionType((C,), C), FunctionType((E,), E)],
        )
        self.assertEqual(fun, FunctionType((TopType(),), self.D1))
        self.assertEqual(join_unique_many(self.three, [self.D2, self.D3, self.D4]), TopType())
        self.assertEqual(
            meet_unique_many(self.three, [A, FunctionType((A,), A)]), BottomType())

    def test_spec_calculation_uses_family_meet(self):
        spec = get_specifications(self.three, ClassName("N"))
        self.assertIn(Signature("x", self.D1), spec.signatures)

    def test_minimal_demands_defined_meet(self):
        env = _env(
            ["A", "C", "D1", "D2", "N"],
            [("D1", "A"), ("D1", "C"), ("D2", "A"), ("D2", "C"), ("N", "A"), ("N", "C")],
            sigma={
                "A": Specification([Signature("x", self.A)]),
                "C": Specification([Signature("x", self.C)]),
                "N": Specification([]),
            },
        )
        # D1 is below both parents' entries, but the meet of {A, C} is not unique.
        self.assertFalse(
            minimal_specification(env, ClassName("N"), Specification([Signature("x", self.D1)])))
        self.assertTrue(
            minimal_specification(self.three, ClassName("N"), Specification([Signature("x", self.D1)])))


if __name__ == "__main__":
    unittest.main()
