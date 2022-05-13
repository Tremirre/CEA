import typing
import copy

import core.hypothesis
import core.instance
import core.types


def eliminate_entailed_general_hypotheses(hypotheses: set[core.hypothesis.Hypothesis]):
    result = copy.copy(hypotheses)
    for hypothesis in hypotheses:
        for contr_hypothesis in hypotheses:
            if hypothesis is contr_hypothesis:
                continue
            if hypothesis.is_more_general_then(contr_hypothesis):
                result.remove(contr_hypothesis)
    return result


def find_s(
        labeled_instances: typing.Iterable[core.instance.Instance],
        domain: dict[core.types.attribute, set[core.types.value]]
) -> core.hypothesis.Hypothesis:
    hypothesis = core.hypothesis.Hypothesis(domain.keys(), strict_initialization=True)
    for instance in labeled_instances:
        if instance.label is not core.types.Label.POSITIVE:
            continue
        hypothesis = core.hypothesis.get_minimally_generalized_hypothesis(hypothesis, instance)
    return hypothesis


def list_then_eliminate(
        labeled_instances: typing.Iterable[core.instance.Instance],
        domain: dict[core.types.attribute, set[core.types.value]]
) -> set[core.hypothesis.Hypothesis]:
    valid_hypothesis = core.hypothesis.generate_all_hypotheses(domain)
    for instance in labeled_instances:
        accept_instance = instance.label is core.types.Label.POSITIVE
        valid_hypothesis = {
            hypothesis for hypothesis in valid_hypothesis if hypothesis.is_consistent(instance, accept_instance)
        }
    return valid_hypothesis


def candidate_elimination(
        labeled_instances: typing.Iterable[core.instance.Instance],
        domain: dict[core.types.attribute, set[core.types.value]]
) -> tuple[set[core.hypothesis.Hypothesis], core.hypothesis.Hypothesis]:
    general_boundary = {core.hypothesis.Hypothesis(domain.keys(), strict_initialization=False)}
    specific_boundary = core.hypothesis.Hypothesis(domain.keys(), strict_initialization=True)
    for instance in labeled_instances:
        if instance.label is core.types.Label.POSITIVE:
            general_boundary = {
                hypothesis for hypothesis in general_boundary if hypothesis.is_consistent(instance, should_accept=True)
            }
            specific_boundary = core.hypothesis.get_minimally_generalized_hypothesis(specific_boundary, instance)
            is_generalized = False
            for general_hypothesis in general_boundary:
                if general_hypothesis.is_more_general_then(specific_boundary):
                    is_generalized = True
                    # break
            if not is_generalized:
                raise Exception("Training set inconsistency detected!")
        else:
            if specific_boundary.does_accept_instance(instance):
                raise Exception("Training set inconsistency detected!")
            new_general_boundary = set()
            for general_hypothesis in general_boundary:
                minimal_specification = core.hypothesis.get_stricter_consistent_hypotheses(
                    general_hypothesis,
                    instance,
                    domain
                )
                minimal_specification = {
                    hypothesis for hypothesis in minimal_specification if
                    hypothesis.is_more_general_then(specific_boundary)
                }
                new_general_boundary.update(minimal_specification)
            general_boundary = eliminate_entailed_general_hypotheses(new_general_boundary)
    return general_boundary, specific_boundary
