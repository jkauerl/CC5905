import unittest

from src.gradual.definitions import (
    Edge,
    Environment,
    Signature,
    Specification,
)
from src.gradual.types import GradualFunctionType
from src.gradual.validations import (
    acyclic,
    exists_all_signatures,
    includes_node,
    is_valid_edge,
    is_valid_fun,
    is_valid_function,
    is_valid_graph,
    is_valid_node,
    is_valid_signature,
    is_valid_type,
    minimal_specification,
    no_overloading,
)
from src.static.types import ClassName


class TestValidations(unittest.TestCase):
    def setUp(self):
        cls = ClassName("A")
        sigs = [Signature("x", ClassName("A"))]
        sigma = {"A": Specification(sigs)}
        self.simple_psi = Environment(Ns=[cls], Es=[], sigma=sigma)

    def test_minimal_specification_true(self):
        spec = self.simple_psi.sigma["A"]
        self.assertTrue(minimal_specification(self.simple_psi, ClassName("A"), spec))

    def test_minimal_specification_false_due_to_missing_parent_method(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        edges = [Edge(source=class_a, target=class_b)]
        parent_sig = Signature("f", ClassName("B"))
        environment = Environment(
            Ns=[class_a, class_b],
            Es=edges,
            sigma={"A": Specification([]), "B": Specification([parent_sig])},
        )
        spec = Specification([])
        self.assertFalse(minimal_specification(environment, class_a, spec))

    def test_includes_node_true(self):
        spec = self.simple_psi.sigma["A"]
        self.assertTrue(includes_node(self.simple_psi, ClassName("A"), spec))

    def test_includes_node_false_missing_signature(self):
        cls = ClassName("A")
        sig = Signature("foo", ClassName("Int"))
        environment = Environment(Ns=[cls], Es=[], sigma={"A": Specification([sig])})
        spec = Specification([])
        self.assertFalse(includes_node(environment, cls, spec))

    def test_includes_node_false_wrong_type(self):
        cls = ClassName("A")
        correct_sig = Signature("foo", ClassName("Int"))
        environment = Environment(
            Ns=[cls], Es=[], sigma={"A": Specification([correct_sig])}
        )
        wrong_sig = Signature("foo", ClassName("Bool"))
        spec = Specification([wrong_sig])
        self.assertFalse(includes_node(environment, cls, spec))

    def test_exists_all_signatures_true(self):
        spec = self.simple_psi.sigma["A"]
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
        environment = Environment(
            Ns=[ClassName("A"), ClassName("Int")],
            Es=[],
            sigma={"A": Specification(sigs)},
        )
        spec = Specification(sigs)
        self.assertTrue(is_valid_signature(environment, spec))

    def test_graph_is_acyclic(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        edges = [Edge(source=class_a, target=class_b)]
        environment = Environment(
            Ns=[class_a, class_b],
            Es=edges,
            sigma={"A": Specification([]), "B": Specification([])},
        )
        self.assertTrue(acyclic(environment))

    def test_graph_is_not_acyclic(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        edges = [
            Edge(source=class_a, target=class_b),
            Edge(source=class_b, target=class_a),
        ]
        environment = Environment(
            Ns=[class_a, class_b],
            Es=edges,
            sigma={"A": Specification([]), "B": Specification([])},
        )
        self.assertFalse(acyclic(environment))

    def test_valid_type_true(self):
        environment = Environment(Ns=[ClassName("Int")], Es=[], sigma={})
        self.assertTrue(is_valid_type(environment, ClassName("Int")))

    def test_valid_type_false(self):
        environment = Environment(Ns=[ClassName("A")], Es=[], sigma={})
        self.assertFalse(is_valid_type(environment, ClassName("Unknown")))

    def test_valid_type_function_true(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        func = GradualFunctionType(domain=[class_a], codomain=class_b)
        environment = Environment(
            Ns=[class_a, class_b],
            Es=[],
            sigma={"A": Specification([]), "B": Specification([])},
        )
        self.assertTrue(is_valid_type(environment, func))

    def test_valid_type_function_false(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        func = GradualFunctionType(domain=[class_a], codomain=class_b)
        environment = Environment(Ns=[class_a], Es=[], sigma={"A": Specification([])})
        self.assertFalse(is_valid_type(environment, func))

    def test_valid_node_true(self):
        cls = ClassName("A")
        environment = Environment(Ns=[cls], Es=[], sigma={"A": Specification([])})
        self.assertTrue(is_valid_node(environment, cls))

    def test_valid_node_false(self):
        environment = Environment(Ns=[], Es=[], sigma={})
        self.assertFalse(is_valid_node(environment, ClassName("Missing")))

    def test_valid_edge_true(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        edge = Edge(source=class_a, target=class_b)
        environment = Environment(
            Ns=[class_a, class_b],
            Es=[edge],
            sigma={"A": Specification([]), "B": Specification([])},
        )
        self.assertTrue(is_valid_edge(environment, class_a, class_b))

    def test_valid_edge_false(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        environment = Environment(Ns=[class_a], Es=[], sigma={"A": Specification([])})
        self.assertFalse(is_valid_edge(environment, class_a, class_b))

    def test_valid_function_true(self):
        cls = ClassName("A")
        environment = Environment(Ns=[cls], Es=[], sigma={"A": Specification([])})
        func = GradualFunctionType(domain=[cls], codomain=cls)
        self.assertTrue(is_valid_function(environment, func))

    def test_valid_function_false(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        environment = Environment(Ns=[class_a], Es=[], sigma={"A": Specification([])})
        func = GradualFunctionType(domain=[class_a], codomain=class_b)
        self.assertFalse(is_valid_function(environment, func))

    def test_valid_fun_true(self):
        sig = Signature("foo", ClassName("A"))
        environment = Environment(
            Ns=[ClassName("A")], Es=[], sigma={"A": Specification([sig])}
        )
        self.assertTrue(is_valid_fun(environment))

    def test_valid_fun_false(self):
        sig = Signature("bar", ClassName("Missing"))
        cls = ClassName("A")
        environment = Environment(Ns=[cls], Es=[], sigma={"A": Specification([sig])})
        self.assertFalse(is_valid_fun(environment))

    def test_valid_graph_true(self):
        cls = ClassName("A")
        sig = Signature("foo", ClassName("A"))
        environment = Environment(Ns=[cls], Es=[], sigma={"A": Specification([sig])})
        self.assertTrue(is_valid_graph(environment))

    def test_valid_graph_false(self):
        cls = ClassName("A")
        sig = Signature("foo", ClassName("Unknown"))
        environment = Environment(Ns=[cls], Es=[], sigma={"A": Specification([sig])})
        self.assertFalse(is_valid_graph(environment))

    def test_valid_graph_missing_sigma_entry(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        sig_a = Signature("foo", ClassName("A"))
        environment = Environment(
            Ns=[class_a, class_b], Es=[], sigma={"A": Specification([sig_a])}
        )
        self.assertFalse(is_valid_graph(environment))

    def test_exists_all_signatures_false_on_extra_signature(self):
        class_a = ClassName("A")
        declared = [Signature("foo", class_a)]
        extra = Signature("bar", class_a)
        environment = Environment(
            Ns=[class_a], Es=[], sigma={"A": Specification(declared)}
        )
        spec_with_extra = Specification(declared + [extra])
        self.assertFalse(exists_all_signatures(environment, class_a, spec_with_extra))

    def test_is_valid_signature_false_on_invalid_signature(self):
        class_a = ClassName("A")
        sig_invalid = Signature(
            "foo", ClassName("Missing")
        )  # Invalid type (not in environment.Ns)
        environment = Environment(
            Ns=[class_a], Es=[], sigma={"A": Specification([sig_invalid])}
        )
        self.assertFalse(is_valid_signature(environment, environment.sigma["A"]))

    def test_is_valid_edge_false_when_edge_missing(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        environment = Environment(
            Ns=[class_a, class_b],
            Es=[],
            sigma={"A": Specification([]), "B": Specification([])},
        )
        self.assertFalse(is_valid_edge(environment, class_a, class_b))

    def test_valid_graph_cyclic_graph(self):
        class_a = ClassName("A")
        class_b = ClassName("B")
        edges = [
            Edge(source=class_a, target=class_b),
            Edge(source=class_b, target=class_a),
        ]
        environment = Environment(
            Ns=[class_a, class_b],
            Es=edges,
            sigma={
                "A": Specification([]),
                "B": Specification([]),
            },
        )
        self.assertFalse(is_valid_graph(environment))


if __name__ == "__main__":
    unittest.main()
