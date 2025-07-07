from ..definitions import Environment
from ..subtyping import is_gradual_subtype
from .definitions import EvidenceInterval, EvidenceSpecification


def is_subtype_interval(
    environment: Environment, interval_1: EvidenceInterval, interval_2: EvidenceInterval
) -> bool:
    """Check if the first evidence interval is a subtype of the second evidence
        interval.

    :param environment: The Environment object representing the type system.
    :param interval_1: The first evidence interval to check.
    :param interval_2: The second evidence interval to check.
    :return: True if interval_1 is a subtype of interval_2, False otherwise.
    """
    return is_gradual_subtype(
        environment, interval_1.lower_bound, interval_2.lower_bound
    ) and is_gradual_subtype(
        environment, interval_1.upper_bound, interval_2.upper_bound
    )


def is_subtype_evidence_spec(
    environment: Environment,
    evidence_1: EvidenceSpecification,
    evidence_2: EvidenceSpecification,
) -> bool:
    """Check if the first evidence specification is a subtype of the second evidence
        specification.

    :param environment: The Environment object representing the type system.
    :param evidence_1: The first evidence specification to check.
    :param evidence_2: The second evidence specification to check.
    :return: True if evidence_1 is a subtype of evidence_2, False otherwise.
    """
    for sig2 in evidence_2.signatures:
        matching_sig1 = next(
            (sig1 for sig1 in evidence_1.signatures if sig1.var == sig2.var), None
        )
        if matching_sig1 is None:
            return False
        result = is_subtype_interval(environment, matching_sig1.interval, sig2.interval)
        if not result:
            return False
    return True
