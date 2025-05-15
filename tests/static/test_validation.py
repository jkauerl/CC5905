import pytest

from src.static.definitions import ClassName, Edge, Psi, Signature, Specification
from src.static.validations import (
    acyclic,
    exists_all_signatures,
    is_includes_node,
    is_minimal_specification,
    is_valid_signature,
    no_overloading,
)


@pytest.fixture
def simple_psi():
    # Define a minimal Psi system with one class and no inheritance
    cls = ClassName("A")
    sigs = [Signature("x", ClassName("A"))]
    sigma = {"A": sigs}
    return Psi(Ns=[cls], Es=[], sigma=sigma)


def test_minimal_specification_true(simple_psi):
    spec = Specification(simple_psi.sigma["A"])
    assert is_minimal_specification(ClassName("A"), spec, simple_psi)


def test_includes_node_true(simple_psi):
    spec = Specification(simple_psi.sigma["A"])
    assert is_includes_node(ClassName("A"), spec, simple_psi)


def test_exists_all_signatures_true(simple_psi):
    spec = Specification(simple_psi.sigma["A"])
    assert exists_all_signatures(simple_psi, ClassName("A"), spec)


def test_no_overloading_true():
    sigs = [Signature("f", ClassName("Int")), Signature("g", ClassName("Bool"))]
    spec = Specification(sigs)
    assert no_overloading(spec)


def test_no_overloading_false():
    sigs = [Signature("f", ClassName("Int")), Signature("f", ClassName("Bool"))]
    spec = Specification(sigs)
    assert not no_overloading(spec)


def test_valid_signature_true():
    sigs = [Signature("x", ClassName("Int"))]
    psi = Psi(Ns=[ClassName("A"), ClassName("Int")], Es=[], sigma={"A": sigs})
    assert is_valid_signature(psi, sigs)


def test_graph_is_acyclic():
    clsA = ClassName("A")
    clsB = ClassName("B")
    edges = [Edge(source=clsA, target=clsB)]
    psi = Psi(Ns=[clsA, clsB], Es=edges, sigma={"A": [], "B": []})
    assert acyclic(psi)


def test_graph_is_not_acyclic():
    clsA = ClassName("A")
    clsB = ClassName("B")
    edges = [Edge(source=clsA, target=clsB), Edge(source=clsB, target=clsA)]
    psi = Psi(Ns=[clsA, clsB], Es=edges, sigma={"A": [], "B": []})
    assert not acyclic(psi)
