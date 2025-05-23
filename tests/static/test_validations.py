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
        class_a = ClassName("A")
        class_b = ClassName("B")
        edges = [Edge(source=class_a, target=class_b)]
        parent_sig = Signature("f", ClassName("B"))
        psi = Psi(Ns=[class_a, class_b], Es=edges, sigma={"A": [], "B": [parent_sig]})
        spec = Specification([])
        self.assertFalse(is_minimal_specification(class_a, spec, psi))

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
        class_a = ClassName("A")
        class_b = ClassName("B")
        edges = [Edge(source=class_a, target=class_b)]
        psi = Psi(Ns=[class_a, class_b], Es=edges, sigma={"A": [], "B": []})
        self.assertTrue(acyclic(psi))

    def test_graph_is_not_acyclic(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        edges = [
            Edge(source=class_a, target=class_b),
            Edge(source=class_b, target=class_a),
        ]
        psi = Psi(Ns=[class_a, class_b], Es=edges, sigma={"A": [], "B": []})
        self.assertFalse(acyclic(psi))

    def test_valid_type_true(self):
        psi = Psi(Ns=[ClassName("Int")], Es=[], sigma={})
        self.assertTrue(is_valid_type(psi, ClassName("Int")))

    def test_valid_type_false(self):
        psi = Psi(Ns=[ClassName("A")], Es=[], sigma={})
        self.assertFalse(is_valid_type(psi, ClassName("Unknown")))

    def test_valid_type_function_true(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        func = FunctionType(domain=[class_a], codomain=class_b)
        psi = Psi(Ns=[class_a, class_b], Es=[], sigma={"A": [], "B": []})
        self.assertTrue(is_valid_type(psi, func))

    def test_valid_type_function_false(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        func = FunctionType(domain=[class_a], codomain=class_b)
        psi = Psi(Ns=[class_a], Es=[], sigma={"A": []})
        self.assertFalse(is_valid_type(psi, func))

    def test_valid_node_true(self):
        cls = ClassName("A")
        psi = Psi(Ns=[cls], Es=[], sigma={"A": []})
        self.assertTrue(is_valid_node(psi, cls))

    def test_valid_node_false(self):
        psi = Psi(Ns=[], Es=[], sigma={})
        self.assertFalse(is_valid_node(psi, ClassName("Missing")))

    def test_valid_edge_true(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        edge = Edge(source=class_a, target=class_b)
        psi = Psi(Ns=[class_a, class_b], Es=[edge], sigma={"A": [], "B": []})
        self.assertTrue(is_valid_edge(psi, class_a, class_b))

    def test_valid_edge_false(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        psi = Psi(Ns=[class_a], Es=[], sigma={"A": []})
        self.assertFalse(is_valid_edge(psi, class_a, class_b))

    def test_valid_function_true(self):
        cls = ClassName("A")
        psi = Psi(Ns=[cls], Es=[], sigma={"A": []})
        func = FunctionType(domain=[cls], codomain=cls)
        self.assertTrue(is_valid_function(psi, func))

    def test_valid_function_false(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        psi = Psi(Ns=[class_a], Es=[], sigma={"A": []})
        func = FunctionType(domain=[class_a], codomain=class_b)
        self.assertFalse(is_valid_function(psi, func))

    def test_valid_fun_true(self):
        sig = Signature("foo", ClassName("A"))
        psi = Psi(Ns=[ClassName("A")], Es=[], sigma={"A": [sig]})
        self.assertTrue(is_valid_fun(psi))

    def test_valid_fun_false(self):
        sig = Signature("bar", ClassName("Missing"))
        cls = ClassName("A")
        psi = Psi(Ns=[cls], Es=[], sigma={"A": [sig]})
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
        class_a = ClassName("A")
        class_b = ClassName("B")
        sig_a = Signature("foo", ClassName("A"))
        psi = Psi(Ns=[class_a, class_b], Es=[], sigma={"A": [sig_a]})
        self.assertFalse(is_valid_graph(psi))

    def test_exists_all_signatures_false_on_extra_signature(self):
        class_a = ClassName("A")
        declared = [Signature("foo", class_a)]
        extra = Signature("bar", class_a)
        psi = Psi(Ns=[class_a], Es=[], sigma={"A": declared})
        spec_with_extra = Specification(declared + [extra])
        self.assertFalse(exists_all_signatures(psi, class_a, spec_with_extra))

    def test_is_valid_signature_false_on_invalid_signature(self):
        class_a = ClassName("A")
        sig_invalid = Signature(
            "foo", ClassName("Unknown")
        )  # Invalid type (not in psi.Ns)
        psi = Psi(Ns=[class_a], Es=[], sigma={"A": [sig_invalid]})
        self.assertFalse(is_valid_signature(psi, psi.sigma["A"]))

    def test_is_valid_edge_false_when_edge_missing(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        psi = Psi(Ns=[class_a, class_b], Es=[], sigma={"A": [], "B": []})
        self.assertFalse(is_valid_edge(psi, class_a, class_b))

    def test_valid_graph_cyclic_graph(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        edges = [
            Edge(source=class_a, target=class_b),
            Edge(source=class_b, target=class_a),
        ]
        psi = Psi(Ns=[class_a, class_b], Es=edges, sigma={"A": [], "B": []})
        self.assertFalse(is_valid_graph(psi))


if __name__ == "__main__":
    unittest.main()
