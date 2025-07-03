from ..definitions import Environment
from ..subtyping import is_subtype
from .definitions import EvidenceInterval, EvidenceSpecification


def is_subtype_interval(environment: Environment, interval_1: EvidenceInterval, interval_2: EvidenceInterval) -> bool:
    """Check if the first evidence interval is a subtype of the second evidence interval.
    
    :param environment: The Environment object representing the type system.
    :param interval_1: The first evidence interval to check.
    :param interval_2: The second evidence interval to check.
    :return: True if interval_1 is a subtype of interval_2, False otherwise.
    """
    return (is_subtype(environment, interval_1.lower_bound, interval_2.lower_bound) and
            is_subtype(environment, interval_1.upper_bound, interval_2.upper_bound))


def is_subtype_evidence_spec(environment: Environment, evidence_1: EvidenceSpecification, evidence_2: EvidenceSpecification) -> bool:
    """Check if the first evidence specification is a subtype of the second evidence specification.
    
    :param environment: The Environment object representing the type system.
    :param evidence_1: The first evidence specification to check.
    :param evidence_2: The second evidence specification to check.
    :return: True if evidence_1 is a subtype of evidence_2, False otherwise.
    """
    spec1_dict = {sig.var: sig.interval for sig in evidence_1.signatures}
    spec2_dict = {sig.var: sig.interval for sig in evidence_2.signatures}

    for var, interval2 in spec2_dict.items():
        if var not in spec1_dict:
            return False
        if not is_subtype_interval(environment, spec1_dict[var], interval2):
            return False
    return True
