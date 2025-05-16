import unittest
from src.static.definitions import ClassName, Edge, Psi, Signature, Specification
from src.static.validations import (
    acyclic,
    exists_all_signatures,
    is_includes_node,
    is_minimal_specification,
    is_valid_signature,
    no_overloading,
)


class TestValidations(unittest.TestCase):

    def setUp(self):
        cls = ClassName("A")
        sigs = [Signature("x", ClassName("A"))]
        sigma = {"A": sigs}
        self.simple_psi = Psi(Ns=[cls], Es=[], sigma=sigma)

    def test_minimal_specification_true(self):
        spec = Specification(self.simple_psi.sigma["A"])
        self.assertTrue(is_minimal_specification(ClassName("A"), spec, self.simple_psi))

    def test_includes_node_true(self):
        spec = Specification(self.simple_psi.sigma["A"])
        self.assertTrue(is_includes_node(ClassName("A"), spec, self.simple_psi))

    def test_exists_all_signatures_true(self):
        spec = Specification(self.simple_psi.sigma["A"])
        self.assertTrue(exists_all_signatures(self.simple_psi, ClassName("A"), spec))

    def test_no_overloading_true(self):
        sigs = [Signature("f", ClassName("Int")), Signature("g", ClassName("Bool"))]
        spec = Specification(sigs)
        self.assertTrue(no_overloading(spec))

    def test_no_overloading_false(self):
        sigs = [Signature("f", ClassName("Int")), Signature("f", ClassName("Bool"))]
        spec = Specification(sigs)
        self.assertFalse(no_overloading(spec))

    def test_valid_signature_true(self):
        sigs = [Signature("x", ClassName("Int"))]
        psi = Psi(Ns=[ClassName("A"), ClassName("Int")], Es=[], sigma={"A": sigs})
        self.assertTrue(is_valid_signature(psi, sigs))

    def test_graph_is_acyclic(self):
        clsA = ClassName("A")
        clsB = ClassName("B")
        edges = [Edge(source=clsA, target=clsB)]
        psi = Psi(Ns=[clsA, clsB], Es=edges, sigma={"A": [], "B": []})
        self.assertTrue(acyclic(psi))

    def test_graph_is_not_acyclic(self):
        clsA = ClassName("A")
        clsB = ClassName("B")
        edges = [Edge(source=clsA, target=clsB), Edge(source=clsB, target=clsA)]
        psi = Psi(Ns=[clsA, clsB], Es=edges, sigma={"A": [], "B": []})
        self.assertFalse(acyclic(psi))


if __name__ == "__main__":
    unittest.main()
