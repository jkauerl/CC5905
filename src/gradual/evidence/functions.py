from typing import Set, Tuple

from src.static.definitions import Type
from src.static.functions import join, meet

from ..definitions import (
    BottomType,
    Environment,
    GradualFunctionType,
    GradualType,
    TopType,
    Unknown,
)
from ..subtyping import is_subtype, is_subtype_spec
from .definitions import (
    CompleteEvidence,
    Evidence,
    EvidenceInterval,
    EvidenceSpecification,
)

""" Defintions of meet and join over the evidence in the type system
"""

# Meet


def meet_evidence_intervals(
    environment: Environment, interval_1: EvidenceInterval, interval_2: EvidenceInterval
) -> Set[EvidenceInterval]:
    """Compute the meet of two intervals in the type system.

    :param environment: The Environment object representing the type system.
    :param interval_1: The first interval to meet.
    :param interval_2: The second interval to meet.
    :return: A new Interval that is the meet of the two intervals.
    """
    lower_bounds = meet(environment, interval_1.lower_bound, interval_2.lower_bound)
    upper_bounds = meet(environment, interval_1.upper_bound, interval_2.upper_bound)
    intervals = set()
    for lower_bound in lower_bounds:
        for upper_bound in upper_bounds:
            if is_subtype(environment, lower_bound, upper_bound):
                intervals.add(EvidenceInterval(lower_bound, upper_bound))
    return intervals


def meet_evidence_specifications(
    environment: Environment,
    spec_1: EvidenceSpecification,
    spec_2: EvidenceSpecification,
) -> Set[EvidenceSpecification]:
    """Compute the meet of two specifications in the type system.

    :param environment: The Environment object representing the type system.
    :param spec_1: The first specification to meet.
    :param spec_2: The second specification to meet.
    :return: A new Specification that is the meet of the two specifications.
    """
    specifications = set()
    for signature_1 in spec_1.signatures:
        for signature_2 in spec_2.signatures:
            if signature_1.var == signature_2.var:
                new_signatures = meet_evidence_intervals(
                    environment, signature_1.interval, signature_2.interval
                )
                for new_signature in new_signatures:
                    extra_signatures = [
                        sig
                        for sig in spec_1.signatures + spec_2.signatures
                        if sig.var != signature_1.var
                    ]
                    combined = [new_signature] + extra_signatures
                    specifications.add(EvidenceSpecification(combined))

    return specifications


def meet_evidences(
    environment: Environment, evidence_1: Evidence, evidence_2: Evidence
) -> Set[Evidence]:
    """Compute the meet of two evidences in the type system.

    :param environment: The Environment object representing the type system.
    :param evidence_1: The first evidence to meet.
    :param evidence_2: The second evidence to meet.
    :return: A new Evidence that is the meet of the two evidences.
    """
    spec_1 = meet_evidence_specifications(
        environment, evidence_1.specification_1, evidence_2.specification_1
    )
    spec_2 = meet_evidence_specifications(
        environment, evidence_1.specification_2, evidence_2.specification_2
    )
    evidences = set()
    for s1 in spec_1:
        for s2 in spec_2:
            if is_subtype_spec(environment, s1, s2):
                evidences.add(Evidence(s1, s2))
    return evidences


def meet_complete_evidences(
    environment: Environment,
    complete_evidence_1: CompleteEvidence,
    complete_evidence_2: CompleteEvidence,
) -> CompleteEvidence:
    """Compute the meet of two complete evidences in the type system.

    :param environment: The Environment object representing the type system.
    :param complete_evidence_1: The first complete evidence to meet.
    :param complete_evidence_2: The second complete evidence to meet.
    :return: A new CompleteEvidence that is the meet of the two complete evidences.
    """
    evidences = []
    for ev1 in complete_evidence_1.evidences:
        for ev2 in complete_evidence_2.evidences:
            new_evidences = meet_evidences(environment, ev1, ev2)
            evidences.extend(new_evidences)
    return CompleteEvidence(evidences)


# Join


def join_evidence_intervals(
    environment: Environment, interval_1: EvidenceInterval, interval_2: EvidenceInterval
) -> Set[EvidenceInterval]:
    """Compute the join of two intervals in the type system.

    :param environment: The Environment object representing the type system.
    :param interval_1: The first interval to join.
    :param interval_2: The second interval to join.
    :return: A new Interval that is the join of the two intervals.
    """
    lower_bounds = join(environment, interval_1.lower_bound, interval_2.lower_bound)
    upper_bounds = join(environment, interval_1.upper_bound, interval_2.upper_bound)
    intervals = set()
    for lower_bound in lower_bounds:
        for upper_bound in upper_bounds:
            if is_subtype(environment, upper_bound, lower_bound):
                intervals.add(EvidenceInterval(lower_bound, upper_bound))
    return intervals


def join_evidence_specifications(
    environment: Environment,
    spec_1: EvidenceSpecification,
    spec_2: EvidenceSpecification,
) -> Set[EvidenceSpecification]:
    """Compute the join of two specifications in the type system.

    :param environment: The Environment object representing the type system.
    :param spec_1: The first specification to join.
    :param spec_2: The second specification to join.
    :return: A new Specification that is the join of the two specifications.
    """
    specifications = set()
    for signature_1 in spec_1.signatures:
        for signature_2 in spec_2.signatures:
            if signature_1.var == signature_2.var:
                new_signatures = join_evidence_intervals(
                    environment, signature_1, signature_2
                )
                for new_signature in new_signatures:
                    extra_signatures = [
                        sig
                        for sig in spec_1.signatures + spec_2.signatures
                        if sig.var != signature_1.var
                    ]
                    combined = [new_signature] + extra_signatures
                    specifications.add(EvidenceSpecification(combined))

    return specifications


def join_evidence(
    environment: Environment, evidence_1: Evidence, evidence_2: Evidence
) -> Set[Evidence]:
    """Compute the join of two evidences in the type system.

    :param environment: The Environment object representing the type system.
    :param evidence_1: The first evidence to join.
    :param evidence_2: The second evidence to join.
    :return: A new Evidence that is the join of the two evidences.
    """
    spec_1 = join_evidence_specifications(
        environment, evidence_1.specification_1, evidence_2.specification_1
    )
    spec_2 = join_evidence_specifications(
        environment, evidence_1.specification_2, evidence_2.specification_2
    )
    evidences = set()
    for s1 in spec_1:
        for s2 in spec_2:
            if is_subtype_spec(environment, s1, s2):
                evidences.add(Evidence(s1, s2))
    return evidences


def join_complete_evidences(
    environment: Environment,
    complete_evidence_1: CompleteEvidence,
    complete_evidence_2: CompleteEvidence,
) -> CompleteEvidence:
    """Compute the join of two complete evidences in the type system.

    :param environment: The Environment object representing the type system.
    :param complete_evidence_1: The first complete evidence to join.
    :param complete_evidence_2: The second complete evidence to join.
    :return: A new CompleteEvidence that is the join of the two complete evidences.
    """
    evidences = []
    for ev1 in complete_evidence_1.evidences:
        for ev2 in complete_evidence_2.evidences:
            new_evidences = join_evidence(environment, ev1, ev2)
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
        case GradualFunctionType(domain, codomain):
            domain_interval = lift_gradual_type(domain)
            codomain_interval = lift_gradual_type(codomain)
            lower_bound = GradualFunctionType(
                domain_interval.upper_bound, codomain_interval.lower_bound
            )
            upper_bound = GradualFunctionType(
                domain_interval.lower_bound, codomain_interval.upper_bound
            )
            return EvidenceInterval(lower_bound, upper_bound)
        case Unknown():
            return EvidenceInterval(BottomType(), TopType())
        case _:  # For all other concrete types
            return EvidenceInterval(t, t)


def interior_intervals(
    environment: Environment, interval_1: EvidenceInterval, interval_2: EvidenceInterval
) -> Set[Tuple[EvidenceInterval, EvidenceInterval]]:
    """Compute the interior intervals of two intervals in the type system.

    :param environment: The Environment object representing the type system.
    :param interval_1: The first interval to compute the interior of.
    :param interval_2: The second interval to compute the interior of.
    :return: A list of intervals that are the interior of the two intervals.
    """
    lowers = meet(environment, interval_1.upper_bound, interval_2.upper_bound)
    uppers = join(environment, interval_1.lower_bound, interval_2.lower_bound)

    pairs = set()
    for ti in lowers:
        for tj in uppers:
            first_interval = EvidenceInterval(interval_1.lower_bound, ti)
            second_interval = EvidenceInterval(tj, interval_2.upper_bound)
            pairs.add((first_interval, second_interval))

    return pairs


def interior_gradual_specification(
    environment: Environment,
    spec_1: EvidenceSpecification,
    spec_2: EvidenceSpecification,
) -> Set[Tuple[EvidenceSpecification, EvidenceSpecification]]:
    """Compute the interior signatures of two specifications in the type system.

    :param environment: The Environment object representing the type system.
    :param spec_1: The first specification to compute the interior of.
    :param spec_2: The second specification to compute the interior of.
    :return: A list of pairs of specifications that are the interior of the two
             specifications.
    """
    pairs = set()
    for signature_1 in spec_1.signatures:
        for signature_2 in spec_2.signatures:
            if signature_1.var == signature_2.var:
                intervals = interior_intervals(
                    environment, signature_1.interval, signature_2.interval
                )
                for interval_pair in intervals:
                    new_signature_1 = EvidenceSpecification(
                        [signature_1.var, interval_pair[0]]
                    )
                    new_signature_2 = EvidenceSpecification(
                        [signature_2.var, interval_pair[1]]
                    )
                    pairs.add((new_signature_1, new_signature_2))

    return pairs


def interior_types(
    environment: Environment, ti: GradualType, tj: GradualType
) -> Set[Tuple[EvidenceInterval, EvidenceInterval]]:
    """Compute the interior types of two gradual types in the type system.

    :param environment: The Environment object representing the type system.
    :param ti: The first gradual type to compute the interior of.
    :param tj: The second gradual type to compute the interior of.
    :return: A list of pairs of intervals that are the interior of the
             two gradual types.
    """
    match ti, tj:
        case GradualFunctionType(f1i, g2), GradualFunctionType(g3i, g4):
            domain_pairs = interior_types(environment, g3i, f1i)
            codomain_pairs = interior_types(environment, g2, g4)
            results = set()
            for (t1i, t2i), (t3i, t4i) in domain_pairs:
                for (t5, t6), (t7, t8) in codomain_pairs:
                    intv1 = EvidenceInterval(
                        GradualFunctionType(t4i, t5), GradualFunctionType(t3i, t6)
                    )
                    intv2 = EvidenceInterval(
                        GradualFunctionType(t2i, t7), GradualFunctionType(t1i, t8)
                    )
                    results.add((intv1, intv2))
            return results
        case GradualType(), GradualType():
            if is_subtype(environment, ti, tj):
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
        case GradualFunctionType(fi, fj), Unknown():
            unknown_fun = GradualFunctionType(Unknown(), Unknown())
            return {(EvidenceInterval(GradualFunctionType(fi, fj), unknown_fun),)}
        case Unknown(), GradualFunctionType(fi, fj):
            unknown_fun = GradualFunctionType(Unknown(), Unknown())
            return {(EvidenceInterval(unknown_fun, GradualFunctionType(fi, fj)),)}


def interior_specification(
    environment: Environment,
    spec_1: EvidenceSpecification,
    spec_2: EvidenceSpecification,
) -> Set[Tuple[EvidenceInterval, EvidenceInterval]]:
    """Compute the interior specifications of two specifications in the type system.

    :param environment: The Environment object representing the type system.
    :param spec_1: The first specification to compute the interior of.
    :param spec_2: The second specification to compute the interior of.
    :return: A list of pairs of specifications that are the interior of
             the two specifications.
    """
    result = set()
    all_vars = set(spec_1.keys()).union(set(spec_2.keys()))
    for var in all_vars:
        ti = spec_1.var
        tj = spec_2.var

        ti = ti if ti is not None else Unknown()
        tj = tj if tj is not None else Unknown()

        interior = interior_types(environment, ti, tj)
        if interior:
            result.append(interior)
        else:
            return []

    return result


def transitivity_interval(
    environment: Environment,
    par_interval_1: Tuple[EvidenceInterval, EvidenceInterval],
    par_interval_2: Tuple[EvidenceInterval, EvidenceInterval],
) -> Set[Tuple[EvidenceInterval, EvidenceInterval]]:
    """Compute the transitivity of two pairs of intervals in the type system.

    :param environment: The Environment object representing the type system.
    :param par_interval_1: The first pair of intervals to compute the transitivity of.
    :param par_interval_2: The second pair of intervals to compute the transitivity of.
    :return: A set of pairs of intervals that are the transitivity of the two pairs of
             intervals.
    """
    meet_group = meet_evidence_intervals(
        environment, par_interval_2[0], par_interval_1[1]
    )

    result = set()
    for i in meet_group:
        left_interiors = meet_evidence_intervals(environment, par_interval_1[0], i)
        right_interiors = meet_evidence_intervals(environment, i, par_interval_2[1])
        for j in left_interiors:
            for k in right_interiors:
                if j.upper_bound == k.lower_bound:
                    result.add((j.lower_bound, k.upper_bound))
    return result


def transitivity_specifications(
    environment: Environment,
    par_spec_1: Tuple[EvidenceSpecification, EvidenceSpecification],
    par_spec_2: Tuple[EvidenceSpecification, EvidenceSpecification],
) -> Set[Tuple[EvidenceSpecification, EvidenceSpecification]]:
    """Compute the transitivity of two specifications in the type system.

    :param environment: The Environment object representing the type system.
    :param spec_1: The first specification to compute the transitivity of.
    :param spec_2: The second specification to compute the transitivity of.
    :return: A set of pairs of specifications that are the transitivity of
             the two specifications.
    """
    meet_group = meet_evidence_specifications(environment, par_spec_2[0], par_spec_1[1])

    result = set()
    for i in meet_group:
        left_interior = meet_evidence_specifications(environment, par_spec_1[0], i)
        right_interior = meet_evidence_specifications(environment, i, par_spec_2[1])
        for j in left_interior:
            for k in right_interior:
                if all(
                    left.interval.upper_bound == right.interval.lower_bound
                    for left, right in zip(j.signatures, k.signatures)
                ):
                    left_bounds = [sig.interval.lower_bound for sig in j.signatures]
                    right_bounds = [sig.interval.upper_bound for sig in k.signatures]
                    result.add((left_bounds, right_bounds))
    return result


def transitivity_complete_evidences(
    environment: Environment,
    complete_evidence_1: CompleteEvidence,
    complete_evidence_2: CompleteEvidence,
) -> CompleteEvidence:
    """Compute the transitivity of two complete evidences in the type system.

    :param environment: The Environment object representing the type system.
    :param complete_evidence_1: The first complete evidence to compute the
           transitivity.
    :param complete_evidence_2: The second complete evidence to compute the
           transitivity.
    :return: A set of complete evidences that are the transitivity of the two complete
             evidences.
    """
    results = set()
    for ev1 in complete_evidence_1.evidences:
        for ev2 in complete_evidence_2.evidences:
            evidences = transitivity_specifications(
                environment,
                (ev1.specification_1, ev1.specification_2),
                (ev2.specification_1, ev2.specification_2),
            )
            for evidence in evidences:
                results.add(Evidence(evidence[0], evidence[1]))
    return CompleteEvidence(list(results))
