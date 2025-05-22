import unittest

from src.static.definitions import (
    ClassName,
    Edge,
    FunctionType,
    Psi,
    Signature,
    Specification,
)
from src.static.validations import (
    acyclic,
    exists_all_signatures,
    is_includes_node,
    is_minimal_specification,
    is_valid_edge,
    is_valid_fun,
    is_valid_function,
    is_valid_graph,
    is_valid_node,
    is_valid_signature,
    is_valid_type,
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

    def test_minimal_specification_false_due_to_missing_parent_method(self):
        clsA = ClassName("A")
        clsB = ClassName("B")
        edges = [Edge(source=clsA, target=clsB)]
        parent_sig = Signature("f", ClassName("B"))
        psi = Psi(Ns=[clsA, clsB], Es=edges, sigma={"A": [], "B": [parent_sig]})
        spec = Specification([])
        self.assertFalse(is_minimal_specification(clsA, spec, psi))

    def test_includes_node_true(self):
        spec = Specification(self.simple_psi.sigma["A"])
        self.assertTrue(is_includes_node(ClassName("A"), spec, self.simple_psi))

    def test_is_includes_node_false_missing_signature(self):
        cls = ClassName("A")
        sig = Signature("foo", ClassName("Int"))
        psi = Psi(Ns=[cls], Es=[], sigma={"A": [sig]})
        spec = Specification([])
        self.assertFalse(is_includes_node(cls, spec, psi))

    def test_is_includes_node_false_wrong_type(self):
        cls = ClassName("A")
        correct_sig = Signature("foo", ClassName("Int"))
        psi = Psi(Ns=[cls], Es=[], sigma={"A": [correct_sig]})
        wrong_sig = Signature("foo", ClassName("Bool"))
        spec = Specification([wrong_sig])
        self.assertFalse(is_includes_node(cls, spec, psi))

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

    def test_valid_type_function_true(self):
        clsA = ClassName("A")
        clsB = ClassName("B")
        func = FunctionType(domain=[clsA], codomain=clsB)
        psi = Psi(Ns=[clsA, clsB], Es=[], sigma={"A": [], "B": []})
        self.assertTrue(is_valid_type(psi, func))

    def test_valid_type_function_false(self):
        clsA = ClassName("A")
        clsB = ClassName("B")
        func = FunctionType(domain=[clsA], codomain=clsB)
        psi = Psi(Ns=[clsA], Es=[], sigma={"A": []})
        self.assertFalse(is_valid_type(psi, func))

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

    def test_valid_graph_missing_sigma_entry(self):
        clsA = ClassName("A")
        clsB = ClassName("B")
        sigA = Signature("foo", ClassName("A"))
        psi = Psi(Ns=[clsA, clsB], Es=[], sigma={"A": [sigA]})  # Missing "B" in sigma
        self.assertFalse(is_valid_graph(psi))

    def test_exists_all_signatures_false_on_extra_signature(self):
        clsA = ClassName("A")
        declared = [Signature("foo", clsA)]
        extra = Signature("bar", clsA)
        psi = Psi(Ns=[clsA], Es=[], sigma={"A": declared})  # psi is valid
        spec_with_extra = Specification(declared + [extra])
        self.assertFalse(exists_all_signatures(psi, clsA, spec_with_extra))

    def test_is_valid_signature_false_on_invalid_signature(self):
        clsA = ClassName("A")
        sigInvalid = Signature(
            "foo", ClassName("Unknown")
        )  # Invalid type (not in psi.Ns)
        psi = Psi(Ns=[clsA], Es=[], sigma={"A": [sigInvalid]})
        self.assertFalse(is_valid_signature(psi, psi.sigma["A"]))

    def test_is_valid_edge_false_when_edge_missing(self):
        clsA = ClassName("A")
        clsB = ClassName("B")
        edge = Edge(source=clsA, target=clsB)
        psi = Psi(Ns=[clsA, clsB], Es=[], sigma={"A": [], "B": []})  # Edge not in Es
        self.assertFalse(is_valid_edge(psi, clsA, clsB))

    def test_valid_graph_cyclic_graph(self):
        clsA = ClassName("A")
        clsB = ClassName("B")
        edges = [
            Edge(source=clsA, target=clsB),
            Edge(source=clsB, target=clsA),
        ]  # Cycle
        psi = Psi(Ns=[clsA, clsB], Es=edges, sigma={"A": [], "B": []})
        self.assertFalse(is_valid_graph(psi))


if __name__ == "__main__":
    unittest.main()
