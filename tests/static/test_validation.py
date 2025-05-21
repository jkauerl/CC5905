import unittest
from src.static.definitions import ClassName, Edge, Psi, Signature, Specification, FunctionType
from src.static.validations import (
    is_minimal_specification,
    is_includes_node,
    exists_all_signatures,
    no_overloading,
    acyclic,
    is_valid_type,
    is_valid_signature,
    is_valid_function,
    is_valid_node,
    is_valid_edge,
    is_valid_fun,
    is_valid_graph,
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

    def test_valid_type_true(self):
        psi = Psi(Ns=[ClassName("Int")], Es=[], sigma={})
        self.assertTrue(is_valid_type(psi, ClassName("Int")))

    def test_valid_type_false(self):
        psi = Psi(Ns=[ClassName("A")], Es=[], sigma={})
        self.assertFalse(is_valid_type(psi, ClassName("Unknown")))

    def test_valid_node_true(self):
        cls = ClassName("A")
        psi = Psi(Ns=[cls], Es=[], sigma={"A": []})
        self.assertTrue(is_valid_node(psi, cls))

    def test_valid_node_false(self):
        psi = Psi(Ns=[], Es=[], sigma={})
        self.assertFalse(is_valid_node(psi, ClassName("Missing")))

    def test_valid_edge_true(self):
        clsA = ClassName("A")
        clsB = ClassName("B")
        edge = Edge(source=clsA, target=clsB)
        psi = Psi(Ns=[clsA, clsB], Es=[edge], sigma={"A": [], "B": []})
        self.assertTrue(is_valid_edge(psi, clsA, clsB))

    def test_valid_edge_false(self):
        clsA = ClassName("A")
        clsB = ClassName("B")
        edge = Edge(source=clsA, target=clsB)
        psi = Psi(Ns=[clsA], Es=[], sigma={"A": []})  # missing B
        self.assertFalse(is_valid_edge(psi, clsA, clsB))

    def test_valid_function_true(self):
        cls = ClassName("A")
        psi = Psi(Ns=[cls], Es=[], sigma={"A": []})
        func = FunctionType(domain=[cls], codomain=cls)
        self.assertTrue(is_valid_function(psi, func))

    def test_valid_function_false(self):
        clsA = ClassName("A")
        clsB = ClassName("B")
        psi = Psi(Ns=[clsA], Es=[], sigma={"A": []})  # B is not in Ns
        func = FunctionType(domain=[clsA], codomain=clsB)
        self.assertFalse(is_valid_function(psi, func))

    def test_valid_fun_true(self):
        sig = Signature("foo", ClassName("A"))
        psi = Psi(Ns=[ClassName("A")], Es=[], sigma={"A": [sig]})
        self.assertTrue(is_valid_fun(psi))

    def test_valid_fun_false(self):
        sig = Signature("bar", ClassName("Missing"))
        cls = ClassName("A")
        psi = Psi(Ns=[cls], Es=[], sigma={"A": [sig]})  # <- Include the bad sig
        self.assertFalse(is_valid_fun(psi))

    def test_valid_graph_true(self):
        cls = ClassName("A")
        sig = Signature("foo", ClassName("A"))
        psi = Psi(Ns=[cls], Es=[], sigma={"A": [sig]})
        self.assertTrue(is_valid_graph(psi))

    def test_valid_graph_false(self):
        cls = ClassName("A")
        sig = Signature("foo", ClassName("Unknown"))
        psi = Psi(Ns=[cls], Es=[], sigma={"A": [sig]})
        self.assertFalse(is_valid_graph(psi))


if __name__ == "__main__":
    unittest.main()
