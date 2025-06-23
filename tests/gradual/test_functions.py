import unittest

from src.gradual.definitions import (
    BottomType,
    ClassName,
    Edge,
    GradualFunctionType,
    Environment,
    Signature,
    Specification,
    TopType,
)
from src.gradual.functions import (
    inherited,
    join_unique,
    lower_set,
    meet_unique,
    names,
    proj,
    proj_many,
    specifications,
    undeclared,
    upper_set,
)
from src.gradual.subtyping import (
    is_subtype,
    is_subtype_spec,
)
from src.static.functions import (
    get_all_parent_specifications,
    meet,
    join,
)
from src.static.subtyping import (
    is_direct_subtype,
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
                Signature(
                    var="y", type=GradualFunctionType(domain=[self.A], codomain=self.B)
                ),
            ]
        )

        self.spec_C = Specification(signatures=[Signature(var="x", type=self.A)])

        self.spec_D = Specification(signatures=[Signature(var="x", type=self.A)])

        self.environment = Environment(
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
        result = lower_set(self.environment, self.A)
        self.assertIn(self.B, result)
        self.assertIn(self.C, result)
        self.assertIn(self.D, result)
        self.assertIn(self.A, result)

    def test_upper_set(self):
        self.assertIn(self.A, upper_set(self.environment, self.B))
        self.assertNotIn(self.C, upper_set(self.environment, self.B))

    def test_meet(self):
        m = meet(self.environment, self.B, self.C)
        self.assertIn(self.D, m)

    def test_meet_inheritance(self):
        m = meet(self.environment, self.A, self.B)
        self.assertIn(self.B, m)
        self.assertNotIn(self.A, m)

    def test_meet_unique(self):
        m = meet_unique(self.environment, self.B, self.C)
        self.assertEqual(m, self.D)

    def test_join(self):
        j = join(self.environment, self.B, self.C)
        self.assertIn(self.A, j)

    def test_join_inheritance(self):
        j = join(self.environment, self.A, self.B)
        self.assertIn(self.A, j)
        self.assertNotIn(self.B, j)

    def test_join_unique(self):
        self.assertEqual(join_unique(self.environment, self.B, self.C), self.A)

    def test_proj(self):
        self.assertEqual(proj("x", self.spec_B), self.A)
        self.assertEqual(
            proj("y", self.spec_B), GradualFunctionType(domain=[self.A], codomain=self.B)
        )
        self.assertIsNone(proj("z", self.spec_B))

    def test_names(self):
        self.assertEqual(names(self.spec_B), {"x", "y"})

    def test_proj_many(self):
        specs = [self.spec_A, self.spec_B]
        results = proj_many("x", specs)
        self.assertEqual(results, [self.A, self.A])

    def test_is_direct_subtype(self):
        self.assertTrue(is_direct_subtype(self.environment, self.B, self.A))
        self.assertFalse(is_direct_subtype(self.environment, self.B, self.C))

    def test_is_subtype(self):
        self.assertTrue(is_subtype(self.environment, self.B, self.A))
        self.assertTrue(is_subtype(self.environment, self.C, self.A))
        self.assertFalse(is_subtype(self.environment, self.A, self.B))

    def test_is_subtype_cycle_detection(self):
        visited = set()
        visited.add((self.B, self.A))
        self.assertFalse(is_subtype(self.environment, self.B, self.A, visited))

    def test_is_subtype_identity(self):
        self.assertTrue(is_subtype(self.environment, self.B, self.B))

    def test_is_subtype_toptype(self):
        self.assertTrue(is_subtype(self.environment, self.B, TopType()))

    def test_is_subtype_bottomtype(self):
        self.assertTrue(is_subtype(self.environment, BottomType(), self.A))

    def test_is_subtype_function_type_domain_length_mismatch(self):
        ft1 = GradualFunctionType(domain=(self.A, self.B), codomain=self.C)
        ft2 = GradualFunctionType(domain=(self.A,), codomain=self.C)
        self.assertFalse(is_subtype(self.environment, ft1, ft2))

    def test_is_subtype_function_type_codomain_mismatch(self):
        ft1 = GradualFunctionType(domain=(self.A,), codomain=self.A)
        ft2 = GradualFunctionType(domain=(self.A,), codomain=self.B)

        self.assertFalse(is_subtype(self.environment, ft1, ft2))

    def test_is_subtype_spec(self):
        self.assertTrue(is_subtype_spec(self.spec_B, self.spec_A, self.environment))
        self.assertFalse(is_subtype_spec(self.spec_A, self.spec_B, self.environment))

    def test_is_not_subtype_spec(self):
        spec1 = Specification(signatures=[Signature(var="x", type=self.B)])
        spec2 = Specification(signatures=[Signature(var="x", type=self.C)])
        self.assertFalse(is_subtype_spec(spec1, spec2, self.environment))

    def test_get_all_parent_specifications(self):
        parent_specs = get_all_parent_specifications(self.environment, self.D)
        self.assertIn(self.spec_B, parent_specs)
        self.assertIn(self.spec_C, parent_specs)
        self.assertNotIn(self.spec_A, parent_specs)

    def test_undeclared(self):
        undeclared_vars = undeclared(self.environment, self.D)
        self.assertIn("y", undeclared_vars)
        self.assertNotIn("x", undeclared_vars)

    def test_inherited(self):
        inherited_vars = inherited(self.environment, self.D)
        self.assertIn("y", inherited_vars)
        self.assertIsInstance(inherited_vars["y"], GradualFunctionType)
        self.assertEqual(inherited_vars["y"].codomain, self.B)
        self.assertNotIn("x", inherited_vars)

    def test_specifications(self):
        spec = specifications(self.environment, self.D)
        var_names = {sig.var for sig in spec.signatures}
        self.assertIn("x", var_names)
        self.assertIn("y", var_names)
        y_sig = next(sig for sig in spec.signatures if sig.var == "y")
        self.assertIsInstance(y_sig.type, GradualFunctionType)
        self.assertEqual(y_sig.type.codomain, self.B)


# TODO: High level functions for testing

if __name__ == "__main__":
    unittest.main()
