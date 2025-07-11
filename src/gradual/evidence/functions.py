from itertools import product
from typing import Dict, Optional, Set, Tuple

from src.static.functions import join, meet
from src.static.subtyping import is_subtype

from ...static.types import BottomType, TopType, Type
from ..definitions import (
    Environment,
    Specification,
)
from ..subtyping import is_gradual_subtype
from ..types import GradualFunctionType, GradualType, Unknown
from .definitions import (
    CompleteEvidence,
    Evidence,
    EvidenceInterval,
    EvidenceSignature,
    EvidenceSpecification,
)
from .subtyping import is_subtype_evidence_spec

""" Defintions of meet and join over the evidence in the type system
"""


# Meet


def meet_evidence_intervals(
    environment: Environment, sig_1: EvidenceSignature, sig_2: EvidenceSignature
) -> Set[EvidenceSignature]:
    """Compute the meet of two intervals in the type system.

    :param environment: The Environment object representing the type system.
    :param sig_1: The first signature to meet.
    :param sig_2: The second signature to meet.
    :return: A set of EvidenceSignatures that are the meet of the two signatures.
    """

    lower_bounds = meet(
        environment, sig_1.interval.lower_bound, sig_2.interval.lower_bound
    )
    upper_bounds = meet(
        environment, sig_1.interval.upper_bound, sig_2.interval.upper_bound
    )

    signatures = set()
    for lower in lower_bounds:
        for upper in upper_bounds:
            if is_subtype(environment, lower, upper):
                interval = EvidenceInterval(lower, upper)
                signatures.add(EvidenceSignature(sig_1.var, interval))
    return signatures


def meet_evidence_specifications(
    environment: Environment,
    spec_1: EvidenceSpecification,
    spec_2: EvidenceSpecification,
) -> Set[EvidenceSpecification]:
    """Compute the meet of two specifications in the type system.

    :param environment: The Environment object representing the type system.
    :param spec_1: The first specification to meet.
    :param spec_2: The second specification to meet.
    :return: A set of EvidenceSpecifications that are the meet of the two
        specifications.
    """
    result = set()
    sigs_1 = {sig.var: sig for sig in spec_1.signatures}
    sigs_2 = {sig.var: sig for sig in spec_2.signatures}

    meets_by_var = {}

    all_vars = sigs_1.keys() | sigs_2.keys()  # union of variables

    for var in all_vars:
        sig_1 = sigs_1.get(var)
        sig_2 = sigs_2.get(var)

        if sig_1 and sig_2:
            meets_by_var[var] = meet_evidence_intervals(environment, sig_1, sig_2)
        elif sig_1:
            meets_by_var[var] = {sig_1}
        else:
            meets_by_var[var] = {sig_2}

    for combo in product(*meets_by_var.values()):
        spec = EvidenceSpecification(set(combo))
        result.add(spec)

    return result


def meet_evidences(
    environment: Environment, evidence_1: Evidence, evidence_2: Evidence
) -> Set[Evidence]:
    """Compute the meet of two evidences in the type system.

    :param environment: The Environment object representing the type system.
    :param evidence_1: The first evidence to meet.
    :param evidence_2: The second evidence to meet.
    :return: A set of Evidence that are the meet of the two evidences.
    """
    s1_meet_s3 = meet_evidence_specifications(
        environment, evidence_1.specification_1, evidence_2.specification_1
    )
    s2_meet_s4 = meet_evidence_specifications(
        environment, evidence_1.specification_2, evidence_2.specification_2
    )

    evidences = set()
    for s_prime_1 in s1_meet_s3:
        for s_prime_2 in s2_meet_s4:
            if is_subtype_evidence_spec(environment, s_prime_1, s_prime_2):
                ev = Evidence(s_prime_1, s_prime_2)
                evidences.add(ev)
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
    evidences = set()
    for ev1 in complete_evidence_1.evidences:
        for ev2 in complete_evidence_2.evidences:
            new_evidences = meet_evidences(environment, ev1, ev2)
            evidences.update(new_evidences)

    return CompleteEvidence(evidences)


""" Precision meet
"""


def meet_precision_interval(
    environment: Environment, i1: EvidenceInterval, i2: EvidenceInterval
) -> Set[EvidenceInterval]:
    """Compute the precision meet of two intervals in the type system.

    :param environment: The Environment object representing the type system.
    :param i1: The first interval to meet.
    :param i2: The second interval to meet.
    :return: A set of EvidenceIntervals that are the precision meet of the two
        intervals.
    """
    lower_joins = join(environment, i1.lower_bound, i2.lower_bound)
    upper_meets = meet(environment, i1.upper_bound, i2.upper_bound)

    result = set()
    for lower in lower_joins:
        for upper in upper_meets:
            if is_subtype(environment, lower, upper):
                result.add(EvidenceInterval(lower, upper))
    return result


def meet_precision_specification(
    environment: Environment,
    spec1: EvidenceSpecification,
    spec2: EvidenceSpecification,
) -> Set[EvidenceSpecification]:
    """Compute the precision meet of two specifications in the type system.

    :param environment: The Environment object representing the type system.
    :param spec1: The first specification to meet.
    :param spec2: The second specification to meet.
    :return: A set of EvidenceSpecifications that are the precision meet of the two
        specifications.
    """
    result = set()
    sigs1 = {sig.var: sig for sig in spec1.signatures}
    sigs2 = {sig.var: sig for sig in spec2.signatures}

    common_vars = sigs1.keys() & sigs2.keys()
    meets_by_var: Dict[str, Set[EvidenceSignature]] = {}

    for var in common_vars:
        sig1 = sigs1[var]
        sig2 = sigs2[var]
        intervals = meet_precision_interval(environment, sig1.interval, sig2.interval)
        meets_by_var[var] = {EvidenceSignature(var, interval) for interval in intervals}

    for combo in product(*meets_by_var.values()):
        result.add(EvidenceSpecification(set(combo)))

    return result


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
    :return: A set of pairs of EvidenceIntervals that are the interior of the two
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
    :return: A set of pairs of EvidenceSpecifications that represent the interior of the
        two specifications.
    """
    pairs = set()

    sigs1_by_var = {sig.var: sig for sig in spec_1.signatures}
    sigs2_by_var = {sig.var: sig for sig in spec_2.signatures}

    if not spec_2.signatures:
        return {(spec_1, EvidenceSpecification(set()))}

    common_vars = sigs1_by_var.keys() & sigs2_by_var.keys()

    interval_pairs_by_var = {}

    for var in common_vars:
        intv1 = sigs1_by_var[var].interval
        intv2 = sigs2_by_var[var].interval
        interval_pairs = interior_intervals(environment, intv1, intv2)

        if not interval_pairs:
            return set()

        interval_pairs_by_var[var] = interval_pairs

    from itertools import product

    for combo in product(*interval_pairs_by_var.values()):
        sigs1 = set()
        sigs2 = set()

        for var, (i1, i2) in zip(interval_pairs_by_var.keys(), combo):
            sigs1.add(EvidenceSignature(var, i1))
            sigs2.add(EvidenceSignature(var, i2))

        unmatched_vars = sigs1_by_var.keys() - common_vars
        for var in unmatched_vars:
            sigs1.add(sigs1_by_var[var])

        pairs.add((EvidenceSpecification(sigs1), EvidenceSpecification(sigs2)))

    return pairs


def interior_types(
    environment: Environment, ti: GradualType, tj: GradualType
) -> Optional[Tuple[EvidenceInterval, EvidenceInterval]]:
    """Compute the interior types of two gradual types in the type system.

    :param environment: The Environment object representing the type system.
    :param ti: The first gradual type.
    :param tj: The second gradual type.
    :return: A pair of EvidenceIntervals that represent the interior of the two types,
        or None if the types are not compatible.
    """
    match ti, tj:
        case GradualFunctionType(f1i, g2), GradualFunctionType(g3i, g4):
            domain_result = interior_types(environment, g3i, f1i)
            codomain_result = interior_types(environment, g2, g4)
            if domain_result is None or codomain_result is None:
                return None
            (d_left, d_right) = domain_result
            (c_left, c_right) = codomain_result
            left = EvidenceInterval(
                GradualFunctionType(d_right.upper, c_left.lower),
                GradualFunctionType(d_left.lower, c_left.upper),
            )
            right = EvidenceInterval(
                GradualFunctionType(d_right.lower, c_right.lower),
                GradualFunctionType(d_left.upper, c_right.upper),
            )
            return (left, right)
        case Type(), Type():
            if is_gradual_subtype(environment, ti, tj):
                left = lift_gradual_type(ti)
                right = EvidenceInterval(ti, tj)
                return (left, right)
            return None
        case Type(), Unknown():
            left = lift_gradual_type(ti)
            return (left, EvidenceInterval(ti, TopType()))
        case Unknown(), Type():
            right = lift_gradual_type(tj)
            return (EvidenceInterval(BottomType(), tj), right)
        case Unknown(), Unknown():
            spec = lift_gradual_type(Unknown())
            return (spec, spec)
        case GradualFunctionType(fi, fj), Unknown():
            unknown_fun = GradualFunctionType(Unknown(), Unknown())
            left = EvidenceInterval(GradualFunctionType(fi, fj), unknown_fun)
            right = lift_gradual_type(Unknown())
            return (left, right)
        case Unknown(), GradualFunctionType(fi, fj):
            unknown_fun = GradualFunctionType(Unknown(), Unknown())
            left = lift_gradual_type(Unknown())
            right = EvidenceInterval(unknown_fun, GradualFunctionType(fi, fj))
            return (left, right)
        case _:
            return None


def interior_class_specification(
    environment: Environment,
    spec_1: Specification,
    spec_2: Specification,
) -> Optional[CompleteEvidence]:
    """Compute the interior specifications of two specifications in the type system.

    :param environment: The Environment object representing the type system.
    :param spec_1: The first specification to compute the interior of.
    :param spec_2: The second specification to compute the interior of.
    :return: A CompleteEvidence that represents the interior of the two specifications,
             or None if the specifications are not compatible.
    """
    left_spec = set()
    right_spec = set()

    all_vars = set(spec_1.keys()).union(set(spec_2.keys()))

    for var in all_vars:
        sig1 = spec_1.get_signature(var)
        sig2 = spec_2.get_signature(var)

        t1 = sig1.type if sig1 else None
        t2 = sig2.type if sig2 else None

        if t1 is not None and t2 is not None:
            interiors = interior_types(environment, t1, t2)
            if interiors is None:
                return None

            i1, i2 = interiors

            if is_gradual_subtype(environment, t1, t2):
                left_spec.add(EvidenceSignature(var, i1))
                right_spec.add(EvidenceSignature(var, i2))
            elif is_gradual_subtype(environment, t2, t1):
                left_spec.add(EvidenceSignature(var, i2))
                right_spec.add(EvidenceSignature(var, i1))
            else:
                return None

        elif t1 is not None:
            left_spec.add(EvidenceSignature(var, lift_gradual_type(t1)))

        elif t2 is not None:
            right_spec.add(EvidenceSignature(var, lift_gradual_type(t2)))

    return CompleteEvidence(
        {
            Evidence(
                EvidenceSpecification(left_spec),
                EvidenceSpecification(right_spec),
            )
        }
    )


""" Transitivity functions
"""


def transitivity_interval(
    environment: Environment,
    par_interval_1: EvidenceSignature,
    par_interval_2: EvidenceSignature,
) -> Set[EvidenceSignature]:
    """Compute the transitivity of two pairs of intervals in the type system.

    :param environment: The Environment object representing the type system.
    :param par_interval_1: EvidenceSignature representing.
    :param par_interval_2: EvidenceSignature representing.
    :return: Set of EvidenceSignatures representing transitivity intervals.
    """
    result = set()

    middle_intervals = meet_precision_interval(
        environment, par_interval_1.interval, par_interval_2.interval
    )

    for im in middle_intervals:
        left_pairs = interior_intervals(environment, par_interval_1.interval, im)
        right_pairs = interior_intervals(environment, im, par_interval_2.interval)

        for left_low, _ in left_pairs:
            for right_low, right_high in right_pairs:
                combined_interval = EvidenceInterval(
                    left_low.lower_bound, right_high.upper_bound
                )
                result.add(EvidenceSignature(par_interval_1.var, combined_interval))

    return result


def transitivity_specifications(
    environment: Environment,
    par_spec_1: Evidence,
    par_spec_2: Evidence,
) -> Set[Evidence]:
    """Compute the transitivity of two specifications in the type system.

    :param environment: The Environment object representing the type system.
    :param par_spec_1: Evidence representing.
    :param par_spec_2: Evidence representing.
    :return: Set of Evidence representing the transitivity.
    """
    result = set()

    middle_specs = meet_precision_specification(
        environment, par_spec_1.specification_2, par_spec_2.specification_1
    )

    for sm in middle_specs:
        left_interior_pairs = interior_gradual_specification(
            environment, par_spec_1.specification_1, sm
        )
        right_interior_pairs = interior_gradual_specification(
            environment, sm, par_spec_2.specification_2
        )

        for left_spec, _ in left_interior_pairs:
            for _, right_spec in right_interior_pairs:
                combined = Evidence(left_spec, right_spec)
                result.add(combined)
    return result


def transitivity_complete_evidences(
    environment: Environment,
    complete_evidence_1: CompleteEvidence,
    complete_evidence_2: CompleteEvidence,
) -> Optional[CompleteEvidence]:
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
            new_evidences = transitivity_specifications(environment, ev1, ev2)
            results.update(new_evidences)

    if not results:
        return None
    return CompleteEvidence(results)
