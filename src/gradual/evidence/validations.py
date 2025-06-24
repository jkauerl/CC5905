from ..definitions import Environment
from ..subtyping import is_subtype
from .definitions import EvidenceSignature


def is_subtype_evidence(
    environment: Environment,
    evidence_1: EvidenceSignature,
    evidence_2: EvidenceSignature,
) -> bool:
    """Check if the first evidence is a subtype of the second evidence.

    :param environment: The Environment object representing the type system.
    :param evidence_1: The first evidence to check.
    :param evidence_2: The second evidence to check.
    :return: True if evidence_1 is a subtype of evidence_2, False otherwise.
    """
    if is_subtype(
        environment, evidence_1.interval.lower_bound, evidence_2.interval.lower_bound
    ):
        if is_subtype(
            environment,
            evidence_1.interval.upper_bound,
            evidence_2.interval.upper_bound,
        ):
            return evidence_1.var == evidence_2.var
        return True
    return False
