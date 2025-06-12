from typing import List, Set
from ..definitions import Psi,  GradualType, Unknown, BottomType, TopType, FunctionType, Specification
from .definitions import EvidenceInterval, EvidenceSpecification, Evidence, CompleteEvidence
from ..subtyping import is_subtype, is_subtype_spec
from src.static.functions import join, meet
from src.static.definitions import Type

""" Defintions of meet and join over the evidence in the type system
"""

# Meet

def meet_evidence_intervals(psi: Psi, interval_1: EvidenceInterval, interval_2: EvidenceInterval) -> list[EvidenceInterval]:
    """Compute the meet of two intervals in the type system.

    :param psi: The Psi object representing the type system.
    :param interval_1: The first interval to meet.
    :param interval_2: The second interval to meet.
    :return: A new Interval that is the meet of the two intervals.
    """
    lower_bounds = meet(psi, interval_1.lower_bound, interval_2.lower_bound)
    upper_bounds = meet(psi, interval_1.upper_bound, interval_2.upper_bound)
    intervals = []
    for lower_bound in lower_bounds:
        for upper_bound in upper_bounds:
            if is_subtype(psi, lower_bound, upper_bound):
                intervals.append(EvidenceInterval(lower_bound, upper_bound))
    return intervals


def meet_evidence_specifications(psi: Psi, spec_1: EvidenceSpecification, spec_2: EvidenceSpecification) -> list[EvidenceSpecification]:
    """Compute the meet of two specifications in the type system.

    :param psi: The Psi object representing the type system.
    :param spec_1: The first specification to meet.
    :param spec_2: The second specification to meet.
    :return: A new Specification that is the meet of the two specifications.
    """
    specifications = []
    for signature_1 in spec_1.signatures:
        for signature_2 in spec_2.signatures:
            if signature_1.var == signature_2.var:
                new_signatures = meet_evidence_intervals(psi, signature_1.interval, signature_2.interval)
                for new_signature in new_signatures:
                    extra_signatures = [
                        sig for sig in spec_1.signatures + spec_2.signatures
                        if sig.var != signature_1.var
                    ]
                    combined = [new_signature] + extra_signatures
                    specifications.append(EvidenceSpecification(combined))

    return specifications


def meet_evidences(psi: Psi, evidence_1: Evidence, evidence_2: Evidence) -> list[Evidence]:
    """Compute the meet of two evidences in the type system.
    
    :param psi: The Psi object representing the type system.
    :param evidence_1: The first evidence to meet.
    :param evidence_2: The second evidence to meet.
    :return: A new Evidence that is the meet of the two evidences.
    """
    spec_1 = meet_evidence_specifications(psi, evidence_1.specification_1, evidence_2.specification_1)
    spec_2 = meet_evidence_specifications(psi, evidence_1.specification_2, evidence_2.specification_2)
    evidences = []
    for s1 in spec_1:
        for s2 in spec_2:
            if is_subtype_spec(psi, s1, s2):
                evidences.append(Evidence(s1, s2))
    return evidences


def meet_complete_evidences(psi: Psi, complete_evidence_1: CompleteEvidence, complete_evidence_2: CompleteEvidence) -> CompleteEvidence:
    """Compute the meet of two complete evidences in the type system.

    :param psi: The Psi object representing the type system.
    :param complete_evidence_1: The first complete evidence to meet.
    :param complete_evidence_2: The second complete evidence to meet.
    :return: A new CompleteEvidence that is the meet of the two complete evidences.
    """
    evidences = []
    for ev1 in complete_evidence_1.evidences:
        for ev2 in complete_evidence_2.evidences:
            new_evidences = meet_evidences(psi, ev1, ev2)
            evidences.extend(new_evidences)
    return CompleteEvidence(evidences)

# Join

def join_evidence_intervals(psi: Psi, interval_1: EvidenceInterval, interval_2: EvidenceInterval) -> list[EvidenceInterval]:
    """Compute the join of two intervals in the type system.

    :param psi: The Psi object representing the type system.
    :param interval_1: The first interval to join.
    :param interval_2: The second interval to join.
    :return: A new Interval that is the join of the two intervals.
    """
    lower_bounds = join(psi, interval_1.lower_bound, interval_2.lower_bound)
    upper_bounds = join(psi, interval_1.upper_bound, interval_2.upper_bound)
    intervals = []
    for lower_bound in lower_bounds:
        for upper_bound in upper_bounds:
            if is_subtype(psi, upper_bound, lower_bound):
                intervals.append(EvidenceInterval(lower_bound, upper_bound))
    return intervals


def join_evidence_specifications(psi: Psi, spec_1: EvidenceSpecification, spec_2: EvidenceSpecification) -> list[EvidenceSpecification]:
    """Compute the join of two specifications in the type system.

    :param psi: The Psi object representing the type system.
    :param spec_1: The first specification to join.
    :param spec_2: The second specification to join.
    :return: A new Specification that is the join of the two specifications.
    """
    specifications = []
    for signature_1 in spec_1.signatures:
        for signature_2 in spec_2.signatures:
            if signature_1.var == signature_2.var:
                new_signatures = join_evidence_intervals(psi, signature_1, signature_2)
                for new_signature in new_signatures:
                    extra_signatures = [
                        sig for sig in spec_1.signatures + spec_2.signatures
                        if sig.var != signature_1.var
                    ]
                    combined = [new_signature] + extra_signatures
                    specifications.append(EvidenceSpecification(combined))

    return specifications


def join_evidence(psi: Psi, evidence_1: Evidence, evidence_2: Evidence) -> list[Evidence]:
    """Compute the join of two evidences in the type system.
    
    :param psi: The Psi object representing the type system.
    :param evidence_1: The first evidence to join.
    :param evidence_2: The second evidence to join.
    :return: A new Evidence that is the join of the two evidences.
    """
    spec_1 = join_evidence_specifications(psi, evidence_1.specification_1, evidence_2.specification_1)
    spec_2 = join_evidence_specifications(psi, evidence_1.specification_2, evidence_2.specification_2)
    evidences = []
    for s1 in spec_1:
        for s2 in spec_2:
            if is_subtype_spec(psi, s1, s2):
                evidences.append(Evidence(s1, s2))
    return evidences


def join_complete_evidences(psi: Psi, complete_evidence_1: CompleteEvidence, complete_evidence_2: CompleteEvidence) -> CompleteEvidence:
    """Compute the join of two complete evidences in the type system.

    :param psi: The Psi object representing the type system.
    :param complete_evidence_1: The first complete evidence to join.
    :param complete_evidence_2: The second complete evidence to join.
    :return: A new CompleteEvidence that is the join of the two complete evidences.
    """
    evidences = []
    for ev1 in complete_evidence_1.evidences:
        for ev2 in complete_evidence_2.evidences:
            new_evidences = join_evidence(psi, ev1, ev2)
            evidences.extend(new_evidences)
    return CompleteEvidence(evidences)

""" Interior functions
"""

def lift_gradual_type(t: GradualType) -> EvidenceInterval:
    """Lift a gradual type to a gradual type with lower and upper bounds.

    :param t: The type to lift.
    :return: A new Type that is the lifted gradual type.
    """
    match t:
        case FunctionType(domain, codomain):
            domain_interval = lift_gradual_type(domain)
            codomain_interval = lift_gradual_type(codomain)
            lower_bound = FunctionType(domain_interval.upper_bound, codomain_interval.lower_bound)
            upper_bound = FunctionType(domain_interval.lower_bound, codomain_interval.upper_bound)
            return Interval(lower_bound, upper_bound)
        case Unknown():
            return EvidenceInterval(BottomType(), TopType())
        case _: # For all other concrete types
            return EvidenceInterval(t, t)


def interior_intervals(psi: Psi, interval_1: EvidenceInterval, interval_2: EvidenceInterval) -> List[Set[EvidenceInterval, EvidenceInterval]]:
    """Compute the interior intervals of two intervals in the type system.

    :param psi: The Psi object representing the type system.
    :param interval_1: The first interval to compute the interior of.
    :param interval_2: The second interval to compute the interior of.
    :return: A list of intervals that are the interior of the two intervals.
    """
    lowers = meet(psi, interval_1.upper_bound, interval_2.upper_bound)
    uppers = join(psi, interval_1.lower_bound, interval_2.lower_bound)

    pairs = []
    for ti in lowers:
        for tj in uppers:
            first_interval = EvidenceInterval(interval_1.lower_bound, ti)
            second_interval = EvidenceInterval(tj, interval_2.upper_bound)
            pairs.append((first_interval, second_interval))

    return pairs


def interior_gradual_specification(psi: Psi, spec_1: EvidenceSpecification, spec_2: EvidenceSpecification) -> List[Set[EvidenceSpecification, EvidenceSpecification]]:
    """Compute the interior signatures of two specifications in the type system.

    :param psi: The Psi object representing the type system.
    :param spec_1: The first specification to compute the interior of.
    :param spec_2: The second specification to compute the interior of.
    :return: A list of pairs of specifications that are the interior of the two specifications.
    """
    pairs = []
    for signature_1 in spec_1.signatures:
        for signature_2 in spec_2.signatures:
            if signature_1.var == signature_2.var:
                intervals = interior_intervals(psi, signature_1.interval, signature_2.interval)
                for interval_pair in intervals:
                    new_signature_1 = EvidenceSpecification([signature_1.var, interval_pair[0]])
                    new_signature_2 = EvidenceSpecification([signature_2.var, interval_pair[1]])
                    pairs.append((new_signature_1, new_signature_2))

    return pairs


def interior_types(psi: Psi, ti: GradualType, tj: GradualType) -> List[Set[EvidenceInterval, EvidenceInterval]]:
    """Compute the interior types of two gradual types in the type system.

    :param psi: The Psi object representing the type system.
    :param ti: The first gradual type to compute the interior of.
    :param tj: The second gradual type to compute the interior of.
    :return: A list of pairs of intervals that are the interior of the two gradual types.
    """
    match ti, tj:
        case FunctionType(fi1, fj1), FunctionType(fi2, fj2):
            pass  # TODO: Handle function types
        case GradualType(), GradualType():
            if is_subtype(psi, ti, tj):
                spec_1 = lift_gradual_type(ti)
                return {(spec_1, EvidenceInterval(ti, tj))}
        case Type(), Unknown():
            spec_1 = lift_gradual_type(ti)
            return {(spec_1, EvidenceInterval(ti, TopType()))}
        case Unknown(), Type():
            spec_1 = lift_gradual_type(tj)
            return {(EvidenceInterval(BottomType(), tj), spec_1)}
        case Unknown(), Unknown():
            spec_1 = lift_gradual_type(Unknown())
            spec_2 = lift_gradual_type(Unknown())
            return {(spec_1, spec_2)}
        

def interior_specification(psi: Psi, spec_1: EvidenceSpecification, spec_2: EvidenceSpecification) -> List[Set[EvidenceInterval, EvidenceInterval]]:
    """Compute the interior specifications of two specifications in the type system.

    :param psi: The Psi object representing the type system.
    :param spec_1: The first specification to compute the interior of.
    :param spec_2: The second specification to compute the interior of.
    :return: A list of pairs of specifications that are the interior of the two specifications.
    """
    result = []

    all_vars = set(spec_1.keys()).union(set(spec_2.keys()))
    for var in all_vars:
        ti = spec_1.get(var)
        tj = spec_2.get(var)

        ti = ti if ti is not None else Unknown()
        tj = tj if tj is not None else Unknown()

        interior = interior_types(psi, ti, tj)
        if interior:
            result.append(interior)
        else:
            return []

    return result
